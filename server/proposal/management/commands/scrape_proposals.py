from django.core.management.base import BaseCommand
from proposal import tasks

import argparse
from datetime import datetime, timedelta
import sys
import time


def datetype(fmt):
    def parse_date(s):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            raise argparse.ArgumentTypeError(
                "Could not parse datetime '%s' (expected mm/dd/yyyy)" % s)

    return parse_date


def format_duration(sec):
    m, s = divmod(int(sec), 60)
    pieces = []
    if m:
        pieces.append(str(m) + " minutes")
    if s:
        pieces.append(str(s) + " seconds")
    return " ".join(pieces)


class Command(BaseCommand):
    help = "Pull proposals from available importers."

    def add_arguments(self, parser):
        parser.add_argument("since", nargs=1, type=datetype("%m/%d/%Y"),
                            help="specify start date for proposals to fetch",
                            default=(datetime.now() - timedelta(days=14)))
        parser.add_argument("-i", "--importer", default={},
                            help="Filter importers by region name")

    def handle(self, *args, **options):
        start_time = datetime.now()
        result = tasks.pull_updates.delay(
            options["since"],
            importers_filter=options["importer"])

        wait_count = 0
        while result.status == "PENDING":
            time.sleep(1)
            wait_count += 1
            if wait_count > 15:
                self.stderr.write(
                    "Task did not start within 15 seconds. "
                    "Is Celery running?")
                result.revoke()
                sys.exit(1)

        self.stdout.write("Running tasks.pull_updates.\n"
                          "This may take some time.\n"
                          "Check the celery terminal for detailed logs.")
        proposals = result.get()
        duration = datetime.now().timestamp() - start_time.timestamp()
        self.stdout.write("Fetched {count} proposals in {duration}"
                          .format(count=len(proposals),
                                  duration=format_duration(duration)))
