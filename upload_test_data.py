#!/usr/bin/env python
"""Script to upload test FHIR data directly using Django ORM"""

import os
import django
import json
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()

from patient_portal.api.views import PatientInfoViewSet
from rest_framework.test import APIRequestFactory
from django.contrib.auth.models import User

# Create a fake request with the FHIR data
factory = APIRequestFactory()

# Load the FHIR bundle
with open('data/test_patients.json', 'rb') as f:
    file_data = f.read()

# Create a mock uploaded file
file_io = BytesIO(file_data)
mock_file = InMemoryUploadedFile(
    file_io,
    'file',
    'test_patients.json',
    'application/json',
    len(file_data),
    None
)
file_io.seek(0)  # Reset to beginning

# Create a mock user
user, _ = User.objects.get_or_create(username='admin', is_staff=True, is_superuser=True)

# Create request with file
request = factory.post('/api/patients/upload_fhir/', {'file': mock_file}, format='multipart')
request.user = user
request.FILES['file'] = mock_file

# Create viewset and call the action
viewset = PatientInfoViewSet()
viewset.format_kwarg = None

# Call upload directly
response = viewset.upload_fhir(request)

print(f"Status: {response.status_code}")
print(f"Response: {response.data}")
