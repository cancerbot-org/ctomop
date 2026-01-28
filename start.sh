#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate

echo "Creating/resetting admin user..."
python reset_admin.py

echo "Starting gunicorn..."
exec gunicorn ctomop.wsgi:application
