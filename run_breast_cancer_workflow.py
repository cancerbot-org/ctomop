"""
Complete workflow script to generate synthetic breast cancer patients and populate PatientInfo

This script demonstrates the complete workflow:
1. Generate 100 synthetic breast cancer patients (50 TNBC, 50 non-TNBC)
2. Load them into OMOP CDM tables
3. Extract data into PatientInfo for clinical trial matching
4. Query and analyze the results

Usage:
    python run_breast_cancer_workflow.py
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()

from django.core.management import call_command
from omop_core.models import Person, PatientInfo
import json


def run_complete_workflow():
    """Run the complete workflow for breast cancer patient generation and analysis"""
    
    print("🚀 Starting Breast Cancer Patient Generation Workflow")
    print("=" * 60)
    
    # Step 1: Generate synthetic patients
    print("\n📊 Step 1: Generating 100 synthetic breast cancer patients...")
    try:
        call_command(
            'generate_breast_cancer_patients',
            count=100,
            tnbc_ratio=0.5,
            seed=42
        )
        print("✅ Successfully generated synthetic patients")
    except Exception as e:
        print(f"❌ Error generating patients: {e}")
        return False
    
    # Step 2: Populate PatientInfo from OMOP tables
    print("\n🔄 Step 2: Populating PatientInfo from OMOP tables...")
    try:
        call_command(
            'populate_patient_info',
            force_update=True,
            verbose=True
        )
        print("✅ Successfully populated PatientInfo records")
    except Exception as e:
        print(f"❌ Error populating PatientInfo: {e}")
        return False
    
    # Step 3: Analyze results
    print("\n📈 Step 3: Analyzing generated data...")
    analyze_generated_data()
    
    # Step 4: Clinical trial matching examples
    print("\n🎯 Step 4: Clinical trial matching examples...")
    demonstrate_clinical_trial_matching()
    
    print("\n✅ Workflow completed successfully!")
    return True


def analyze_generated_data():
    """Analyze the generated patient data"""
    
    # Count total patients
    total_patients = PatientInfo.objects.count()
    print(f"📊 Total PatientInfo records: {total_patients}")
    
    # Analyze TNBC vs non-TNBC
    tnbc_patients = PatientInfo.objects.filter(tnbc_status=True).count()
    non_tnbc_patients = PatientInfo.objects.filter(tnbc_status=False).count()
    
    print(f"🎗️  TNBC patients: {tnbc_patients}")
    print(f"🎗️  Non-TNBC patients: {non_tnbc_patients}")
    
    # Analyze genetic mutations
    patients_with_mutations = PatientInfo.objects.exclude(genetic_mutations=[]).count()
    print(f"🧬 Patients with genetic mutations: {patients_with_mutations}")
    
    # Sample genetic mutations
    mutation_examples = PatientInfo.objects.exclude(genetic_mutations=[])[:3]
    for i, patient in enumerate(mutation_examples, 1):
        print(f"\n🧬 Example {i} - Patient {patient.person.person_id} mutations:")
        for mutation in patient.genetic_mutations:
            print(f"   - {mutation.get('gene', 'unknown')}: {mutation.get('variant', 'unknown')} "
                  f"({mutation.get('origin', 'unknown')}, {mutation.get('interpretation', 'unknown')})")
    
    # Biomarker analysis
    er_positive = PatientInfo.objects.filter(estrogen_receptor_status='Positive').count()
    pr_positive = PatientInfo.objects.filter(progesterone_receptor_status='Positive').count()
    her2_positive = PatientInfo.objects.filter(her2_status='Positive').count()
    
    print(f"\n🔬 Biomarker Status:")
    print(f"   ER+: {er_positive}")
    print(f"   PR+: {pr_positive}")
    print(f"   HER2+: {her2_positive}")


def demonstrate_clinical_trial_matching():
    """Demonstrate clinical trial matching queries with genetic mutations."""
    print("\n🔍 Clinical Trial Matching Examples:")
    
    # Note: SQLite doesn't support JSONField contains lookup, so we use icontains for basic matching
    
    print("\n🎯 Trial 1: TNBC patients with BRCA mutations")
    try:
        # For SQLite, use icontains to search for gene names in the JSON string
        tnbc_brca_patients = PatientInfo.objects.filter(
            tnbc_status=True,
            genetic_mutations__icontains='brca'
        )
        print(f"   Eligible patients: {tnbc_brca_patients.count()}")
        
        # Show first few patients
        for patient in tnbc_brca_patients[:3]:
            print(f"   - Patient {patient.person_id}: {len(patient.genetic_mutations or [])} mutations")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n🎯 Trial 2: Patients with pathogenic mutations")
    try:
        pathogenic_patients = PatientInfo.objects.filter(
            genetic_mutations__icontains='pathogenic'
        )
        print(f"   Eligible patients: {pathogenic_patients.count()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n🎯 Trial 3: Patients with germline mutations")
    try:
        germline_patients = PatientInfo.objects.filter(
            genetic_mutations__icontains='germline'
        )
        print(f"   Eligible patients: {germline_patients.count()}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n🎯 Trial 4: ER+ patients (hormone therapy eligible)")
    try:
        er_positive_patients = PatientInfo.objects.filter(er_status=True)
        print(f"   Eligible patients: {er_positive_patients.count()}")
    except Exception as e:
        print(f"   Error: {e}")
        
    # Show sample genetic mutations from a few patients
    print("\n🧬 Sample genetic mutations:")
    patients_with_mutations = PatientInfo.objects.exclude(genetic_mutations__isnull=True).exclude(genetic_mutations__exact=[])[:3]
    for patient in patients_with_mutations:
        print(f"   Patient {patient.person_id}:")
        for mutation in (patient.genetic_mutations or []):
            print(f"     - {mutation.get('gene', 'Unknown')}: {mutation.get('variant', 'Unknown')} ({mutation.get('interpretation', 'Unknown')})")
    
    if not patients_with_mutations:
        print("   No patients with genetic mutations found")
        # Let's check what we do have
        all_patients = PatientInfo.objects.all()[:5]
        print(f"\n📊 Sample of {all_patients.count()} patients:")
        for patient in all_patients:
            print(f"   - Patient {patient.person_id}: TNBC={patient.tnbc_status}, ER={patient.er_status}, mutations={len(patient.genetic_mutations or [])}")


def main():
    """Main function to run the workflow"""
    
    print("🧬 Breast Cancer OMOP CDM Data Generation & Analysis")
    print("=" * 60)
    print("This script will:")
    print("1. Generate 100 synthetic breast cancer patients")
    print("2. Store data in OMOP CDM tables")
    print("3. Extract to PatientInfo for clinical trial matching")
    print("4. Demonstrate clinical trial matching queries")
    print("=" * 60)
    
    # Confirm before proceeding
    response = input("\nProceed with data generation? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("Workflow cancelled.")
        return
    
    # Run the workflow
    success = run_complete_workflow()
    
    if success:
        print("\n🎉 All steps completed successfully!")
        print("\nNext steps:")
        print("1. Review the generated data in the Django admin")
        print("2. Run additional clinical trial matching queries")
        print("3. Export data for external analysis")
    else:
        print("\n❌ Workflow failed. Check the error messages above.")


if __name__ == "__main__":
    main()
