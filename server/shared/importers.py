import imp
import os


def get_module(file_name, path):
    try:
        assert file_name.endswith(".py")
        mod_name = file_name[0:-3]
        file_path = os.path.join(path, file_name)
        mod = imp.load_source(mod_name, file_path)
        return mod
    except:
        return None


def find_modules(path):
    for file_name in os.listdir(path):
        mod = get_module(file_name, path)
        if mod: yield mod
