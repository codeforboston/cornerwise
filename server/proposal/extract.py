from collections import OrderedDict
import os
import re

from .models import Document, Proposal, Attribute

def properties(lines):
    property_pattern = re.compile(r"^([a-z]+(\s+[a-z]+)?): (.*)(\n|$)", re.I)
    properties = {}

    for line in lines:
        m = property_pattern.match(line)

        if m:
            properties[m.group(1)] = m.group(3)

    return properties

def paragraphize(lines):
    empty_line = re.compile(r"\s*\n$")
    ps = []
    current_p = []

    for line in lines:
        if empty_line.match(line):
            if current_p:
                ps.append(current_p)
            current_p = []
        else:
            current_p.append(line.strip())

    return ps


def make_sections(lines):
    staff_report_pattern = re.compile(r"PLANNING STAFF REPORT")
    section_pattern = re.compile(r"[IVX]+\. ([^a-z]+)(\n|$)")

    found = OrderedDict()
    section_name = "Header"
    section = []

    for line in lines:
        line = line.strip()
        if staff_report_pattern.match(line):
            new_section_name = "Planning Staff Report"
        else:
            sp_match = section_pattern.match(line)

            if sp_match:
                new_section_name = sp_match.group(1)
            else:
                section.append(line)
                continue

        found[section_name] = section

        section_name = new_section_name
        section = []

    return found


def staff_reports(docs_manager=Document.objects):
    return docs_manager.filter(field="reports")\
                       .filter(title__icontains="staff report")

def document_lines(doc):
    txt_path = os.path.join("/client/media/doc", str(doc.pk), "text.txt")
    with open(txt_path) as txt_file:
        return txt_file.readlines()
