#!/usr/bin/env python3
"""
Script to generate a 'templates' module containing all the client-side
templates.
"""
import json
import os
from pathlib import PurePosixPath
import re


def file_contents(f):
    return "".join(line.strip() for line in f)


def collect_files(template_dir, url_base):
    basepath = PurePosixPath(template_dir)
    baseurl = PurePosixPath(url_base)

    for dirname, _, files in os.walk(template_dir):
        rel_dirname = PurePosixPath(dirname).relative_to(template_dir)
        for filename in files:
            path = os.path.join(dirname, filename)
            url = baseurl.joinpath(rel_dirname, filename)
            with open(path) as f:
                yield str(url), file_contents(f)


def make_file_dict(gen):
    return {url: contents for url, contents in gen}


def templates_file(file_dict):
    return (
        "define([], function() { return " + json.dumps(file_dict) + "; });")


def do_main():
    file_dir = os.path.dirname(__file__)
    template_dir = os.path.join(file_dir, "../client/template")
    url_base = "/static/template"
    out_dir = os.path.join(
        os.path.dirname(__file__), "../client/scripts/src/build/")

    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "templates.js"), "w") as outfile:
        outfile.write(
            templates_file(
                make_file_dict(collect_files(template_dir, url_base))))


if __name__ == "__main__":
    do_main()
