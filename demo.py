#!/usr/bin/env python
"""
Django OMOP CTomop Demo Script

This script demonstrates the usage of the OMOP CDM, Oncology, and Genomic models
for cancer clinical trial matching applications.
"""

import os
import sys
import django
from datetime import date, datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop_project.settings')
django.setup()

# Import models
from omop_core.models import (
    Vocabulary, Domain, ConceptClass, Concept, Person, 
    VisitOccurrence, ConditionOccurrence, Measurement
)
from omop_oncology.models import (
    CancerDiagnosis, CancerTreatment, CancerBiomarker, Episode
)
from omop_genomics.models import (
    GenomicAnalysis, GenomicVariant, GenomicGene
)


def demo_basic_usage():
    """Demonstrate basic model usage"""
    print("🧬 OMOP CTomop Django Models Demo")
    print("=" * 50)
    
    # Check that models are accessible
    print("\n✅ Model Import Test:")
    print(f"- Core models: {len([x for x in dir() if 'models' in str(type(eval(x))) if hasattr(eval(x), '_meta')])}")
    print(f"- Concept model: {Concept}")
    print(f"- Person model: {Person}")
    print(f"- CancerDiagnosis model: {CancerDiagnosis}")
    print(f"- GenomicVariant model: {GenomicVariant}")
    
    # Database table count
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"\n📊 Database Tables Created: {len(tables)}")
        
        # Show some key tables
        omop_tables = [table[0] for table in tables if not table[0].startswith('django_') and not table[0].startswith('auth_')]
        print(f"- OMOP Tables: {len(omop_tables)}")
        print(f"- Sample tables: {omop_tables[:10]}...")
    
    print("\n🎯 Key Features:")
    print("- Complete OMOP CDM v6.0 implementation")
    print("- Cancer-specific oncology extension") 
    print("- Genomic data models for precision medicine")
    print("- Clinical trial matching ready")
    print("- Django admin interface included")
    
    print("\n📚 Model Categories:")
    print("- Core OMOP: Standardized clinical data")
    print("- Oncology: Cancer diagnosis, treatment, biomarkers")
    print("- Genomics: Variants, expression, pharmacogenomics")
    
    print("\n🚀 Ready for:")
    print("- Electronic Health Record integration")
    print("- Clinical trial patient matching")
    print("- Cancer research data management")
    print("- Genomic data analysis workflows")


if __name__ == "__main__":
    demo_basic_usage()