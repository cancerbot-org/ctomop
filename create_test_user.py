#!/usr/bin/env python
"""Create or reset testuser account"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()

from django.contrib.auth.models import User

username = 'testuser'
password = 'testpass123'
email = 'testuser@example.com'

user = User.objects.filter(username=username).first()
if user:
    print(f"User '{username}' exists")
    user.set_password(password)
    user.save()
    print(f"✓ Password reset to '{password}'")
else:
    user = User.objects.create_user(username=username, password=password, email=email, first_name='Test', last_name='User')
    print(f"✓ Created user '{username}' with password '{password}'")

print(f"\nYou can now login with:")
print(f"  Username: {username}")
print(f"  Password: {password}")
