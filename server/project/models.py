from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.forms.models import model_to_dict


class Project(models.Model):
    name = models.CharField(max_length=128,
                            unique=True)
    department = models.CharField(max_length=128,
                                  db_index=True,)
    category = models.CharField(max_length=20,
                                db_index=True)
    region_name = models.CharField(max_length=128,
                                   default="Somerville, MA")
    shape = models.MultiPolygonField(null=True)
    description = models.TextField(default="")
    justification = models.TextField(default="")
    website = models.URLField(null=True)
    approved = models.BooleanField(db_index=True)

    def to_dict(self, include_budget=True):
        d = model_to_dict(self)

        if include_budget:
            d["budget"] = {bi.year: {"budget": bi.budget,
                                     "funding_source": bi.funding_source}
                           for bi in self.budgetitem_set.all()}

        return d

    @classmethod
    def create_from_dict(kls, d):
        project = kls(name=d["name"],
                      department=d["department"],
                      category=d["category"],
                      region_name=d["region_name"],
                      description=d["description"],
                      justification=d["justification"],
                      approved=d["approved"])

        project.save()

        for year, amount in d["budget"].items():
            project.budgetitem_set.create(year=year,
                                          budget=amount,
                                          funding_source=d["funding_source"])

        if d["address"]:
            # Future notes: Each location associated with a project could
            # potentially have its own description.
            project.proposal_set.create(case_number="CP " + str(project.pk),
                                        summary=d["description"],
                                        source="",
                                        updated=d["updated"],
                                        region_name=d["region_name"],
                                        address=d["address"],
                                        status=d["status"],
                                        # TODO: Rethink this.
                                        complete=False,
                                        location=Point(d["long"], d["lat"]))
            project.address = d["address"]
            project.location = Point(d["long"], d["lat"])

        return project


class BudgetItem(models.Model):
    project = models.ForeignKey(Project)
    year = models.IntegerField()
    budget = models.DecimalField(max_digits=11, decimal_places=2)
    funding_source = models.CharField(max_length=64)
    comment = models.TextField()

    def to_dict(self):
        return model_to_dict(self)
