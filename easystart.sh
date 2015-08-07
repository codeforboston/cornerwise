#!/bin/sh
HOST_PORT=3000
CITYDASH_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

function setup_environment {
    eval $(boot2docker shellinit)
}

function open_browser {
    if ( which xdg-open >/dev/null ); then
        xdg-open $1
    elif ( which open >/dev/null ); then
        open $1
    fi;
}

function report_changes {
    echo "$1 has changed since the image was created."
    echo "Rerun ${BASH_SOURCE[0]} with -b flag to rebuild, -B to ignore changes"
    exit 2
}

function print_help {
    echo "
Usage: ${BASH_SOURCE[0]} [options] [command]

Quickly build and launch the CityDash container. If a command is
specified, run that command in the container and exit.

Options:
  -b      Force Docker to build a new image, even if one exists
  -B      Ignore changes to dependencies when determining whether
          to build a new image. Only build if there is no
          existing image
  -f      Set up the Boot2Docker VM to forward the Django port to
          localhost.
  -p <port> Run on a port other than 3000
  -r      Force Docker to run a new container, rather than
          attach to one that is already running
  -s      Create a container and run the CityDash start script
  -x      If a running container is found, stop it
"
}

SHOULD_BUILD=0
FORCE_RUN=0
VM_PORT_FORWARDING=0
IGNORE_CHANGES=0
AUTOSTART=0
STOP_RUNNING=0

while getopts ":rbBfpshx" opt; do
    case $opt in
        b)
            SHOULD_BUILD=1
            ;;
        B)
            IGNORE_CHANGES=1
            ;;
        r)
            FORCE_RUN=1
            ;;
        s)
            AUTOSTART=1
            RUN_COMMAND="/bin/sh /app/start.sh"
            ;;
        f)
            VM_PORT_FORWARDING=1
            ;;
        p)
            check_re='^[0-9]{4,}$'
            if ! [[ $OPTARG =~ $check_re ]]; then
                echo "Port must be an integer >=1000."
                exit 1
            fi
            HOST_PORT=$OPTARG
            ;;
        x)
            STOP_RUNNING=1
            ;;
        h)
            print_help
            exit 1
            ;;

        \?)
            echo "Unrecognized flag: -$OPTARG" >&2
            exit 1
            ;;
    esac
done

shift $((OPTIND-1))

if [ -z "$RUN_COMMAND" ]; then
    if [ -n "$1" ]; then
        RUN_COMMAND="$*"
    else
        RUN_COMMAND=/bin/bash
    fi
fi

if (! (which docker >/dev/null)); then
    # Docker is not installed
    open_browser "http://docs.docker.com/installation/"

    exit 1
fi;

# Using Boot2Docker?
if (which boot2docker >/dev/null); then
    USE_B2D=1

    # Download the ISO, if necesary:
    boot2docker init >/dev/null

    # Is it up?
    if [ $(boot2docker status) != "running" ] ; then
        echo "Starting up Boot2Docker."
        boot2docker up;
    fi;

    setup_environment

    # Forward the VM port to localhost
    if ((VM_PORT_FORWARDING)); then
        VBoxManage controlvm boot2docker-vm natpf1 "django,tcp,127.0.0.1,$HOST_PORT,,$HOST_PORT"
    fi;
else
    if [ $(uname) == "Darwin" ]; then
        # OS X
        echo "You're running OS X, so you should install Boot2Docker."
        open_browser "http://boot2docker.io"

        exit 1
    fi
    USE_B2D=0
fi;

IMAGE_CREATED=$(docker inspect citydash | grep "Created" | perl -n -e'/"Created": "(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)\.\d+Z"/ && print $1')

if ((!IGNORE_CHANGES)); then
    # Determine if the image should be rebuilt.
    if ((!$SHOULD_BUILD)); then
        SHOULD_BUILD=1

        if [ $? -eq 0 ]; then
            echo "Found existing citydash image (created: $IMAGE_CREATED)"
            SHOULD_BUILD=0

            # Convert edit date to a timestamp
            CREATED_STAMP=$(date -j -f "%Y-%m-%dT%H:%M:%S" "$IMAGE_CREATED" "+%s")
            DOCKERFILE_MODIFIED=$(stat -f %m $CITYDASH_DIR/Dockerfile)

            if [ $DOCKERFILE_MODIFIED -gt $CREATED_STAMP ]; then
                report_changes "Dockerfile"
                SHOULD_BUILD=1
            else
                for path in $CITYDASH_DIR/docker-support/*; do
                    if [ $(stat -f %m $path) -gt $CREATED_STAMP ]; then
                        report_changes $path
                        SHOULD_BUILD=1
                        break
                    fi
                done
            fi
        fi
    fi
fi

if ((SHOULD_BUILD)); then
    echo "Building citydash image."
    docker build -t citydash $CITYDASH_DIR
fi;

if ((!FORCE_RUN || STOP_RUNNING)); then
    # Determine if the container is already running:
    CONTAINER_ID=$(docker ps | awk '/citydash/ { if (match($2, /^citydash/)) print $1 }')
else
    CONTAINER_ID=""
fi;

if [ -n $CONTAINER_ID ] && ((STOP_RUNNING)); then
    echo "Stopping container: $CONTAINER_ID"
    docker stop $CONTAINER_ID
    CONTAINER_ID=""
fi

if [ -n "$CONTAINER_ID" ]; then
    # Found a container. Attach to it:
    echo "Attaching to running container with id: $CONTAINER_ID"
    docker exec -it $CONTAINER_ID $RUN_COMMAND
else
    echo "Starting container..."
    docker run -it -v $CITYDASH_DIR/server:/app -v $CITYDASH_DIR/client:/client -v $CITYDASH_DIR/data:/data -p "$HOST_PORT:3000" citydash $RUN_COMMAND
fi;

if [ $? -eq 1 ]; then
    echo "Failed to start the container."
    exit 1
fi;


if ((AUTOSTART)); then
    # Do a busy wait for the Django server to start up
    wait_count=0
    is_running=1
    if ((USE_B2D)); then
        HOSTNAME=$(boot2docker ip)
    else
        HOSTNAME="localhost"
    fi
    # Wait for the port to open
    until (lsof -i @$HOSTNAME:$HOST_PORT >/dev/null); do
        ((wait_count++))

        if ((wait_count > 30)); then
            is_running=0
            break
        fi

        sleep 1
    done

    if ((is_running)); then
        echo "Django started successfully on port $HOST_PORT."

        if ((VM_PORT_FORWARDING || !USE_B2D)); then
            open_browser "http://localhost:$HOST_PORT"
        else
            open_browser "http://$HOSTNAME:$HOST_PORT"
        fi
    else
        echo "The Django server did not start within 30 seconds."
        exit 3
    fi
fi
