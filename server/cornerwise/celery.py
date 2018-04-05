# pylint: disable=E402
import os
import logging
from traceback import format_tb

from celery import Celery
from celery.signals import task_failure, task_prerun, task_postrun

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cornerwise.settings")
import django
django.setup()
from django.conf import settings
from django.utils import timezone

app = Celery("cornerwise")
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@task_failure.connect
def on_task_failure(**kwargs):
    """
    Record details when a task fails.
    """
    from redis_utils import append_to_key

    append_to_key("cornerwise:logs:task_failure",
                  {"task_id": kwargs["task_id"],
                   "task": kwargs["sender"].name,
                   "timestamp": timezone.now(),
                   "traceback": format_tb(kwargs["traceback"]),
                   "exception": type(kwargs["exception"]).__name__,
                   "message": str(kwargs["exception"]),
                   "args": kwargs["args"],
                   "kwargs": kwargs["kwargs"]})


@task_prerun.connect
def setup_task_logging(**kwargs):
    from shared.logger import RedisLoggingHandler

    task_id = kwargs["task_id"]
    if task_id:
        logger = logging.getLogger(f"celery_tasks.{task_id}")
        logger.propagate = True
        handler = RedisLoggingHandler(
            topic=f"cornerwise:task_log:{task_id}",
            expiration=604800)
        handler.setLevel(logging.INFO)
        handler.setFormatter(
            logging.Formatter("[%(asctime)s][%(levelname)s] %(message)s"))
        logger.addHandler(handler)


@task_postrun.connect
def cleanup_task_logging(task_id=None, task=None, state=None, **kwargs):
    from redis_utils import append_to_key

    if task_id:
        logger = logging.getLogger(f"celery_tasks.{task_id}")
        for handler in logger.handlers:
            handler.flush()
            handler.close()
        logger.handlers = []

        # Record that a task has recently run
        append_to_key("cornerwise:recent_tasks", (task.name, task_id, state))
