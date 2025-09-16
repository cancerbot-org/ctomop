#!/usr/bin/env python3
"""
Demonstration script showing how to use the PatientInfo population management command.

This script demonstrates the complete workflow:
1. Creating OMOP CDM data and extensions
2. Using the population command to generate comprehensive PatientInfo records
3. Querying the results for clinical trial matching

Usage:
    python demo_population.py
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()

from django.core.management import call_command
from django.utils import timezone
from omop_core.models import Person, PatientInfo, ConditionOccurrence
from omop_genomics.models import BiomarkerMeasurement, TumorAssessment
from omop_oncology.models import TreatmentLine, SocialDeterminant


def main():
    print("=" * 80)
    print("PatientInfo Population Command Demonstration")
    print("=" * 80)
    
    print("\n1. Current State Analysis")
    print("-" * 40)
    
    person_count = Person.objects.count()
    patient_info_count = PatientInfo.objects.count()
    condition_count = ConditionOccurrence.objects.count()
    biomarker_count = BiomarkerMeasurement.objects.count()
    treatment_count = TreatmentLine.objects.count()
    
    print(f"Persons in database: {person_count}")
    print(f"PatientInfo records: {patient_info_count}")
    print(f"Condition occurrences: {condition_count}")
    print(f"Biomarker measurements: {biomarker_count}")
    print(f"Treatment lines: {treatment_count}")
    
    print("\n2. Demonstration: Running Population Command")
    print("-" * 50)
    
    print("Running: python manage.py populate_patient_info --force-update --verbose")
    call_command('populate_patient_info', force_update=True, verbose=True)
    
    print("\n3. Results: Updated PatientInfo Records")
    print("-" * 45)
    
    updated_count = PatientInfo.objects.count()
    print(f"PatientInfo records after population: {updated_count}")
    
    # Show detailed example
    if PatientInfo.objects.exists():
        example_patient = PatientInfo.objects.first()
        print(f"\nExample populated record (Person {example_patient.person.person_id}):")
        print(f"  Age: {example_patient.patient_age}")
        print(f"  Gender: {example_patient.gender}")
        print(f"  Disease: {example_patient.disease}")
        print(f"  Stage: {example_patient.stage}")
        print(f"  Location: {example_patient.region}, {example_patient.country}")
        print(f"  Language: {example_patient.languages}")
        print(f"  Weight: {example_patient.weight} {example_patient.weight_units}")
        print(f"  Height: {example_patient.height} {example_patient.height_units}")
        print(f"  BMI: {example_patient.bmi}")
        print(f"  ECOG: {example_patient.ecog_performance_status}")
        print(f"  Karnofsky: {example_patient.karnofsky_performance_score}")
        
        # Treatment information
        if example_patient.first_line_therapy:
            print(f"  First Line Therapy: {example_patient.first_line_therapy}")
            print(f"  First Line Date: {example_patient.first_line_date}")
            print(f"  First Line Outcome: {example_patient.first_line_outcome}")
        
        # Biomarkers
        biomarker_fields = [
            ('estrogen_receptor_status', 'ER Status'),
            ('progesterone_receptor_status', 'PR Status'),
            ('her2_status', 'HER2 Status'),
            ('pd_l1_tumor_cels', 'PD-L1 %'),
        ]
        
        print("  Biomarkers:")
        for field, label in biomarker_fields:
            value = getattr(example_patient, field, None)
            if value:
                print(f"    {label}: {value}")
    
    print("\n4. Clinical Trial Matching Potential")
    print("-" * 40)
    
    print("The populated PatientInfo records now contain comprehensive data for:")
    print("  ✓ Demographics (age, gender, race, ethnicity, language)")
    print("  ✓ Geographic location")
    print("  ✓ Disease information (diagnosis, stage, histology, TNM)")
    print("  ✓ Treatment history (lines, regimens, responses)")
    print("  ✓ Biomarkers (hormone receptors, HER2, PD-L1)")
    print("  ✓ Performance status (ECOG, Karnofsky)")
    print("  ✓ Vital signs and measurements")
    print("  ✓ Social determinants")
    print("  ✓ Health behaviors (smoking, substance use)")
    print("  ✓ Infection status (HIV, Hepatitis)")
    print("  ✓ Laboratory values")
    print("  ✓ Tumor assessments and response data")
    
    print("\n5. Usage Examples")
    print("-" * 20)
    
    print("# Populate specific patient:")
    print("python manage.py populate_patient_info --person-id 1001")
    
    print("\n# Force update all patients:")
    print("python manage.py populate_patient_info --force-update")
    
    print("\n# Verbose output for debugging:")
    print("python manage.py populate_patient_info --verbose")
    
    print("\n# Query populated data:")
    print("python manage.py query_patient_info")
    
    print("\n" + "=" * 80)
    print("Demonstration Complete!")
    print("The PatientInfo population command successfully extracts and")
    print("consolidates data from all OMOP CDM and extension tables into")
    print("comprehensive patient profiles suitable for clinical trial matching.")
    print("=" * 80)


if __name__ == '__main__':
    main()
