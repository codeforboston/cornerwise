#!/bin/bash

# In case the requirements have changed.
pip install -q -r /support/requirements.txt

if [ -f "/support/$APP_MODE-requirements.txt" ]; then
    pip install -q -r /support/$APP_MODE-requirements.txt
fi

cd $(dirname "${BASH_SOURCE[0]}")
mkdir -p logs

if [ -z "$APP_ROOT" ]; then
    export APP_ROOT=$(pwd)
fi

# Wait until Postgres is accepting connections:
trial_count=0
while ! timeout 1 bash -c "echo > /dev/tcp/$POSTGRES_HOST/5432" 2>/dev/null; do
    trial_count=$((trial_count+1))
    if ((trial_count == 12)); then
        echo "Postgres took too long to start."
        exit 1
    fi
    sleep 5;
done

# Prefer Python 3:
PYTHON_BIN=$(which python3 || which python)
manage="$PYTHON_BIN $APP_ROOT/manage.py"

echo "Applying any outstanding migrations"
$manage migrate

echo "Creating views"
$manage sync_pgviews

rm /tmp/*.pid

# Start celery in the background of this container if there is not a linked
# container running with the name 'celery'.
if ! getent hosts celery; then
    export C_FORCE_ROOT=1

    if ((CELERY_MONITOR)); then
        celery_opts="-E"
    fi

    celery -A $APP_NAME beat --pidfile=/tmp/celerybeat.pid &
    celery -A $APP_NAME worker --loglevel=INFO \
           --pidfile=/tmp/celery.pid \
           --autoscale=$CELERY_MAX_WORKERS,$CELERY_MIN_WORKERS \
           $celery_opts &
fi

if [ "$APP_MODE" = "production" ]; then
    gunicorn --bind "0.0.0.0:${APP_PORT:=3000}" \
             cornerwise.wsgi:application
else
    $manage runserver 0.0.0.0:$APP_PORT
fi
