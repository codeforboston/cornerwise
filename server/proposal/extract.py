from collections import OrderedDict
import os
import re

from .models import Document, Proposal, Attribute

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
            if current_p:
                ps.append(current_p.join(" "))
            current_p = []
        else:
            current_p.append(line.strip())

    return ps

def make_matcher(patt, group=None, value=None):
    assert group or value, "Matcher must have a group or value"

    if isinstance(patt, str):
        patt = re.compile(patt)

    def matcher(line):
        m = patt.match(line)

        if m:
            return m.group(group) if group else value

        return None

    return matcher

section_matchers = [
    make_matcher(r"PLANNING STAFF REPORT",
                 value="Planning Staff Report"),
    make_matcher(r"[IVX]+\. ([^a-z]+)(\n|$)", group=1)
]


def make_sections(lines, matchers=section_matchers):
    found = OrderedDict()
    section_name = "Header"
    section = []

    for line in lines:
        line = line.strip()
        new_section_name = None

        for matcher in matchers:
            name = matcher(line)
            if name:
                new_section_name = name
                break

        if new_section_name:
            found[section_name] = section
            section_name = new_section_name
            section = []
        else:
            section.append(line)


    return found


def staff_reports(docs_manager=Document.objects):
    return docs_manager.filter(field="reports")\
                       .filter(title__icontains="staff report")

def document_lines(doc):
    with open(doc.fulltext.path) as txt:
        return txt.readlines()

def staff_report_properties(doc):
    """Extract a dictionary of properties from the plaintext contents of a
    Planning Staff Report.
    """
    lines = document_lines(doc)
    sections = make_sections(lines)

    props = {}

    props.update(properties(sections["Header"]))
    props.update(properties(sections["Planning Staff Report"]))

    return props

def get_properties(doc):
    # TODO: Dispatch on the document's 'field' (or title?)
    return staff_report_properties(doc)
