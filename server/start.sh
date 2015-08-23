#!/bin/bash
service postgresql start
service redis-server start # Required for celery and caching

# Force Celery to run as root:
export C_FORCE_ROOT=1

if [ -z "$APP_ROOT" ]; then
    export APP_ROOT=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
fi

if [ -z "$APP_NAME" ]; then
    export APP_NAME=$(basename $(dirname $(find $APP_ROOT -name settings.py | head -n 1)))
fi

pid_file=/var/run/$APP_NAME_django.pid
server_out=$APP_ROOT/django.log
server_err=$APP_ROOT/error.log

# The APP_PORT global is set
if [ -z "$APP_PORT" ]; then
    export APP_PORT=3000
fi

if [ -n "$1" ]; then
    port="$1"
fi

if pid=$(cat $pid_file); then
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
$PYTHON_BIN $APP_ROOT/manage.py migrate --database=migrate
echo "Starting Django.  Logging output to: $(readlink -f $server_out)"
nohup $PYTHON_BIN $APP_ROOT/manage.py runserver 0.0.0.0:$APP_PORT >$server_out 2>$server_err&
echo $! >$pid_file

sleep 1
server_ping=$(curl -s "http://0.0.0.0:3000/ping")
curl_code=$?

if ((curl_code)); then
    tail $server_err
else
    if [ "$server_ping" = "running" ]; then
        echo "Django is now running on port $APP_PORT."
    else
        echo "The server is running, but there may be a configuration error."
    fi
fi
