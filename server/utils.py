import os, re

def normalize(s):
    s = re.sub(r"[',!@#$%^&*()-=[\]]+", "", s)
    s = re.sub(r"\s+", "_", s)

    return s.lower()

def extension(path):
    return path.split(os.path.extsep)[-1].lower()

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
