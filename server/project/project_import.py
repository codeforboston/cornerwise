import csv, os, re, sys
from decimal import Decimal

from django.contrib.gis.geos import Point

from .models import *
from proposal.models import Proposal

def rows_import(rows):
    i = 0
    for row in rows:
        if row["Total/Subtotal"] == "Subtotal":
            # Add BudgetItems
            continue

        project = Project()
        project.name = row["Project"]
        project.department = row["Department"]
        project.category = row["Type"]
        project.approved = row["Status"] == "Approved"

        project.save()

        i += 1

        for k, v in row.items():
            if not v or not k.isdigit():
                continue

            year = int(k)
            amount = Decimal(v[1:])
            project.budgetitem_set.create(year=year, budget=amount)

        address = row["Address"]
        if address:
            m = re.search(r"\((-?\d+\.\d+), (-?\d+\.\d+)\)", address)
            if m:
                point = Point(x=float(m.group(2)),
                              y=float(m.group(1)))
                address_line = address.split("\n")

                # Use placeholder for case number
                project.proposals.create(case_number="CP %i" % i,
                                         address=address_line[0],
                                         location=point)

        i += 1

def csv_import(infile):
    rows_import(csv.DictReader(infile))
