import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from omop_core.models import PatientInfo
from patient_portal.api.serializers import PatientInfoSerializer

p = PatientInfo.objects.first()
person_id = p.person.person_id

client = APIClient()
user = User.objects.first()
client.force_authenticate(user=user)

serializer = PatientInfoSerializer(p)
data = serializer.data
data['relapse_count'] = 7  # explicit change!

response = client.patch(f'/api/patient-info/{person_id}/', data, format='json')
p.refresh_from_db()
print(f"After PATCH (all fields, relapse_count=7), DB relapse_count: {p.relapse_count}")
