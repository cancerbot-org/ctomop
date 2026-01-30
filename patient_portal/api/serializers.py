from rest_framework import serializers
from django.contrib.auth.models import User
from omop_core.models import PatientInfo, Person
from datetime import date


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class PatientListSerializer(serializers.ModelSerializer):
    """Serializer for patient list view with key fields"""
    person_id = serializers.IntegerField(source='person.person_id', read_only=True)
    patient_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    updated_at = serializers.DateTimeField(format='%Y-%m-%d', read_only=True)
    
    class Meta:
        model = PatientInfo
        fields = [
            'person_id',
            'patient_name',
            'age',
            'disease',
            'stage',
            'updated_at',
        ]
    
    def get_patient_name(self, obj):
        # Get name from Person model (OMOP extension)
        if obj.person:
            full_name = f"{obj.person.given_name or ''} {obj.person.family_name or ''}".strip()
            return full_name if full_name else f"Patient {obj.person.person_id}"
        return f"Patient {obj.person.person_id}"
    
    def get_age(self, obj):
        if obj.date_of_birth:
            today = date.today()
            age = today.year - obj.date_of_birth.year - ((today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day))
            return age
        return None


class PatientInfoSerializer(serializers.ModelSerializer):
    person_id = serializers.IntegerField(source='person.person_id', read_only=True)
    patient_name = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    gender = serializers.SerializerMethodField()
    refractory_status = serializers.CharField(source='treatment_refractory_status', required=False, allow_null=True, allow_blank=True)
    
    class Meta:
        model = PatientInfo
        fields = '__all__'
        read_only_fields = ['person', 'created_at', 'updated_at']
    
    def get_patient_name(self, obj):
        # Get name from Person model (OMOP extension)
        if obj.person:
            full_name = f"{obj.person.given_name or ''} {obj.person.family_name or ''}".strip()
            return full_name if full_name else f"Patient {obj.person.person_id}"
        return f"Patient {obj.person.person_id}"
    
    def get_age(self, obj):
        if obj.date_of_birth:
            today = date.today()
            age = today.year - obj.date_of_birth.year - ((today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day))
            return age
        return None
    
    def get_gender(self, obj):
        if obj.person and obj.person.gender_concept:
            gender_name = obj.person.gender_concept.concept_name
            if gender_name == 'MALE':
                return 'Male'
            elif gender_name == 'FEMALE':
                return 'Female'
            else:
                return 'Other'
        return 'Unknown'
    
    def update(self, instance, validated_data):
        # Handle the refractory_status mapping
        if 'treatment_refractory_status' in validated_data:
            instance.treatment_refractory_status = validated_data.pop('treatment_refractory_status')
        return super().update(instance, validated_data)
