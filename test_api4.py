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

# Use correct patient-info router path. router.register generates URLs appended with /
# However, pk is person_id or pk?
print(f"Using pk: {p.id}")
response = client.patch(f'/api/patient-info/{p.id}/', {'relapse_count': 5}, format='json')

print(f"Response status: {response.status_code}")
print(f"Response data: {response.data.get('relapse_count') if hasattr(response, 'data') else response.content}")

p.refresh_from_db()
print(f"Updated DB relapse_count: {p.relapse_count}")
