#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate

echo "Creating admin user..."
python manage.py setup_admin

echo "Starting gunicorn..."
exec gunicorn ctomop.wsgi:application
