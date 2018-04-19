#!/usr/bin/env python3
"""
Script to generate a 'templates' module containing all the client-side
templates.
"""
import json
import os
from pathlib import PurePosixPath
import re

path = os.path

def file_contents(f):
    return "".join(line.strip() for line in f)


# TODO Rewrite this to remove the dependency on Python 3-only 'pathlib', so
# that we don't need py3 in the JS build image.
def collect_files(template_dir, url_base):
    basepath = PurePosixPath(template_dir)
    baseurl = PurePosixPath(url_base)

    for dirname, _, files in os.walk(template_dir):
        rel_dirname = PurePosixPath(dirname).relative_to(template_dir)
        for filename in files:
            template_path = path.join(dirname, filename)
            url = baseurl.joinpath(rel_dirname, filename)
            with open(template_path, "r", encoding="utf8") as f:
                yield str(url), file_contents(f)


def make_file_dict(gen):
    return {url: contents for url, contents in gen}


def templates_file(file_dict):
    return (
        "define([], function() { return " + json.dumps(file_dict) + "; });")


def do_main():
    file_dir = path.dirname(__file__)
    client_dir = os.environ.get("CLIENT_DIR", path.join(file_dir, "../client"))
    template_dir = path.join(client_dir, "template")
    url_base = "/static/template"
    out_dir = path.join(client_dir, "scripts/src/build/")

    template_dir = os.environ.get("JS_TEMPLATES_DIR", template_dir)
    out_dir = os.environ.get("JS_TEMPLATES_BUILD_DIR", out_dir)

    os.makedirs(out_dir, exist_ok=True)

    with open(path.join(out_dir, "templates.js"), "w") as outfile:
        outfile.write(
            templates_file(
                make_file_dict(collect_files(template_dir, url_base))))


if __name__ == "__main__":
    do_main()
