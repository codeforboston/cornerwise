# pylint: disable=E402
import os
import logging
from traceback import format_tb

from celery import Celery, signals

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cornerwise.settings")
import django
django.setup()
from django.conf import settings
from django.utils import timezone

app = Celery("cornerwise")
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@signals.task_failure.connect
def on_task_failure(sender, **kwargs):
    """
    Record details when a task fails.
    """
    from cornerwise.utils import append_to_key

    append_to_key("cornerwise:logs:task_failure",
                  {"task_id": kwargs["task_id"],
                   "task": sender.name,
                   "timestamp": timezone.now(),
                   "traceback": format_tb(kwargs["traceback"]),
                   "exception": type(kwargs["exception"]).__name__,
                   "message": str(kwargs["exception"]),
                   "args": kwargs["args"],
                   "kwargs": kwargs["kwargs"]})


@signals.task_prerun.connect
def setup_task_logging(task_id=None, **kwargs):
    from shared.logger import RedisLoggingHandler

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


@signals.task_postrun.connect
def cleanup_task_logging(task_id=None, **kwargs):
    if task_id:
        logger = logging.getLogger(f"celery_tasks.{task_id}")
        for handler in logger.handlers:
            handler.flush()
            handler.close()
        logger.handlers = []
