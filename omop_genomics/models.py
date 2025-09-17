from django.db import models
from omop_core.models import Person, Concept, VisitOccurrence, Measurement

# All genomics and biomarker data should be stored in standard OMOP tables:
# - Genetic variants: Use Measurement table with appropriate LOINC/HGVS concepts
# - Biomarkers (ER, PR, HER2, PD-L1): Use Measurement table with standardized concepts  
# - Tumor assessments: Use Observation table with appropriate response concepts
# - Specimen information: Use standard OMOP Specimen table if available, or Measurement
# This ensures full OMOP CDM compliance and interoperability
