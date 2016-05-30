#!/bin/bash

# In case the requirements have changed.
pip install -q -r /support/requirements.txt

cd $(dirname "${BASH_SOURCE[0]}")

if [ -z "$APP_ROOT" ]; then
    export APP_ROOT=$(pwd)
fi

# The APP_PORT global is set
if [ -z "$APP_PORT" ]; then
    export APP_PORT=3000
fi

# Prefer Python 3:
PYTHON_BIN=$(which python3 || which python)

echo "Applying any outstanding migrations"
$PYTHON_BIN $APP_ROOT/manage.py migrate

if [ "$APP_MODE" = "production" ]; then
    gunicorn -b "0.0.0.0:$APP_PORT" cornerwise.wsgi
else
    $PYTHON_BIN $APP_ROOT/manage.py runserver 0.0.0.0:$APP_PORT
fi
