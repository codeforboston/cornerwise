import os
import re

def extension(path):
    return path.split(os.path.extsep)[-1].lower()
