#!/bin/bash

cd $(dirname "${BASH_SOURCE[0]}")
mkdir -p logs

export C_FORCE_ROOT=1

pip install -q -r /support/requirements.txt

if [ "$APP_MODE" = "production" ]; then
    # Only run tasks automatically in production:
    python manage.py celerybeat --detach
else
    celery_opts=" --loglevel=INFO -f /logs/celery.log --autoreload"
fi

celery_opts+=" --autoscale=$CELERY_MAX_WORKERS,$CELERY_MIN_WORKERS"

if ((CELERY_MONITOR)); then
    celery_opts+=" -E"
fi

celery worker -A $APP_NAME $celery_opts
