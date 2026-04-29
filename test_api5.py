import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from omop_core.models import PatientInfo

p = PatientInfo.objects.first()

client = APIClient()
user = User.objects.first()
client.force_authenticate(user=user)

response = client.patch(f'/api/patient-info/{p.id}/', {'relapse_count': 5}, format='json')
print(f"Status: {response.status_code}")
if response.status_code != 200:
    print(response.content)

