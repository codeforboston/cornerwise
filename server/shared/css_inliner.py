"""

Make it possible to write emails using Django templates. There are a few steps
involved:

1. Parse the Django template into nodes
2. Interpret ExtendsNodes and IncludeNodes
3. Return a new Django template as a string
4. Generate an lxml tree from the resulting template
5. Replace <link rel="stylesheet"> nodes with <style> tags
6. Run toronado's CSS inliner on the resulting tree
7. Output the final Django template


- Replace the implementation of all nodes other than ExtendsNodes and
  IncludeNodes to return themselves?
- Is there an API function to do (3), or does that need to be done manually?
"""

import os
from pathlib import PurePath
import re
from urllib import parse
from urllib.request import urlopen

import django.template.base as template_base
import django.template.utils as template_utils
import lxml.html
from django.template.base import Lexer, Parser, Template
from lxml.cssselect import CSSSelector
from lxml.html.builder import STYLE

import toronado


remap_urls = {"/static": "/static"}

def remap_url(src, remap):
    """
    If src is in a subdirectory of any of the keys in `remap`, rewrite the path
    to point to a local file relative to the corresponding value.
    """
    path = PurePath(src)
    for url_path, file_path in remap.items():
        print(url_path, file_path)
        try:
            rel_path = path.relative_to(url_path)
            return PurePath(file_path).joinpath(rel_path)
        except ValueError:
            continue


def resolve_link_src(src, remap=remap_urls):
    pieces = parse.urlsplit(src)
    if pieces.netloc:
        return urlopen(src).read()

    file_path = remap_url(src, remap)
    if file_path:
        with open(file_path) as src_file:
            return src_file.read()


def parsed_to_template_string(parsed):
    pass


def expand_includes(nodelist):
    pass


def links_to_style(tree, rewrite_src=None):
    """
    Replace all stylesheet links in the parsed document tree `tree` with
    <script> tags containing the contents of the URL.
    """
    if not rewrite_src:
        rewrite_src = lambda x: x

    for link in CSSSelector("link[rel=stylesheet]")(tree):
        src = rewrite_src(link.attrib["href"])
        pieces = parse.urlsplit(src)
        if pieces.netloc:
            style_body = urlopen(src).read()
        else:
            with open(src) as local_styles:
                style_body = local_styles.read()
        style = STYLE(style_body.replace("\n", ""))
        link.replace(style)

    return tree


def rebuild_template(template_str):
    nodes = Template(template_str).compile_nodelist()
    expanded = expand_includes(nodes)
    tree = lxml.html.fromstring(nodelist_to_template(expanded))
    links_to_style(tree)
    toronado.inline(tree)

    return lxml.html.tostring(tree)

# body = urlopen("http://localhost:4000").read()
# tree = lxml.html.fromstring(body)


