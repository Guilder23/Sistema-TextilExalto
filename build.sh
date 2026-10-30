#!/usr/bin/env bash
set -o errexit

echo "==== Installing dependencies ===="
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "==== Applying database migrations ===="
python manage.py migrate --noinput

echo "==== Creating initial administrator ===="
python manage.py crear_admin

echo "==== Collecting static files ===="
python manage.py collectstatic --noinput

echo "==== Validating deployment configuration ===="
python manage.py check --deploy

echo "==== Build completed successfully ===="