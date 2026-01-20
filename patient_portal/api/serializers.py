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
        # Get user associated with this person
        try:
            user = User.objects.get(id=obj.person.person_id)
            full_name = f"{user.first_name} {user.last_name}".strip()
            return full_name if full_name else user.username
        except User.DoesNotExist:
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
    
    class Meta:
        model = PatientInfo
        fields = '__all__'
        read_only_fields = ['person', 'created_at', 'updated_at']
    
    def get_patient_name(self, obj):
        try:
            user = User.objects.get(id=obj.person.person_id)
            full_name = f"{user.first_name} {user.last_name}".strip()
            return full_name if full_name else user.username
        except User.DoesNotExist:
            return f"Patient {obj.person.person_id}"
    
    def get_age(self, obj):
        if obj.date_of_birth:
            today = date.today()
            age = today.year - obj.date_of_birth.year - ((today.month, today.day) < (obj.date_of_birth.month, obj.date_of_birth.day))
            return age
        return None
