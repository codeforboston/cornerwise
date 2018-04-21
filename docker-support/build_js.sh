#!/bin/sh

set -e

if [ -n "$BASH_SOURCE" ]; then
    script_dir=$(dirname "$BASH_SOURCE")
    cd $(dirname "$BASH_SOURCE")
else
    script_dir="$PWD"
fi

python_bin=$(which python3 || echo "python")

client_dir=${CLIENT_DIR:-"$script_dir/../client"}
if [ -n "$OUTPUT_DIR" ]; then
    js_output_dir="$OUTPUT_DIR"
    css_output_dir="$OUTPUT_DIR"
    json_output_file="$OUTPUT_DIR/built.json"
else
    js_output_dir="$client_dir/build"
    css_output_dir="$client_dir/build"
    json_output_file="$client_dir/built.json"
fi

if ! which r.js; then
    echo "Please install require.js (npm install -g requirejs) and rerun the script." && exit 1
fi

if ! which postcss; then
    echo "Please install postcss (npm install -g cssnano postcss) and rerun the script." && exit 1
fi

file_hash() {
    $python_bin << EOF | cut -b -15
from hashlib import sha1
with open("$1") as infile:
    print(sha1(infile.read().encode("utf8")).hexdigest())
EOF
}

echo "Assembling templates."
$python_bin $script_dir/build_templates.py || exit 1

echo "Minifying JS."
r.js -o $client_dir/app.build.js || exit 1

mkdir -p "$js_output_dir"
app_js="$js_output_dir/app.js"
mv "$client_dir/app.js" "$app_js"

js_hash=$(file_hash "$app_js")
app_js_hash="$js_output_dir/app.${js_hash}.js"
cp "$app_js" "$app_js_hash"

rm -r $client_dir/dist/

echo "Minifying CSS"
app_css="$css_output_dir/app.build.css"
cat "$client_dir/css/_imports.css" "$client_dir/css/app.css" | postcss --config /config/postcss.config.js --output "$app_css"

css_hash=$(file_hash "$app_css")
app_css_hash="$css_output_dir/app.${css_hash}.css"
cp "$app_css" "$app_css_hash"

echo "New JavaScript build: $app_js_hash"
echo "New CSS build: $app_css_hash"

echo '{"js_filename": "app.'$js_hash'.js", "css_filename": "app.'$css_hash'.css"}' > $json_output_file

cd -
