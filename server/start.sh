#!/bin/bash
service postgresql start
service redis-server start # Required for celery

pid_file=/var/run/_citydash_django.pid
server_out=/app/django.log
server_err=/app/error.log

if [ -f $pid_file ]; then
    pid=$(cat $pid_file);
    echo "Killing server ($pid)";
    kill -KILL $(cat $pid_file);
    rm -f $pid_file
fi;

# Prefer Python 3:
PYTHON_BIN=$(which python3 || which python)
echo "Starting Django.  Logging output to: $(readlink -f $server_out)"
nohup $PYTHON_BIN /app/manage.py runserver 0.0.0.0:3000 >$server_out 2>$server_err&
echo $! >$pid_file