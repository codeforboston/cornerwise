#!/bin/bash

apt-get install -y npm node
npm install -g requirejs
npm install -g cssnano-cli

export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
pip3 install -r /support/requirements.txt

/support/build_js.sh

# http://stackoverflow.com/questions/9283472/command-to-remove-all-npm-modules-globally:
npm ls -gp --depth=0 | awk -F/ '/node_modules/ && !/\/npm$/ {print $NF}' | xargs npm -g rm

apt-get remove -y npm
