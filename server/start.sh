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

echo "Applying any outstanding migrations"
$PYTHON_BIN $APP_ROOT/manage.py migrate

if [ "$APP_MODE" = "production" ]; then
    gunicorn -b "0.0.0.0:$APP_PORT" cornerwise.wsgi
else
    $PYTHON_BIN $APP_ROOT/manage.py runserver 0.0.0.0:$APP_PORT
fi
