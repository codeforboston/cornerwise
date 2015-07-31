#!/bin/sh
RUN_COMMAND="/bin/bash"
POST_COMMAND=""
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

function print_help {
    echo "
Quickly build and launch the CityDash container.

Options:
  -b      Force Docker to build a new image, even if one exists
  -B      Ignore changes to dependencies when determining whether
          to build a new image
  -p      Set up the Boot2Docker VM to forward the Django port to
          localhost.
  -r      Force Docker to run a new container, rather than
          attach to one that is already running
  -s      Create a container and run the CityDash start script
"
}

SHOULD_BUILD=0
FORCE_RUN=0
VM_PORT_FORWARDING=0
IGNORE_CHANGES=0

while getopts ":rbBpsh" opt; do
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
            RUN_COMMAND="/bin/sh /app/start.sh"
            ;;
        p)
            VM_PORT_FORWARDING=1
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

if (! (which docker >/dev/null)); then
    # Docker is not installed
    open_browser "http://docs.docker.com/installation/"

    exit 1
fi;



# Using Boot2Docker?
if (which boot2docker >/dev/null); then
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
fi;

IMAGE_CREATED=$(docker inspect citydash | grep "Created" | perl -n -e'/"Created": "(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)\.\d+Z"/ && print $1')

# Determine if the image should be rebuilt.
if [ "$SHOULD_BUILD" -ne 1 ]; then
    SHOULD_BUILD=1

    if [ $? -eq 0 ]; then
        echo "Found existing citydash image (created: $IMAGE_CREATED)"
        SHOULD_BUILD=0

        # Convert edit date to a timestamp
        CREATED_STAMP=$(date -j -f "%Y-%m-%dT%H:%M:%S" "$IMAGE_CREATED" "+%s")
        DOCKERFILE_MODIFIED=$(stat -f %m $CITYDASH_DIR/Dockerfile)

        if [ $DOCKERFILE_MODIFIED -gt $CREATED_STAMP ]; then
            echo "Dockerfile has changed, so the image should be rebuilt."
            echo "Rerun as: ${BASH_SOURCE[0]} -b"
            exit 1
            SHOULD_BUILD=1
        else
            for path in $CITYDASH_DIR/docker-support/*; do
                if [ $(stat -f %m $path) -gt $CREATED_STAMP ]; then
                    echo "$path has changed, so the image should be rebuilt."
                    echo "Rerun as: ${BASH_SOURCE[0]} -b"
                    exit 1
                    SHOULD_BUILD=1
                    break
                fi
            done
        fi

    fi;
fi;

if [ "$SHOULD_BUILD" -eq 1 ]; then
    echo "Building citydash image."
    docker build -t citydash $CITYDASH_DIR
fi;

if [ $FORCE_RUN -ne 1 ]; then
    # Determine if the container is already running:
    CONTAINER_ID=$(docker ps | awk '/citydash/ { if (match($2, /^citydash/)) print $1 }')
else
    CONTAINER_ID=""
fi;

if [ $CONTAINER_ID ]; then
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



# Possible next steps:
