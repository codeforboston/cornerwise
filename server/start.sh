#!/bin/bash

service postgresql start

cd /app
python manage.py runserver 0.0.0.0:3000
