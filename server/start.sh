#!/bin/bash
service postgresql start
service redis-server start # Required for celery and caching

pip install -q -r /support/requirements.txt

if [ -z "$APP_ROOT" ]; then
    export APP_ROOT=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
fi

if [ -z "$APP_NAME" ]; then
    export APP_NAME=$(basename $(dirname $(find $APP_ROOT -name settings.py | head -n 1)))
fi

pid_file=/var/run/${APP_NAME}_django.pid
server_out=$APP_ROOT/django.log
server_err=$APP_ROOT/error.log

# The APP_PORT global is set
if [ -z "$APP_PORT" ]; then
    export APP_PORT=3000
fi

if [ -n "$1" ]; then
    port="$1"
fi

if [ -f $pid_file ]; then
    pid=$(cat $pid_file)
    if kill $pid 2>/dev/null; then
        echo "Killed running server (pid: $pid)";
    elif kill -0 $pid 2>/dev/null; then
        echo "Could not kill the running server (pid: $pid)"
        exit 1
    fi

    # Either we've killed the process, or the pid file was out of date
    rm -f $pid_file
fi;

# Prefer Python 3:
PYTHON_BIN=$(which python3 || which python)

echo "Applying any outstanding migrations"
$PYTHON_BIN $APP_ROOT/manage.py migrate

# Start Celery:
if [ "$DJANGO_MODE" != "production" ]; then
    # The --autoreload option results in very high CPU usage on
    # my machine...

    #celery_opts=" --autoreload --loglevel=INFO"
    celery_opts=" --loglevel=INFO"
fi

echo "Starting Django.  Logging output to: $(readlink -f $server_out)"
$PYTHON_BIN $APP_ROOT/manage.py runserver 0.0.0.0:$APP_PORT >>$server_out 2>>$server_err &

echo "Starting celery beat and worker"
# Force Celery to run as root
export C_FORCE_ROOT=1

celerybeat_pid_file="$APP_ROOT/celerybeat.pid" 
if [ -f "$celerybeat_pid_file" ]; then
    if kill $(cat $celerybeat_pid_file) 2>/dev/null; then
        echo "Killed running celerybeat."
    fi
fi

$PYTHON_BIN $APP_ROOT/manage.py celerybeat --detach || (echo "celery beat failed!" && exit 1)
$PYTHON_BIN $APP_ROOT/manage.py celery worker $celery_opts

if (($?)); then
    echo "I encountered an error while trying to start Django."
    exit 1;
fi



