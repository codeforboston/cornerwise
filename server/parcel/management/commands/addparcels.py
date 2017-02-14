from django.core.management.base import BaseCommand, CommandError
import logging
import imp
import os

from shared import importers
from parcel.models import LotSize

logger = logging.getLogger(__name__)

IMPORTER_DIR = "/app/parcel/importers" 


def find_importers():
    return filter(lambda mod: hasattr(mod, "run"),
                  importers.find_modules(IMPORTER_DIR))


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
            raise CommandError("You did not tell me what to import!\n"
                               "Run again with --help argument for usage.")

        modules = []
        for mod_name in options["name"]:
            mod = importers.get_module(mod_name + ".py", IMPORTER_DIR)
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
            self.stdout.write("This will take a while!")
            run_fn(logger)
        self.stdout.write("Import complete")

        LotSize.refresh()
