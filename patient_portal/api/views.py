from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth.models import User
from django.contrib.auth import logout, login, authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from omop_core.models import Person, PatientInfo, Concept
from datetime import datetime
import csv
import json
from io import StringIO
from .serializers import (
    UserSerializer, PatientInfoSerializer, PatientListSerializer
)
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods


def get_gender_concept(gender_str):
    """Map gender string to OMOP gender concept"""
    if not gender_str:
        return None
    
    gender_map = {
        'male': 8507,
        'm': 8507,
        'female': 8532,
        'f': 8532,
        'unknown': 8551,
        'other': 8551,
        'ambiguous': 8570,
    }
    
    gender_lower = gender_str.lower().strip()
    concept_id = gender_map.get(gender_lower)
    
    if concept_id:
        try:
            return Concept.objects.get(concept_id=concept_id)
        except Concept.DoesNotExist:
            return None
    return None

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
    
    def update(self, request, pk=None, partial=False):
        """Update patient info for a specific person"""
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
    
    def partial_update(self, request, pk=None):
        """Partial update (PATCH) for patient info"""
        return self.update(request, pk, partial=True)
    
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
                    
                    # Get gender concept
                    gender_concept = get_gender_concept(row.get('gender', ''))
                    gender_source = row.get('gender', 'unknown')
                    
                    person, created = Person.objects.get_or_create(
                        person_id=person_id,
                        defaults={
                            'year_of_birth': int(row.get('year_of_birth', datetime.now().year - 50)),
                            'gender_concept': gender_concept,
                            'gender_source_value': gender_source,
                            'race_concept': None,
                            'race_source_value': 'unknown',
                            'ethnicity_concept': None,
                            'ethnicity_source_value': 'unknown',
                            'person_source_value': f"CSV-{person_id}",
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
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    @method_decorator(csrf_exempt)
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
                        'observations': [],
                        'medications': []
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
                elif resource_type == 'MedicationStatement':
                    patient_ref = resource.get('subject', {}).get('reference', '')
                    patient_id = patient_ref.split('/')[-1] if '/' in patient_ref else ''
                    if patient_id in patients_data:
                        patients_data[patient_id]['medications'].append(resource)
            
            # Process each patient
            for fhir_patient_id, data in patients_data.items():
                try:
                    patient_resource = data['patient']
                    
                    # Generate new person_id
                    last_person = Person.objects.all().order_by('-person_id').first()
                    person_id = last_person.person_id + 1 if last_person else 1000
                    
                    # Parse birth date
                    birth_date = None
                    year_of_birth = None
                    month_of_birth = None
                    day_of_birth = None
                    
                    if patient_resource.get('birthDate'):
                        birth_date = datetime.strptime(patient_resource['birthDate'], '%Y-%m-%d').date()
                        year_of_birth = birth_date.year
                        month_of_birth = birth_date.month
                        day_of_birth = birth_date.day
                    
                    # Extract address information from FHIR
                    country = None
                    region = None
                    city = None
                    postal_code = None
                    
                    if patient_resource.get('address') and len(patient_resource['address']) > 0:
                        address = patient_resource['address'][0]
                        country = address.get('country')
                        region = address.get('state')
                        city = address.get('city')
                        postal_code = address.get('postalCode')
                    
                    # Extract ethnicity and vital signs from extensions
                    ethnicity = None
                    weight = None
                    height = None
                    systolic_bp = None
                    diastolic_bp = None
                    heart_rate = None
                    ecog = None
                    
                    if patient_resource.get('extension'):
                        for ext in patient_resource['extension']:
                            url = ext.get('url', '')
                            if 'ethnicity' in url:
                                ethnicity = ext.get('valueString')
                            elif 'bodyWeight' in url:
                                weight = ext.get('valueQuantity', {}).get('value')
                            elif 'bodyHeight' in url:
                                height = ext.get('valueQuantity', {}).get('value')
                            elif 'systolic-bp' in url:
                                systolic_bp = ext.get('valueQuantity', {}).get('value')
                            elif 'diastolic-bp' in url:
                                diastolic_bp = ext.get('valueQuantity', {}).get('value')
                            elif 'heartRate' in url:
                                heart_rate = ext.get('valueQuantity', {}).get('value')
                            elif 'ecog-performance-status' in url:
                                ecog = ext.get('valueInteger')
                    
                    # Get gender concept from FHIR
                    gender_concept = get_gender_concept(patient_resource.get('gender', ''))
                    
                    # Extract name from FHIR
                    name = patient_resource.get('name', [{}])[0] if patient_resource.get('name') else {}
                    given_name = ' '.join(name.get('given', [])) if name.get('given') else ''
                    family_name = name.get('family', '')
                    
                    # Create Person with OMOP-compliant birth date fields and names
                    person = Person.objects.create(
                        person_id=person_id,
                        gender_concept=gender_concept,
                        year_of_birth=year_of_birth or datetime.now().year - 50,
                        month_of_birth=month_of_birth,
                        day_of_birth=day_of_birth,
                        ethnicity_concept=None,
                        given_name=given_name,
                        family_name=family_name,
                    )
                    
                    # Create User for authentication (optional, not used for display)
                    User.objects.create(
                        id=person.person_id,
                        username=f'patient{person.person_id}',
                        first_name=given_name,
                        last_name=family_name,
                    )
                    
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
                    
                    # Create ConditionOccurrence for the diagnosis
                    if condition_date:
                        from omop_core.models import ConditionOccurrence
                        last_condition = ConditionOccurrence.objects.all().order_by('-condition_occurrence_id').first()
                        condition_id = last_condition.condition_occurrence_id + 1 if last_condition else 1
                        
                        # Get breast cancer concept (using a standard concept ID)
                        breast_cancer_concept = None
                        try:
                            breast_cancer_concept = Concept.objects.filter(
                                concept_name__icontains='breast cancer'
                            ).first()
                        except:
                            pass
                        
                        if breast_cancer_concept:
                            # Get EHR type concept (32817 = EHR)
                            type_concept = Concept.objects.filter(concept_id=32817).first()
                            if not type_concept:
                                type_concept = breast_cancer_concept
                            
                            ConditionOccurrence.objects.create(
                                condition_occurrence_id=condition_id,
                                person=person,
                                condition_concept=breast_cancer_concept,
                                condition_start_date=condition_date.date(),
                                condition_start_datetime=condition_date,
                                condition_type_concept=type_concept,
                                condition_source_value=disease
                            )
                    
                    # Process observations and create Measurement records
                    from omop_core.models import Measurement
                    last_measurement = Measurement.objects.all().order_by('-measurement_id').first()
                    measurement_id = last_measurement.measurement_id + 1 if last_measurement else 1
                    
                    # Extract tumor characteristics from observations
                    tumor_size = None
                    lymph_node_status = None
                    metastasis_status = None
                    er_status = None
                    pr_status = None
                    her2_status = None
                    ki67_index = None
                    pdl1_status = None
                    pdl1_percentage = None
                    genetic_mutations = []
                    
                    for observation in data['observations']:
                        obs_code = observation.get('code', {})
                        obs_text = obs_code.get('text', '').lower()
                        
                        # Check for tumor size
                        if 'tumor size' in obs_text or 'size tumor' in obs_text:
                            if observation.get('valueQuantity'):
                                tumor_size = observation['valueQuantity'].get('value')
                        
                        # Check for lymph node status
                        elif 'lymph node' in obs_text or 'lymph nodes' in obs_text:
                            if observation.get('valueCodeableConcept'):
                                value_concept = observation['valueCodeableConcept']
                                if value_concept.get('text'):
                                    lymph_node_status = value_concept['text']
                                elif value_concept.get('coding'):
                                    lymph_node_status = value_concept['coding'][0].get('display')
                        
                        # Check for metastasis status
                        elif 'metastasis' in obs_text or 'metastases' in obs_text:
                            if observation.get('valueCodeableConcept'):
                                value_concept = observation['valueCodeableConcept']
                                if value_concept.get('text'):
                                    metastasis_status = value_concept['text']
                                elif value_concept.get('coding'):
                                    metastasis_status = value_concept['coding'][0].get('display')
                        
                        # Check for ER status
                        elif 'estrogen receptor' in obs_text or obs_text == 'er':
                            if observation.get('valueCodeableConcept'):
                                value_concept = observation['valueCodeableConcept']
                                if value_concept.get('text'):
                                    er_status = value_concept['text']
                                elif value_concept.get('coding'):
                                    er_status = value_concept['coding'][0].get('display')
                        
                        # Check for PR status
                        elif 'progesterone receptor' in obs_text or obs_text == 'pr':
                            if observation.get('valueCodeableConcept'):
                                value_concept = observation['valueCodeableConcept']
                                if value_concept.get('text'):
                                    pr_status = value_concept['text']
                                elif value_concept.get('coding'):
                                    pr_status = value_concept['coding'][0].get('display')
                        
                        # Check for HER2 status
                        elif 'her2' in obs_text or 'her-2' in obs_text:
                            if observation.get('valueCodeableConcept'):
                                value_concept = observation['valueCodeableConcept']
                                if value_concept.get('text'):
                                    her2_status = value_concept['text']
                                elif value_concept.get('coding'):
                                    her2_status = value_concept['coding'][0].get('display')
                        
                        # Check for Ki67
                        elif 'ki67' in obs_text or 'ki-67' in obs_text:
                            if observation.get('valueQuantity'):
                                ki67_index = observation['valueQuantity'].get('value')
                        
                        # Check for PD-L1
                        elif 'pd-l1' in obs_text or 'pdl1' in obs_text:
                            if observation.get('valueCodeableConcept'):
                                value_concept = observation['valueCodeableConcept']
                                if value_concept.get('text'):
                                    pdl1_status = value_concept['text']
                                elif value_concept.get('coding'):
                                    pdl1_status = value_concept['coding'][0].get('display')
                            # Check for PD-L1 percentage in component
                            if observation.get('component'):
                                for component in observation['component']:
                                    comp_text = component.get('code', {}).get('text', '').lower()
                                    if 'percentage' in comp_text or 'tumor cells' in comp_text:
                                        if component.get('valueQuantity'):
                                            pdl1_percentage = component['valueQuantity'].get('value')
                        
                        # Check for genetic mutations (component-based observations)
                        elif 'gene' in obs_text and 'mutation' in obs_text:
                            mutation_data = {
                                'gene': None,
                                'mutation': None,
                                'origin': None,
                                'interpretation': None
                            }
                            
                            # Get interpretation from main valueCodeableConcept
                            if observation.get('valueCodeableConcept'):
                                value_concept = observation['valueCodeableConcept']
                                if value_concept.get('text'):
                                    mutation_data['interpretation'] = value_concept['text']
                                elif value_concept.get('coding'):
                                    mutation_data['interpretation'] = value_concept['coding'][0].get('display')
                            
                            # Extract gene, mutation, and origin from components
                            if observation.get('component'):
                                for component in observation['component']:
                                    comp_code = component.get('code', {})
                                    comp_text = comp_code.get('text', '').lower()
                                    
                                    if 'gene' in comp_text:
                                        if component.get('valueCodeableConcept'):
                                            mutation_data['gene'] = component['valueCodeableConcept'].get('text')
                                    elif 'mutation' in comp_text or 'dna change' in comp_text:
                                        if component.get('valueCodeableConcept'):
                                            mutation_data['mutation'] = component['valueCodeableConcept'].get('text')
                                    elif 'origin' in comp_text or 'source class' in comp_text:
                                        if component.get('valueCodeableConcept'):
                                            value = component['valueCodeableConcept'].get('text')
                                            if value:
                                                mutation_data['origin'] = value
                                            elif component['valueCodeableConcept'].get('coding'):
                                                mutation_data['origin'] = component['valueCodeableConcept']['coding'][0].get('display')
                            
                            # Only add if we have at least gene and mutation
                            if mutation_data['gene'] and mutation_data['mutation']:
                                genetic_mutations.append(mutation_data)
                    
                    for observation in data['observations']:
                        obs_date = None
                        if observation.get('effectiveDateTime'):
                            try:
                                obs_date = datetime.strptime(observation['effectiveDateTime'], '%Y-%m-%d')
                            except ValueError:
                                continue
                        
                        if not obs_date:
                            continue
                        
                        # Get observation name and value
                        obs_code = observation.get('code', {})
                        obs_name = obs_code.get('text', '')
                        if not obs_name and obs_code.get('coding'):
                            obs_name = obs_code['coding'][0].get('display', '')
                        
                        # Get value
                        value_number = None
                        value_string = None
                        unit = None
                        
                        if observation.get('valueQuantity'):
                            value_qty = observation['valueQuantity']
                            value_number = value_qty.get('value')
                            unit = value_qty.get('unit')
                        elif observation.get('valueCodeableConcept'):
                            value_concept = observation['valueCodeableConcept']
                            if value_concept.get('text'):
                                value_string = value_concept['text']
                            elif value_concept.get('coding'):
                                value_string = value_concept['coding'][0].get('display')
                        
                        # Find or create measurement concept
                        measurement_concept = None
                        try:
                            measurement_concept = Concept.objects.filter(
                                concept_name__icontains=obs_name[:50]
                            ).first()
                        except:
                            pass
                        
                        if not measurement_concept:
                            # Use a generic lab test concept if not found
                            measurement_concept = Concept.objects.filter(concept_id=3000963).first()
                        
                        if measurement_concept:
                            # Get Lab type concept (32856 = Lab)
                            type_concept = Concept.objects.filter(concept_id=32856).first()
                            if not type_concept:
                                type_concept = measurement_concept
                            
                            Measurement.objects.create(
                                measurement_id=measurement_id,
                                person=person,
                                measurement_concept=measurement_concept,
                                measurement_date=obs_date.date(),
                                measurement_datetime=obs_date,
                                measurement_type_concept=type_concept,
                                value_as_number=value_number,
                                value_as_string=value_string,
                                measurement_source_value=obs_name[:50],
                                unit_source_value=unit[:50] if unit else None
                            )
                            measurement_id += 1
                    
                    # Extract therapy information from MedicationStatement resources
                    therapy_lines = {}  # {line_number: {'regimen': name, 'date': date, 'outcome': outcome}}
                    
                    for medication in data.get('medications', []):
                        # Get therapy line from extension
                        therapy_line = None
                        therapy_outcome = None
                        
                        for ext in medication.get('extension', []):
                            if 'therapy-line' in ext.get('url', ''):
                                therapy_line = ext.get('valueInteger')
                            elif 'therapy-outcome' in ext.get('url', ''):
                                therapy_outcome = ext.get('valueString')
                        
                        if therapy_line is None:
                            continue
                        
                        # Check if this is a regimen (parent) or individual drug (partOf)
                        if not medication.get('partOf'):
                            # This is the named regimen
                            regimen_name = medication.get('medicationCodeableConcept', {}).get('text', '')
                            start_date = medication.get('effectivePeriod', {}).get('start')
                            
                            if therapy_line not in therapy_lines:
                                therapy_lines[therapy_line] = {
                                    'regimen': regimen_name,
                                    'date': start_date,
                                    'outcome': therapy_outcome
                                }
                            else:
                                therapy_lines[therapy_line]['regimen'] = regimen_name
                                therapy_lines[therapy_line]['outcome'] = therapy_outcome
                    
                    # Map therapy lines to first/second/later fields
                    first_line_therapy = None
                    first_line_date = None
                    first_line_outcome = None
                    second_line_therapy = None
                    second_line_date = None
                    second_line_outcome = None
                    later_therapy = None
                    later_date = None
                    later_outcome = None
                    
                    if 1 in therapy_lines:
                        first_line_therapy = therapy_lines[1]['regimen']
                        if therapy_lines[1]['date']:
                            try:
                                first_line_date = datetime.strptime(therapy_lines[1]['date'], '%Y-%m-%d').date()
                            except:
                                pass
                        first_line_outcome = therapy_lines[1]['outcome']
                    
                    if 2 in therapy_lines:
                        second_line_therapy = therapy_lines[2]['regimen']
                        if therapy_lines[2]['date']:
                            try:
                                second_line_date = datetime.strptime(therapy_lines[2]['date'], '%Y-%m-%d').date()
                            except:
                                pass
                        second_line_outcome = therapy_lines[2]['outcome']
                    
                    # Map line 3 and 4 to "later" field (prioritize most recent)
                    if 4 in therapy_lines:
                        later_therapy = therapy_lines[4]['regimen']
                        if therapy_lines[4]['date']:
                            try:
                                later_date = datetime.strptime(therapy_lines[4]['date'], '%Y-%m-%d').date()
                            except:
                                pass
                        later_outcome = therapy_lines[4]['outcome']
                    elif 3 in therapy_lines:
                        later_therapy = therapy_lines[3]['regimen']
                        if therapy_lines[3]['date']:
                            try:
                                later_date = datetime.strptime(therapy_lines[3]['date'], '%Y-%m-%d').date()
                            except:
                                pass
                        later_outcome = therapy_lines[3]['outcome']
                    
                    # Create PatientInfo with address, ethnicity, vital signs, and therapy
                    patient_info = PatientInfo.objects.create(
                        person=person,
                        date_of_birth=birth_date,
                        disease=disease,
                        stage=stage,
                        histologic_type=histologic_type,
                        country=country,
                        region=region,
                        city=city,
                        postal_code=postal_code,
                        ethnicity=ethnicity,
                        weight=weight,
                        weight_units='kg' if weight else None,
                        height=height,
                        height_units='cm' if height else None,
                        systolic_blood_pressure=systolic_bp,
                        diastolic_blood_pressure=diastolic_bp,
                        heartrate=heart_rate,
                        ecog_performance_status=ecog,
                        tumor_size=tumor_size,
                        lymph_node_status=lymph_node_status,
                        metastasis_status=metastasis_status,
                        estrogen_receptor_status=er_status,
                        progesterone_receptor_status=pr_status,
                        her2_status=her2_status,
                        ki67_proliferation_index=ki67_index,
                        pd_l1_tumor_cels=pdl1_percentage,
                        genetic_mutations=genetic_mutations,
                        first_line_therapy=first_line_therapy,
                        first_line_date=first_line_date,
                        first_line_outcome=first_line_outcome,
                        second_line_therapy=second_line_therapy,
                        second_line_date=second_line_date,
                        second_line_outcome=second_line_outcome,
                        later_therapy=later_therapy,
                        later_date=later_date,
                        later_outcome=later_outcome,
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
def login_view(request):
    """Simple login with username and password"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({
            'error': 'Username and password required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        user_serializer = UserSerializer(user)
        return Response({
            'message': 'Login successful',
            'user': user_serializer.data
        }, status=status.HTTP_200_OK)
    else:
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

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