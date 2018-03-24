#!/bin/bash

# Restart celery

cd $(dirname "${BASH_SOURCE[0]}")
mkdir -p logs

if [ -f /tmp/celery.pid ]; then
    kill -2 $(cat /tmp/celery.pid)
    rm /tmp/celery.pid
fi

if ! getent hosts celery; then
    export C_FORCE_ROOT=1

    celery multi restart 2 -A $APP_NAME -l "${CELERY_LOGLEVEL:-info}" $celery_opts \
           --pidfile=/var/run/celery/%n.pid \
           --logfile=/var/log/celery/%n%I.log
fi
