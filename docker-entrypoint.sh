#!/usr/bin/env bash
set -e

cd Alexandrian-Library

python manage.py migrate --noinput

# python manage.py collectstatic --noinput

# exec gunicorn core.wsgi:application -b 0.0.0.0:8000 --workers 3

python manage.py runserver 0.0.0.0:8000
