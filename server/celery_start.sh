#!/bin/bash

cd $(dirname "${BASH_SOURCE[0]}")

export C_FORCE_ROOT=1

pip install -q -r /support/requirements.txt

if [ "$APP_MODE" = "production" ]; then
    # Only run tasks automatically in production:
    python manage.py celerybeat --detach
else
    celery_opts=" --loglevel=INFO --autoreload"
fi

python manage.py celery worker $celery_opts
