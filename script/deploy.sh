#!/bin/bash

# Builds a new application image and pushes it to Docker Hub. Restarts the
# application on the Docker Machine 'cornerwise', which you must set up
# separately. Rebuilds the CSS and JavaScript and pushes it to the host. Assumes
# that static assets are served from ~/cornerwise/client on the configured
# machine.

DOCKER_HUB_REPO=${DOCKER_HUB_REPO:-bdsand}

cd $(dirname "$BASH_SOURCE")

docker build .. -t $DOCKER_HUB_REPO/cornerwise:latest
docker login
docker push $DOCKER_HUB_REPO/cornerwise:latest

eval $(docker-machine env cornerwise)
docker-compose -f ../docker-compose.prod.yml restart -d

bash ../docker-support/build_js.sh
rsync -azP -e 'docker-machine ssh cornerwise' ../client :cornerwise/client

cd -
