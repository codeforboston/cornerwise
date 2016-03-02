"""Functions for extracting document attributes from its plaintext
contents.
"""

from collections import OrderedDict
from datetime import datetime
from dateutil.parser import parse as date_parse
import pytz
from utils import pushback_iter
import re

empty_line = re.compile(r"\s*\n$")
property_pattern = re.compile(r"^([a-z]+(\s+[a-z]+)*): (.*)(\n|$)", re.I)


def properties(lines):
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


def make_matcher(patt, group=0, value=None, fn=None):
    if isinstance(patt, str):
        patt = re.compile(patt)

    def matcher(line):
        m = patt.search(line)

        if m:
            v = m.group(group) if group else value or m.group(0)

            return fn(v) if (fn and v) else v

        return None

    return matcher


def skip_match(patt, n=0):
    if isinstance(patt, str):
        patt = re.compile(patt)

    def skipper(line):
        if re.match(patt, line):
            def skip(inlines):
                for i in range(n):
                    next(inlines)
            return skip
    return skipper


def subsection_matcher(line):
    if re.match(r"^[0-9]+\.$", line):
        subsection_patt = re.compile(r"^([a-z]+(\s+[a-z]+)*):", re.I)

        def get_subsection_name(inlines):
            for line in inlines:
                m = subsection_patt.match(line)
                if m:
                    if isinstance(inlines, pushback_iter):
                        inlines.pushback(line[m.end():])
                    return m.group(1)
        return get_subsection_name


top_section_matcher = make_matcher(r"^([^a-z]{2,}):$", group=1,
                                   fn=str.lower)


def generate_sections(lines, matchers):
    """
    :param lines: An iterable of strings
    :param matchers: An iterable of functions

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
            if section:
                yield section_name, section
            section_name = new_section_name
            section = []
        else:
            section.append(line)

    yield section_name, section


def make_sections(lines, matchers):
    """Partition the contents of a file into sections using the given list
    of matchers.

    :param lines: An iterator or generator that produces lines of text
    input

    :param matchers: A list of callables that, when called with a line
    of text, should return either None, a section name, or a callable.

    :returns: An OrderedDict mapping section names to section contents
    (a list of string)

    """
    return OrderedDict(generate_sections(lines, matchers))


def get_lines(doc):
    """Returns a generator that successively produces lines from the
    document."""
    enc = doc.encoding
    lines = (line.decode(enc) for line in doc.fulltext)

    return lines


staff_report_section_matchers = [
    skip_match(r"CITY HALL", 2),
    skip_match(r"Page \d+ of \d+"),
    make_matcher(r"PLANNING STAFF REPORT",
                 fn=str.lower),
    make_matcher(r"^[IVX]+\. ([^a-z]+)(\n|$)",
                 group=1,
                 fn=str.lower)
]


def staff_report_sections(doc_json):
    lines = doc_json["lines"]
    return make_sections(lines, staff_report_section_matchers)


# TODO: Clean up the dates of public hearing


def staff_report_properties(doc_json):
    """Extract a dictionary of properties from the plaintext contents of a
    Planning Staff Report.
    """
    sections = staff_report_sections(doc_json)
    props = {}

    props.update(properties(sections["header"]))
    props.update(properties(sections["planning staff report"]))

    pd = sections.get("project description")
    if pd:
        subsections = make_sections(pushback_iter(pd),
                                    [subsection_matcher])

        for pname in ["Proposal", "Subject Property",
                      "Green Building Practices"]:
            v = subsections.get(pname)
            if v:
                props[pname] = "\n".join(paragraphize(v))

    return props


# Decision Documents
def find_vote(decision):
    """From the decision text, perform a very crude pattern match that extracts
    the vote (for/against).
    """
    patt = re.compile(r"voted (\d+-\d+)", re.I)
    m = re.search(patt, decision)

    if m:
        return m.group(1).split("-")

    return None, None

decision_section_matchers = [
    skip_match(r"CITY HALL", 2),
    make_matcher(r"(ZBA DECISION|DESCRIPTION|PLANNING BOARD DECISION):?",
                 value="properties"),
    make_matcher(r"DECISION:", value="decision"),
    top_section_matcher
]


def decision_sections(doc_json):
    lines = doc_json["lines"]
    return make_sections(lines, decision_section_matchers)


def decision_properties(doc_json):
    """Extract a dictionary of properties from the contents of a Decision
    Document."""
    sections = decision_sections(doc_json)
    props = {}
    if "properties" in sections:
        props.update(properties(sections["properties"]))

    vote = find_vote(" ".join(sections["decision"]))
    if vote:
        props["Vote"] = vote

    return props


def remove_match(s, m):
    return s[0:m.start()].rstrip() + s[m.end():]


def doc_type(doc_json):
    if doc_json["field"] == "reports" and re.match(r"staff report",
                                                   doc_json["title"], re.I):
        return "report"
    elif re.match(r"decision", doc_json["title"], re.I):
        return "decision"

    return ""


def get_decision(prop):
    pass


def get_properties(doc_json):
    # Eventually, we'll want to introduce a pluggable property
    # extraction interface, so that other cities and formats can be
    # supported.
    dtype = doc_type(doc_json)
    if dtype == "report":
        return staff_report_properties(doc_json)
    elif dtype == "decision":
        return decision_properties(doc_json)
    else:
        return {}


def split_event(desc):
    """
    Splits a string description of an event into
    """
    now = datetime.now()
    dt, tokens = date_parse(desc, fuzzy_with_tokens=True, default=now)

    if dt == now:
        return None

    dt = pytz.timezone("US/Eastern").localize(dt)

    if len(tokens) > 0:
        event_desc = tokens[0].strip()

        if event_desc and not desc.index(event_desc.lstrip()) == 0:
            event_desc = ""
    else:
        event_desc = ""

    return {"date": dt, "title": event_desc}

event_fields = [("Dates of Public Hearing", "Public Hearing"),
                ("Date of Public Meeting", "Public Hearing")]


def get_events(doc, props=None, fields=event_fields):
    if doc.field == "reports":
        if not props:
            props = get_properties(doc)

        events = []
        for (field, title) in fields:
            date_prop = props.get(field)
            if date_prop:
                event = split_event(date_prop)
                if not event["title"]:
                    event["title"] = title

                events.append(event)

        return events
