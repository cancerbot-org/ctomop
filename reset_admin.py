#!/usr/bin/env python
"""
Simple script to reset admin password
Run with: python reset_admin.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()

from django.contrib.auth.models import User

username = 'admin'
password = '1database'

try:
    user = User.objects.get(username=username)
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print(f"✓ Password reset for user '{username}'")
    print(f"✓ Username: {username}")
    print(f"✓ Password: {password}")
except User.DoesNotExist:
    user = User.objects.create_superuser(
        username=username,
        email='admin@example.com',
        password=password
    )
    print(f"✓ Created new superuser '{username}'")
    print(f"✓ Username: {username}")
    print(f"✓ Password: {password}")
