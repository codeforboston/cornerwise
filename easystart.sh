#!/bin/bash
HOST_PORT=3000
CITYDASH_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
yes_pattern='^[yY]'

function find_vm_name {
    echo $(docker-machine ls | awk '/virtualbox/ { print $1 }' | head -n 1)
}

function setup_environment {
    eval $(docker-machine env $1)
}

function open_browser {
    if ( which xdg-open >/dev/null ); then
        xdg-open $1
    elif ( which open >/dev/null ); then
        open $1
    fi;
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
  -F      Prevents the script's default behavior of setting up the
          VM to forward traffic on the host port to localhost.
  -p <port> Run on a port other than 3000
  -r      Force Docker to run a new container, rather than
          attach to one that is already running
  -x      If a running container is found, stop it
"
}


SHOULD_BUILD=0
FORCE_RUN=0
VM_PORT_FORWARDING=1
IGNORE_CHANGES=0
AUTOSTART=0
STOP_RUNNING=0
skip_build_prompt=0

while getopts ":rbBFpshx" opt; do
    case $opt in
        b)
            SHOULD_BUILD=1
            skip_build_prompt=1
            ;;
        B)
            IGNORE_CHANGES=1
            skip_build_prompt=1
            ;;
        r)
            FORCE_RUN=1
            ;;
        s)
            AUTOSTART=1
            ;;
        F)
            VM_PORT_FORWARDING=0
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

if ((AUTOSTART)); then
    RUN_COMMAND="/bin/sh /app/start.sh \"$HOST_PORT\""
fi

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
    echo "Docker is not installed."
    if [ $(uname) == "Darwin" ]; then
        open_browser "https://www.docker.com/toolbox"
    else
        open_browser "http://docs.docker.com/installation/"
    fi

    exit 1
fi;

use_machine=0
# Using Docker-Machine?
if (which docker-machine >/dev/null); then
    use_machine=1

    vm_name=$(find_vm_name)

    if [ -z "$vm_name" ]; then
        vm_name=dev
        # Initialize, if necessary:
        docker-machine create -d virtualbox "$vm_name" >/dev/null
    fi

    if [ $(docker-machine status $vm_name) != "Running" ] ; then
        docker-machine start $vm_name
    fi;

    setup_environment $vm_name

    # Forward the VM port to localhost
    if ((VM_PORT_FORWARDING)); then
        VBoxManage controlvm $vm_name natpf1 delete django
        # Only using VirtualBox... for now
        VBoxManage controlvm $vm_name natpf1 "django,tcp,127.0.0.1,$HOST_PORT,,$HOST_PORT"
    fi;
elif [ $(uname) == "Darwin" ]; then
    # In case the user installed Docker separately

    # OS X
    echo "You're running OS X, so you should install Docker Machine."

    # Determine the latest version of Docker Toolbox
    release_tag=$(curl -s https://api.github.com/repos/docker/toolbox/releases/latest | grep "tag_name" | perl -n -e '/"tag_name": "v([^"]+)"/ && print $1')

    if [ -n "$release_tag" ]; then
        echo "Downloading latest version of Docker Toolbox ($release_tag)"
        open "https://github.com/docker/toolbox/releases/download/v$release_tag/DockerToolbox-$release_tag.pkg"
    else
        echo "Failed to determine the latest version of Docker Toolbox"
        open_browser "https://www.docker.com/toolbox"
    fi
    exit 1
fi

IMAGE_CREATED=$(docker inspect citydash | grep "Created" | perl -n -e'/"Created": "(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)\.\d+Z"/ && print $1')
NO_EXISTING=$?

if ((!IGNORE_CHANGES)); then
    # Determine if the image should be rebuilt.
    if ((!$SHOULD_BUILD)); then
        SHOULD_BUILD=1

        if [ -n "$IMAGE_CREATED" ]; then
            echo "Found existing citydash image (created: $IMAGE_CREATED)"
            SHOULD_BUILD=0

            if ((!skip_build_prompt)); then
                # Convert edit date to a timestamp
                CREATED_STAMP=$(date -j -f "%Y-%m-%dT%H:%M:%S" "$IMAGE_CREATED" "+%s")
                DOCKERFILE_MODIFIED=$(stat -f %m $CITYDASH_DIR/Dockerfile)
                changed_file=""

                if [ $DOCKERFILE_MODIFIED -gt $CREATED_STAMP ]; then
                    changed_file="Dockerfile"

                else
                    for path in $CITYDASH_DIR/docker-support/*; do
                        if [ $(stat -f %m $path) -gt $CREATED_STAMP ]; then
                            changed_file="$path"

                            break
                        fi
                    done
                fi

                if [ -n "$changed_file" ]; then
                    echo "$changed_file has changed since the image was created."

                    echo "Rebuild citydash image? (y/N)"
                    read -t 10 response
                    if ((response)); then
                        # Request timed out
                        SHOULD_BUILD=0
                    else
                        if [[ "$response" =~ $yes_pattern ]]; then
                            SHOULD_BUILD=1
                        else
                            SHOULD_BUILD=0
                        fi

                    fi
                fi
            fi
        fi
    fi
fi

if ((SHOULD_BUILD)); then
    echo "Building citydash image. This may take a few moments."
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
    docker run -it -v $CITYDASH_DIR/server:/app -v $CITYDASH_DIR/client:/client -v $CITYDASH_DIR/data:/data -v $CITYDASH_DIR/docker-runtime/bashrc:/root/.bashrc -p "$HOST_PORT:3000" citydash $RUN_COMMAND
fi;

if [ $? -eq 1 ]; then
    # TODO: Is it possible to distinguish between a failure to start the
    # container and a timeout? Both apparently return exit code 1.
    echo "Exited abnormally."
    exit 1
fi;


if ((AUTOSTART)); then
    # Do a busy wait for the Django server to start up
    wait_count=0
    is_running=1
    if ((use_machine)); then
        HOSTNAME=$(docker-machine ip "$vm_name")
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

        if ((VM_PORT_FORWARDING || !use_machine)); then
            open_browser "http://localhost:$HOST_PORT"
        else
            open_browser "http://$HOSTNAME:$HOST_PORT"
        fi
    else
        echo "The Django server did not start within 30 seconds."
        exit 3
    fi
fi
