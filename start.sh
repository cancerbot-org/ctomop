#!/bin/bash
set -e

echo "========================================="
echo "Starting Render deployment"
echo "========================================="

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating/resetting admin user..."
python reset_admin.py || {
    echo "ERROR: Failed to create admin user"
    exit 1
}

echo "Verifying admin user exists..."
python -c "
from django.contrib.auth.models import User
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()
try:
    user = User.objects.get(username='admin')
    print(f'✓ Admin user verified: {user.username} (ID: {user.id})')
except User.DoesNotExist:
    print('✗ ERROR: Admin user not found after creation!')
    exit(1)
"

echo "========================================="
echo "Starting gunicorn..."
echo "========================================="
exec gunicorn ctomop.wsgi:application
