#!/bin/sh

function setup_environment {
    # TODO: Only set the variables if they're not already set
    echo "Configuring environment"
    export DOCKER_HOST="tcp://$(boot2docker ip):2376"
    export DOCKER_CERT_PATH=$HOME/.boot2docker/certs/boot2docker-vm
    export DOCKER_TLS_VERIFY=1
}

# Using Boot2Docker?
which boot2docker >/dev/null
NO_B2D=$?

CITYDASH_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

if [ $NO_B2D -eq 0 ]; then
    # Is it up?
    if [ $(boot2docker status) != "running" ] ; then
        echo "Starting up Boot2Docker."
        boot2docker up;
    fi;

    setup_environment
fi;

IMAGE_CREATED=$(docker inspect citydash | grep "Created" | perl -n -e'/"Created": "(.*)"/ && print $1')
SHOULD_BUILD=1

if [ $? -eq 0 ]; then
    echo "Found existing citydash image (created: $IMAGE_CREATED)"
    SHOULD_BUILD=0
    # Convert to a timestamp

    # TODO: Check if any of the build dependencies are newer than the
    # existing image.

    # CREATED_STAMP=date -j -f "YYYY-mm-" "$IMAGE_CREATED" "+$s"
fi;

if [ $SHOULD_BUILD -eq 1 ]; then
    echo "Building citydash image."
    docker build -t citydash $CITYDASH_DIR
fi;

# TODO: Command line option for forcing creation of a new container
# Determine if the container is already running:
CONTAINER_ID=$(docker ps | awk '/citydash/ { if (match($2, /^citydash/)) print $1 }')

if [ $CONTAINER_ID ]; then
    # Found a container. Attach to it:
    echo "Attaching to running container with id: $CONTAINER_ID"
    docker exec -it $CONTAINER_ID /bin/bash
else
    echo "Starting container..."
    docker run -it -v $CITYDASH_DIR/server:/app -p "3000:3000" citydash /bin/bash
fi;

if [ $? -eq 1 ]; then
    echo "Failed to start the container. Is it already running?"
fi;
