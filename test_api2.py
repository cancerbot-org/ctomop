import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()
from django.test import RequestFactory
from django.contrib.auth.models import User
from patient_portal.api.views import PatientInfoViewSet
from omop_core.models import PatientInfo
from rest_framework.test import force_authenticate

p = PatientInfo.objects.first()
print(f"Original DB relapse_count: {p.relapse_count}")

factory = RequestFactory()
request = factory.patch(f'/api/patients/{p.id}/', {'relapse_count': 5}, content_type='application/json')
user = User.objects.first()
force_authenticate(request, user=user)

view = PatientInfoViewSet.as_view({'patch': 'partial_update'})
response = view(request, pk=p.id)

print(f"Response status: {response.status_code}")
print(f"Response data relapse_count: {response.data.get('relapse_count')}")

p.refresh_from_db()
print(f"Updated DB relapse_count: {p.relapse_count}")
