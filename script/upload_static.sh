#!/bin/bash

cd $(dirname "$BASH_SOURCE")

bash ../docker-support/build_js.sh
rsync -az -e 'docker-machine ssh cornerwise' --progress ../client :cornerwise/client

cd -
