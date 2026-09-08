#!/bin/bash
set -e

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating/resetting admin user..."
python manage.py setup_admin

# Deployment checks are opt-in: `deploy=True` checks run on `check --deploy`
# and on nothing else, so without this line patient_portal.W010 -- which names
# the OAuth2 Application rows whose redirect URI scheme is refused -- would
# never execute. `--fail-level ERROR` keeps warnings visible without gating the
# boot on them. `dev` has carried this line since #749; `cb` had not (#146).
echo "Running deployment checks..."
python manage.py check --deploy --fail-level ERROR

echo "Starting gunicorn..."
exec gunicorn ctomop.wsgi:application
