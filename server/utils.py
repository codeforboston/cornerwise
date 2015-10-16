import os, re

def normalize(s):
    s = re.sub(r"[',!@#$%^&*()-=[\]]+", "", s)
    s = re.sub(r"\s+", "_", s)

    return s.lower()

def extension(path):
    return path.split(os.path.extsep)[-1].lower()
