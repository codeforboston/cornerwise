import re

subs = {
    "AVENUE": "AVE",
    "COURT": "CT",
    "CRT": "CT",
    "DRIVE": "DR",
    "ROAD": "RD",
    "SQUARE": "SQ",
    "SQR": "SQUARE",
    "STREET": "ST",
    "STR": "ST",
    "TERRACE": "TER"
}

def normalize_street(street):
    street = street.upper()
    pieces = re.split(r"[\s.]+", street)
    return " ".join(subs.get(p, p) for p in pieces if p)

def normalize_number(num):
    m = re.match(r"\d+", num)
    if m:
        return m.group(0)

def split_address(s):
    m = re.match(r"(\d+)(-\d+)?\s", s)
    if m:
        number = m.group(1)
        street = s[m.end():]

        return number, street
