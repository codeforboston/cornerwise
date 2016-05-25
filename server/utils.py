import os
import re
from collections import deque


def normalize(s):
    s = re.sub(r"[',!@#$%^&*()-=[\]]+", "", s)
    s = re.sub(r"\s+", "_", s)

    return s.lower()


def extension(path):
    return path.split(os.path.extsep)[-1].lower()


class pushback_iter(object):
    """An iterator that implements a pushback() method, allowing values to
be added back to the 'stack' after consideration.

    """
    def __init__(self, it):
        self.iterable = iter(it)
        self.pushed = deque()

    def pushback(self, v):
        self.pushed.append(v)

    def __iter__(self):
        return self

    def __next__(self):
        if self.pushed:
            return self.pushed.pop()
        return next(self.iterable)


def make_file_mover(attr):
    """Returns a function that takes an object and a new name and renames
    the file associated with that object's `attr` file field.

    :param attr: The name of the FileField attribute on the target
    object

    :returns: A function that can be bound as a method of an object with
    the named file field.

    """
    def move_file(self, new_path):
        file_field = getattr(self, attr)
        current_path = file_field and file_field.path

        if not current_path:
            raise IOError("")

        if os.path.basename(new_path) == new_path:
            doc_dir, _ = os.path.split(current_path)
            new_path = os.path.join(doc_dir, new_path)

        if new_path != current_path:
            os.rename(current_path, new_path)

            try:
                setattr(self, attr, new_path)
                self.save()
            except Exception as err:
                os.rename(new_path, self.local_file)

                raise err

        return new_path

    return move_file


def decompose_coord(ll):
    degrees = int(ll)
    minutes = ll % 1 * 60
    seconds = minutes % 1 * 60

    return (degrees, int(minutes), seconds)


prettify_format = "{d}\N{DEGREE SIGN} {m}' {s:.2f}\" {h}"


def prettify_lat(lat):
    d, m, s = decompose_coord(lat)

    return prettify_format.\
        format(d=d, m=m, s=s, h="N" if lat > 0 else "S")


def prettify_long(lng):
    d, m, s = decompose_coord(lng)

    return prettify_format.\
        format(d=d, m=m, s=s, h="E" if lng > 0 else "W")
