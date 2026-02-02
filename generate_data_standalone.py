#!/usr/bin/env python3
"""
Standalone script to generate FHIR data without Django setup issues
"""
import sys
import os

# Set database to SQLite to avoid PostgreSQL dependency
os.environ.pop('DATABASE_URL', None)
os.environ['DJANGO_SETTINGS_MODULE'] = 'ctomop.settings'

# Setup Django
import django
django.setup()

# Now import and run the command
from omop_core.management.commands.generate_fhir_bundle import Command

if __name__ == '__main__':
    command = Command()
    command.handle(count=100, output='data/synthetic_patients_100.json', seed=42, verbosity=1)
    print("\n✓ Generated data/synthetic_patients_100.json with supportive and planned therapies")

