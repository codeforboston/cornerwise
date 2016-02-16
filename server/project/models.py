from django.db import models
from django.forms.models import model_to_dict

# A project
class Project(models.Model):
    # TODO: Use these as choices for category
    CATEGORIES = (("recurring", "Recurring"),
                  ("building", "Major Building"),
                  ("planning", "Planning"),
                  ("parks", "Parks and Playgrounds"),
                  ("infrastructure", "Infrastructure"),
                  ("onetime", "One-Time"))

    name = models.CharField(max_length=128,
                            unique=True)
    department = models.CharField(max_length=128,
                                  db_index=True,)
    category = models.CharField(max_length=20,
                                db_index=True)
    region_name = models.CharField(max_length=128,
                                   default="Somerville, MA")
    description = models.TextField(default="")
    justification = models.TextField(default="")
    website = models.URLField(null=True)
    approved = models.BooleanField(db_index=True)

    def to_dict(self, include_budget=True):
        d = model_to_dict(self)

        if include_budget:
            d["budget"] = {bi.year: bi.to_dict() for bi in
                           self.budgetitem_set.all()}

        return d


class BudgetItem(models.Model):
    project = models.ForeignKey(Project)
    year = models.IntegerField()
    budget = models.DecimalField(max_digits=11, decimal_places=2)
    funding_source = models.CharField(max_length=64)
    comment = models.TextField()

    def to_dict(self):
        return model_to_dict(self)
