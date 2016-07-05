from django.core.management.base import BaseCommand, CommandError
import logging
import imp
import os

logger = logging.getLogger(__name__)

IMPORTER_DIR = "/app/parcel/importers"


def get_importer_module(file_name, path=IMPORTER_DIR):
    try:
        assert file_name.endswith(".py")
        mod_name = file_name[0:-3]
        file_path = os.path.join(path, file_name)
        mod = imp.load_source(mod_name, file_path)
        assert hasattr(mod, "run")
        return mod
    except:
        return None


def find_importers(path=IMPORTER_DIR):
    for file_name in os.listdir(path):
        mod = get_importer_module(file_name, path)
        if mod: yield mod


class Command(BaseCommand):
    help = "Import parcel shapes using an available importer"

    def add_arguments(self, parser):
        parser.add_argument("name", nargs="*",
                            help="Name of the parcel importer to run")
        parser.add_argument("-l", "--list", default=False, action="store_true",
                            help="List the available importers")
        parser.add_argument("-a", "--all", default=False, action="store_true",
                            help="Run all importers")

    def handle(self, *args, **options):
        if options["list"]:
            return self.run_list()

        if options["all"]:
            self.run_all()

        if not options["name"]:
            raise CommandError("You did not tell me what to import!")

        modules = []
        for mod_name in options["name"]:
            mod = get_importer_module(mod_name + ".py")
            if not mod:
                raise CommandError("Unknown importer '%s'\n" % mod_name)
            modules.append(mod)

        self.run_import(modules)

    def run_list(self):
        self.stdout.write("Available importers:\n")
        for mod in find_importers():
            mod_name = getattr(mod, "name", None)
            mod_file = os.path.basename(mod.__file__)[0:-3]
            self.stdout.write(" - %s %s\n" % (mod_file, "(" + mod_name + ")" if mod_name else ""))


    def run_all(self):
        self.run_import(find_importers())

    def run_import(self, modules):
        for module in modules:
            run_fn = getattr(module, "run")
            mod_name = getattr(module, "name", module.__name__)
            self.stdout.write("Running importer for '%s'\n" % mod_name)
            run_fn(logger)
        self.stdout.write("Import complete")
