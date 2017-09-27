import re

from django.core.cache import cache
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

import celery
from celery.utils.log import get_task_logger
from scripts import vision

from .models import Image

task_logger = get_task_logger(__name__)


