#!/bin/bash

# In case the requirements have changed.
pip install -q -r /support/requirements.txt

# Get the subnet mask and IP address of the container
export CONTAINER_CIDR=$(ip -4 addr show eth0 | grep -Po 'inet \K[\d.]+/[\d]+')
export CONTAINER_IP=$(echo $CONTAINER_CIDR | cut -f 1 -d /)

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

# Start celery in the background of this container if there is not a linked
# container running with the name 'celery'.
if ! getent hosts celery; then
    export C_FORCE_ROOT=1

    if ((CELERY_MONITOR)); then
        celery_opts="-E"
    fi

    start_celery() {
        mkdir -p /var/log/celery /var/run/celery

        celery -A $APP_NAME beat \
               --pidfile=/var/run/celery/celerybeat.pid \
               --detach \
               --logfile=/var/log/celery/beat.log \
               $@
        mkdir -p /var/run/celery /var/log/celery
        celery multi start ${CELERY_WORKER_COUNT:-2} -A $APP_NAME -l "${CELERY_LOGLEVEL:-info}" $1 \
               --pidfile=/var/run/celery/%n.pid \
               --logfile=/var/log/celery/%n.log
    }

    restart_celery() {
        if compgen -G /var/run/celery/*.pid > /dev/null; then
            pids=$(cat /var/run/celery/*.pid)
            echo "Killing $(echo $pids | wc -w) celery worker(s)"
            kill $pids
            while ps $pids > /dev/null; do
                sleep 1
            done
        fi
        start_celery $celery_opts
    }

    autoreload_celery() {
        while : ; do
            inotifywait -e modify $APP_ROOT/*/tasks.py
            restart_celery
        done
    }

    rm /var/run/celery/*.pid
    start_celery $celery_opts
    celery_started=1

    if [ "$APP_MODE" != "production" ]; then
        which inotifywait && autoreload_celery &
    fi
fi

start_gunicorn() {
    pidfile=/var/run/gunicorn.pid
    GUNICORN_OPTS=""
    if [ "$AUTO_RELOAD" = "1" ]; then
        GUNICORN_OPTS="$GUNICORN_OPTS --reload"
    fi
    gunicorn --bind "0.0.0.0:${APP_PORT:=3000}" \
             -p "$pidfile" \
             --daemon \
             $GUNICORN_OPTS \
             cornerwise.wsgi:application

    while [ ! -f "$pidfile" ]; do sleep 1; done
    server_pid="$(cat /var/run/gunicorn.pid)"
}

on_sigterm() {
    kill -SIGTERM $server_pid

    if ((celery_started)); then
        celery multi stop 2
    fi
}

on_usr1() {
    # On receiving a SIGUSR1 signal, re-collect the static files, then restart
    # the server.
    # Note: Only one container should receive the signal.
    echo "Received SIGUSR1"
    $manage collectstatic --no-input 2>/dev/null ||
        echo "collectstatic failed; it may not be configured"
}

on_sighup() {
    if [ "$APP_MODE" = "production" ]; then
        # Gunicorn reloads the configuration and restarts the workers:
        kill -s SIGHUP $server_pid
    elif ! ps -p "$server_pid" > /dev/null ; then
        $manage runserver 0.0.0.0:${APP_PORT:-3000}
    fi

    if [ -n "$celery_started" ]; then
        restart_celery
    fi
}

on_usr2() {
    echo "Received SIGUSR2"
    kill -s SIGUSR2 $server_pid
    kill -s SIGWINCH $server_pid
}

if [ "$APP_MODE" = "production" ]; then
    start_gunicorn

    trap on_usr2 SIGUSR2
else
    $manage runserver 0.0.0.0:${APP_PORT:-3000} &

    server_pid="$!"
fi

trap on_usr1 SIGUSR1
trap on_sighup SIGHUP
trap on_sigterm SIGTERM
while : ; do wait; done
