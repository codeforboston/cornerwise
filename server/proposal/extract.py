"""Functions for extracting document attributes from its plaintext
contents.
"""

from collections import OrderedDict
import os
import re


empty_line = re.compile(r"\s*\n$")

def properties(lines):
    property_pattern = re.compile(r"^([a-z]+(\s+[a-z]+)*): (.*)(\n|$)", re.I)
    properties = {}
    last_property = None

    for line in lines:
        m = property_pattern.match(line)

        if m:
            properties[m.group(1)] = m.group(3)
            last_property = m.group(1).strip()
        elif empty_line.match(line):
            last_property = None
        elif last_property:
            properties[last_property] += " " + line.strip()

    return properties

def paragraphize(lines):
    ps = []
    current_p = []

    for line in lines:
        if empty_line.match(line):
            ps.append(current_p)
            current_p = []
        else:
            current_p.append(line.strip())

    ps.append(current_p)

    return [" ".join(p) for p in ps if p]

def make_matcher(patt, group=None, value=None, fn=None):
    assert group or value, "Matcher must have a group or value"

    if isinstance(patt, str):
        patt = re.compile(patt)

    def matcher(line):
        m = patt.search(line)

        if m:
            v = m.group(group) if group else value

            return fn(v) if fn else v

        return None

    return matcher

def footer_matcher(line):
    if re.match(r"CITY HALL", line):
        def skip_lines(infile):
            next(infile)
            next(infile)
        return skip_lines



def generate_sections(lines, matchers):
    """

    :returns: A generator that produces 2-tuples containing each section
    name and its contents as a list of strings

    """
    section_name = "header"
    section = []

    for line in lines:
        line = line.strip()
        new_section_name = None

        for matcher in matchers:
            name = matcher(line)

            if callable(name):
                name = name(lines)

            if isinstance(name, str):
                new_section_name = name
                break

        if new_section_name:
            yield section_name, section
            section_name = new_section_name
            section = []
        else:
            section.append(line)

    yield section_name, section


def make_sections(lines, matchers):
    """Partition the contents of a file into sections using the given list
    of matches.

    :param lines: An iterator or generator that produces lines of text
    input

    :param matchers: A list of callables that, when called with a line
    of text, should return either None, a section name, or a callable.

    :returns: An OrderedDict mapping section names to section contents
    (a list of string)

    """
    found = OrderedDict()

    for section_name, section in generate_sections(lines, matchers):
        found[section_name] = section

    return found

def get_lines(doc):
    """Returns a generator that successively produces lines from the
    document."""
    enc = doc.encoding
    lines = (line.decode(enc) for line in doc.fulltext)

    return lines

staff_report_section_matchers = [
    footer_matcher,
    make_matcher(r"PLANNING STAFF REPORT",
                 value="Planning Staff Report"),
    make_matcher(r"^[IVX]+\. ([^a-z]+)(\n|$)", group=1),
]

def staff_report_properties(doc):
    """Extract a dictionary of properties from the plaintext contents of a
    Planning Staff Report.
    """
    lines = get_lines(doc)
    sections = make_sections(lines, staff_report_section_matchers)

    props = {}

    props.update(properties(sections["header"]))
    props.update(properties(sections["planning staff report"]))

    return props


decision_section_matchers = [
    footer_matcher,
    make_matcher(r"(ZBA DECISION|DESCRIPTION):?", group=1, fn=str.lower),
    make_matcher(r"DECISION:", value="decision")
]

def decision_properties(doc):
    """Extract a dictionary of properties from the contents of a Decision
    Document."""
    lines = get_lines(doc)
    sections = make_sections(lines, decision_section_matchers)

    props = {}
    props.update(properties(sections["zba decision"]))

    return sections

    #props.update(properties(sections[

def get_properties(doc):
    # TODO: Dispatch on the document's field and/or title
    # (doc.field is the name of the column in which the document was found)

    # Eventually, we'll want to introduce a pluggable property
    # extraction interface, so that other cities and formats can be
    # supported.

    if doc.field == "reports" and re.match(r"staff report", doc.title, re.I):
        return staff_report_properties(doc)
    elif re.match(r"decision", doc.title, re.I):
        return decision_properties(doc)
    else:
        return {}
