from django.conf import settings
from django.db.models import Q
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404, render

from shared.request import make_response

from .models import Project, BudgetItem

@make_response()
def view_project(req, pk=None):
    if not pk:
        pk = req.GET.get("pk")

    project = get_object_or_404(Project, pk=pk)

    return project.to_dict()

@make_response()
def list_projects(req):
    return {"projects": [p.to_dict() for p in Project.objects.all()]}
