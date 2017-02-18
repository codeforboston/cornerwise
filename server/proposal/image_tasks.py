import re

from django.core.cache import cache
from django.db.models import F
from django.db.models.signals import post_save
from django.dispatch import receiver

import celery
from celery.utils.log import get_task_logger
from cornerwise import celery_app
from scripts import vision

from .models import Image

task_logger = get_task_logger(__name__)


@celery_app.task(name="proposal.cloud_vision_process")
def cloud_vision_process(image_id):
    processed_key = f"image:{image_id}:logo_checked"
    image = Image.objects.annotate(region_name=F("proposal__region_name"))\
                         .get(pk=image_id)
    if not image.image or cache.get(processed_key):
        return

    city_name = re.split(r"\s*,\s*", image.region_name, 1)[0]
    processed = vision.process_image(image.image.path, )
    logo = processed.get("logo")
    if logo:
        if city_name in logo["description"]:
            image.delete()
            task_logger.info("Logo detected: image #%i deleted", image.pk)
        else:
            cache.set(f"image:{image_id}:logo", logo)
    cache.set(processed_key, True)


def process_image(image):
    if vision.CLIENT:
        cloud_vision_process.delay(image.pk)


@receiver(post_save, sender=Image, dispatch_uid="process_image")
def image_hook(**kwargs):
    image = kwargs["instance"]
    if image.image:
        process_image(image)
