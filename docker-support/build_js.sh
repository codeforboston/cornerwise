#!/usr/bin/env bash

script_dir=$(dirname "$BASH_SOURCE")
cd $(dirname "$BASH_SOURCE")

client_dir=${CLIENT_DIR:-"$script_dir/../client"}
output_dir=${OUTPUT_DIR:-"$client_dir"}
js_output_dir=${JS_OUTPUT_DIR:-"$output_dir/build"}
css_output_dir=${CSS_OUTPUT_DIR:-"$output_dir/css"}

if ! which r.js; then
    echo "Please install require.js (npm install -g requirejs) and rerun the script." && exit 1
fi

if ! which postcss; then
    echo "Please install postcss (npm install -g cssnano postcss) and rerun the script." && exit 1
fi

file_hash() {
    python << EOF | cut -b -15
from hashlib import sha1
with open("$1") as infile:
    print(sha1(infile.read()).hexdigest())
EOF
}

echo "Assembling templates."
python3 $script_dir/build_templates.py || exit 1

echo "Minifying JS."
r.js -o $client_dir/app.build.js || exit 1

mkdir -p "$js_output_dir"
app_js="$js_output_dir/app.js"
mv "$client_dir/dist/main.js" "$app_js"
cp "$client_dir/scripts/require.js" "$js_output_dir/require.js"

js_hash=$(file_hash "$app_js")
app_js_hash="$js_output_dir/app.${js_hash}.js"
cp "$app_js" "$app_js_hash"

rm -r $client_dir/dist/

echo "Minifying CSS"
app_sha="$css_output_dir/app.build.css"
postcss "$client_dir/css/app.css" --config /config/postcss.config.js --output "$app_css"

css_hash=$(file_hash "$app_css")
app_css_hash="$css_output_dir/app.${css_hash}.css"
cp "$app_css" "$app_css_hash"

echo j
echo "New JavaScript build: $app_js_hash"
echo "New CSS build: $app_css_hash"

cd -
