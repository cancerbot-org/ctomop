import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from omop_core.models import PatientInfo

p = PatientInfo.objects.first()
person_id = p.person.person_id

client = APIClient()
user = User.objects.first()
client.force_authenticate(user=user)

print(f"Original DB relapse_count: {p.relapse_count}")
response = client.patch(f'/api/patient-info/{person_id}/', {'relapse_count': 5}, format='json')
print(f"Status 1: {response.status_code}")
if response.status_code != 200: print(response.data)

p.refresh_from_db()
print(f"After PATCH (5), DB relapse_count: {p.relapse_count}")

response2 = client.patch(f'/api/patient-info/{person_id}/', {'relapse_count': ''}, format='json')
print(f"Clear Status: {response2.status_code}")
p.refresh_from_db()
print(f"After CLEAR, DB relapse_count: {p.relapse_count}")
