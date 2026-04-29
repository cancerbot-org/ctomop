import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from omop_core.models import PatientInfo

p = PatientInfo.objects.first()
print(f"Original DB relapse_count: {p.relapse_count}")

client = APIClient()
user = User.objects.first()
client.force_authenticate(user=user)

response = client.patch(f'/api/patients/{p.id}/', {'relapse_count': 5}, format='json')

print(f"Response status: {response.status_code}")
print(f"Response data: {response.data.get('relapse_count')}")

p.refresh_from_db()
print(f"Updated DB relapse_count: {p.relapse_count}")
