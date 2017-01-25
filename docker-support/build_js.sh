#!/usr/bin/env bash

cd $(dirname "$BASH_SOURCE")

if ! which r.js; then
    echo "Please install require.js (npm install -g requirejs) and rerun the script." && exit 1
fi

if ! which cssnano; then
    echo "Please install cssnano (npm install -g cssnano-cli) and rerun the script." && exit 1
fi

echo "Assembling templates."
python build_templates.py || exit 1

echo "Minifying JS."
r.js -o ../client/app.build.js || exit 1

mv ../client/dist/main.js ../client/app.js
rm -r ../client/dist/

echo "Minifying CSS"
cssnano ../client/app.css ../client/app.build.css

cd -
