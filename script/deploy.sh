#!/usr/bin/env bash

if ! which r.js; then
    npm install -g requirejs || exit 1
fi

echo "Assembling templates."
./build_templates.py

r.js -o ../client/app.build.js || exit 1

mv ../client/dist/main.js ../client/app.js
rm -r ../client/dist/
