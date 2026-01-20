from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import logout, login
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from omop_core.models import Person, PatientInfo
from datetime import datetime
import csv
import json
from io import StringIO
from .serializers import (
    UserSerializer, PatientInfoSerializer, PatientListSerializer
)
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

@method_decorator(csrf_exempt, name='dispatch')
class CurrentUserViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """Just return the logged-in user info - they don't need to be a patient"""
        if not request.user.is_authenticated:
            return Response({'error': 'Not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user_serializer = UserSerializer(request.user)
        return Response({
            'user': user_serializer.data
        })

@method_decorator(csrf_exempt, name='dispatch')
class PatientInfoViewSet(viewsets.ModelViewSet):
    serializer_class = PatientInfoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return PatientInfo.objects.all().select_related('person')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PatientListSerializer
        return PatientInfoSerializer
    
    def list(self, request):
        """List all patients - accessible to authenticated users"""
        queryset = self.get_queryset().order_by('-created_at')
        serializer = PatientListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        """Get detailed patient info for a specific person"""
        try:
            person = Person.objects.get(person_id=pk)
            patient_info = PatientInfo.objects.get(person=person)
            
            # Get the User associated with this person (not the logged-in user)
            try:
                patient_user = User.objects.get(id=person.person_id)
                user_serializer = UserSerializer(patient_user)
                user_data = user_serializer.data
            except User.DoesNotExist:
                user_data = None
            
            patient_serializer = PatientInfoSerializer(patient_info)
            
            return Response({
                'patient_info': patient_serializer.data,
                'user': user_data
            })
        except Person.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
        except PatientInfo.DoesNotExist:
            return Response({'error': 'Patient information not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['post'])
    def upload_csv(self, request):
        """Upload patients from CSV file"""
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        if not file.name.endswith('.csv'):
            return Response({'error': 'File must be a CSV'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            decoded_file = file.read().decode('utf-8')
            csv_data = StringIO(decoded_file)
            reader = csv.DictReader(csv_data)
            
            created_count = 0
            errors = []
            
            for row_num, row in enumerate(reader, start=2):
                try:
                    person_id = int(row.get('person_id', 0))
                    if person_id == 0:
                        last_person = Person.objects.all().order_by('-person_id').first()
                        person_id = last_person.person_id + 1 if last_person else 1000
                    
                    person, created = Person.objects.get_or_create(
                        person_id=person_id,
                        defaults={
                            'year_of_birth': int(row.get('year_of_birth', datetime.now().year - 50)),
                            'gender_concept': None,
                            'race_concept': None,
                            'ethnicity_concept': None,
                        }
                    )
                    
                    date_of_birth = None
                    if row.get('date_of_birth'):
                        try:
                            date_of_birth = datetime.strptime(row['date_of_birth'], '%Y-%m-%d').date()
                        except ValueError:
                            try:
                                date_of_birth = datetime.strptime(row['date_of_birth'], '%m/%d/%Y').date()
                            except ValueError:
                                pass
                    
                    patient_info, pi_created = PatientInfo.objects.update_or_create(
                        person=person,
                        defaults={
                            'phone_number': row.get('phone_number', ''),
                            'date_of_birth': date_of_birth,
                            'disease': row.get('disease', ''),
                        }
                    )
                    
                    if pi_created:
                        created_count += 1
                        
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            return Response({
                'success': True,
                'created_count': created_count,
                'errors': errors
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def upload_fhir(self, request):
        """Upload patients from FHIR JSON file"""
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        file = request.FILES['file']
        if not file.name.endswith('.json'):
            return Response({'error': 'File must be a JSON file'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            fhir_data = json.load(file)
            
            if fhir_data.get('resourceType') != 'Bundle':
                return Response({'error': 'FHIR file must be a Bundle'}, status=status.HTTP_400_BAD_REQUEST)
            
            created_count = 0
            errors = []
            
            # Group resources by patient
            patients_data = {}
            
            for entry in fhir_data.get('entry', []):
                resource = entry.get('resource', {})
                resource_type = resource.get('resourceType')
                
                if resource_type == 'Patient':
                    patient_id = resource.get('id', '')
                    patients_data[patient_id] = {
                        'patient': resource,
                        'conditions': [],
                        'observations': []
                    }
                elif resource_type == 'Condition':
                    patient_ref = resource.get('subject', {}).get('reference', '')
                    patient_id = patient_ref.split('/')[-1] if '/' in patient_ref else ''
                    if patient_id in patients_data:
                        patients_data[patient_id]['conditions'].append(resource)
                elif resource_type == 'Observation':
                    patient_ref = resource.get('subject', {}).get('reference', '')
                    patient_id = patient_ref.split('/')[-1] if '/' in patient_ref else ''
                    if patient_id in patients_data:
                        patients_data[patient_id]['observations'].append(resource)
            
            # Process each patient
            for fhir_patient_id, data in patients_data.items():
                try:
                    patient_resource = data['patient']
                    
                    # Generate new person_id
                    last_person = Person.objects.all().order_by('-person_id').first()
                    person_id = last_person.person_id + 1 if last_person else 1000
                    
                    # Extract name
                    first_name = ''
                    last_name = ''
                    if patient_resource.get('name'):
                        name = patient_resource['name'][0]
                        if name.get('given'):
                            first_name = name['given'][0]
                        if name.get('family'):
                            last_name = name['family']
                    
                    # Parse birth date
                    birth_date = None
                    year_of_birth = datetime.now().year - 50
                    if patient_resource.get('birthDate'):
                        birth_date = datetime.strptime(patient_resource['birthDate'], '%Y-%m-%d').date()
                        year_of_birth = birth_date.year
                    
                    # Extract phone
                    phone_number = ''
                    for telecom in patient_resource.get('telecom', []):
                        if telecom.get('system') == 'phone':
                            phone_number = telecom.get('value', '')
                            break
                    
                    # Create Person
                    person = Person.objects.create(
                        person_id=person_id,
                        year_of_birth=year_of_birth,
                        gender_concept=None,
                        race_concept=None,
                        ethnicity_concept=None,
                    )
                    
                    # Create User for the name
                    try:
                        User.objects.create(
                            id=person_id,
                            username=f"patient_{person_id}",
                            first_name=first_name,
                            last_name=last_name,
                        )
                    except Exception as e:
                        # If User creation fails (duplicate id), continue anyway
                        pass
                    
                    # Extract disease, stage, and histologic type from Condition
                    disease = 'Breast Cancer'
                    stage = ''
                    histologic_type = ''
                    condition_date = None
                    
                    for condition in data['conditions']:
                        # Get histologic type from code
                        code = condition.get('code', {})
                        if code.get('text'):
                            histologic_type = code['text']
                        elif code.get('coding') and len(code['coding']) > 0:
                            histologic_type = code['coding'][0].get('display', '')
                        
                        # Get stage
                        stages = condition.get('stage', [])
                        if stages and len(stages) > 0:
                            stage_summary = stages[0].get('summary', {})
                            if stage_summary.get('text'):
                                # Extract just the stage part (e.g., "Breast Cancer Stage II" -> "II")
                                stage_text = stage_summary['text']
                                if 'Stage' in stage_text:
                                    stage = stage_text.split('Stage')[-1].strip()
                            elif stage_summary.get('coding') and len(stage_summary['coding']) > 0:
                                stage = stage_summary['coding'][0].get('code', '')
                        
                        # Get condition onset date
                        if condition.get('onsetDateTime'):
                            try:
                                condition_date = datetime.strptime(condition['onsetDateTime'], '%Y-%m-%d')
                            except ValueError:
                                pass
                        
                        # Try to get histologic type from note if not in code
                        if not histologic_type and condition.get('note'):
                            for note in condition['note']:
                                note_text = note.get('text', '')
                                if 'Histologic type:' in note_text:
                                    histologic_type = note_text.split('Histologic type:')[-1].strip()
                    
                    # Find the most recent observation date
                    most_recent_date = condition_date
                    for observation in data['observations']:
                        if observation.get('effectiveDateTime'):
                            try:
                                obs_date = datetime.strptime(observation['effectiveDateTime'], '%Y-%m-%d')
                                if most_recent_date is None or obs_date > most_recent_date:
                                    most_recent_date = obs_date
                            except ValueError:
                                pass
                    
                    # Create PatientInfo
                    patient_info = PatientInfo.objects.create(
                        person=person,
                        phone_number=phone_number,
                        date_of_birth=birth_date,
                        disease=disease,
                        stage=stage,
                        histologic_type=histologic_type,
                    )
                    
                    # Update timestamps if we have a date
                    if most_recent_date:
                        PatientInfo.objects.filter(id=patient_info.id).update(
                            created_at=most_recent_date,
                            updated_at=most_recent_date
                        )
                    
                    created_count += 1
                    
                except Exception as e:
                    errors.append(f"Patient {fhir_patient_id}: {str(e)}")
            
            return Response({
                'success': True,
                'created_count': created_count,
                'errors': errors
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'])
    def update_patient(self, request, pk=None):
        """Update a specific patient's info"""
        try:
            person = Person.objects.get(person_id=pk)
            patient_info = PatientInfo.objects.get(person=person)
            
            serializer = self.get_serializer(patient_info, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response(serializer.data)
        except Person.DoesNotExist:
            return Response({'error': 'Person not found'}, status=status.HTTP_404_NOT_FOUND)
        except PatientInfo.DoesNotExist:
            return Response({'error': 'Patient info not found'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['delete'])
    def bulk_delete(self, request):
        """Delete multiple patients by person_ids"""
        person_ids = request.data.get('person_ids', [])
        
        if not person_ids:
            return Response({'error': 'No person_ids provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            deleted_count = 0
            errors = []
            
            for person_id in person_ids:
                try:
                    person = Person.objects.get(person_id=person_id)
                    # Delete PatientInfo
                    PatientInfo.objects.filter(person=person).delete()
                    # Delete associated User if exists
                    try:
                        User.objects.filter(id=person_id).delete()
                    except User.DoesNotExist:
                        pass
                    # Delete Person
                    person.delete()
                    deleted_count += 1
                except Person.DoesNotExist:
                    errors.append(f"Person {person_id} not found")
                except Exception as e:
                    errors.append(f"Person {person_id}: {str(e)}")
            
            return Response({
                'success': True,
                'deleted_count': deleted_count,
                'errors': errors
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    """Logout the user and clear session"""
    logout(request)
    return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)

@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for monitoring"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'ctomop',
        'database': 'connected'
    })