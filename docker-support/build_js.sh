#!/usr/bin/env bash

cd $(dirname "$BASH_SOURCE")

client_dir=${CLIENT_DIR:-"../client"}

if ! which r.js; then
    echo "Please install require.js (npm install -g requirejs) and rerun the script." && exit 1
fi

if ! which cssnano; then
    echo "Please install cssnano (npm install -g cssnano-cli) and rerun the script." && exit 1
fi

echo "Assembling templates."
python build_templates.py || exit 1

echo "Minifying JS."
r.js -o $client_dir/app.build.js || exit 1

mkdir -p $client_dir/build
mv $client_dir/dist/main.js $client_dir/build/app.js
cp $client_dir/scripts/require.js $client_dir/build/require.js
echo -e "\n/* Revision: $(git rev-parse HEAD) */" >> $client_dir/app.js
rm -r $client_dir/dist/

echo "Minifying CSS"
cssnano $client_dir/css/app.css $client_dir/css/app.build.css

cd -
