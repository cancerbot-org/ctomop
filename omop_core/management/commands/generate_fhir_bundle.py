"""
Generate comprehensive FHIR Bundle JSON with breast cancer patient data

This command creates a FHIR Bundle including:
- Patient demographics with US addresses
- Breast cancer diagnoses with stage and histologic type
- Lab values (CBC, liver, kidney function)
- Biomarkers (HER2, ER, PR status)
- Genetic mutations (BRCA1, BRCA2, TP53, PIK3CA, etc.)
- Prior lines of therapy (chemotherapy, targeted therapy)

Usage:
    python manage.py generate_fhir_bundle --count 200 --output data/patients.json
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Generate comprehensive FHIR Bundle with breast cancer patient data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=200,
            help='Number of patients to generate (default: 200)',
        )
        parser.add_argument(
            '--output',
            type=str,
            default='data/synthetic_patients_fhir.json',
            help='Output file path (default: data/synthetic_patients_fhir.json)',
        )
        parser.add_argument(
            '--seed',
            type=int,
            default=42,
            help='Random seed for reproducibility (default: 42)',
        )

    def handle(self, *args, **options):
        count = options['count']
        output_path = options['output']
        seed = options['seed']
        
        random.seed(seed)
        
        self.stdout.write('Generating comprehensive FHIR Bundle with breast cancer patients...')
        
        bundle = self.generate_bundle(count)
        
        # Save to file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(bundle, f, indent=2)
        
        self.stdout.write(self.style.SUCCESS(f'✓ Generated FHIR Bundle with {count} patients'))
        self.stdout.write(self.style.SUCCESS(f'✓ Saved to: {output_file}'))
        self.stdout.write(self.style.SUCCESS(f'✓ Total resources: {len(bundle["entry"])}'))
        self.stdout.write(self.style.SUCCESS('✓ Each patient includes:'))
        self.stdout.write('  - Demographics with US address')
        self.stdout.write('  - Breast cancer diagnosis with stage and histologic type')
        self.stdout.write('  - Lab values (CBC, liver, kidney function)')
        self.stdout.write('  - Biomarkers (HER2, ER, PR status)')
        self.stdout.write('  - Genetic mutations (BRCA1, BRCA2, TP53, PIK3CA, etc.)')
        self.stdout.write('  - Prior lines of therapy (chemotherapy, targeted therapy)')

    def generate_bundle(self, num_patients):
        """Generate FHIR Bundle with all resources"""
        bundle = {
            "resourceType": "Bundle",
            "type": "collection",
            "entry": []
        }
        
        for i in range(1, num_patients + 1):
            first_name = random.choice(self.get_first_names())
            last_name = random.choice(self.get_last_names())
            
            # Generate patient
            patient = self.generate_patient(i, first_name, last_name)
            bundle["entry"].append({
                "fullUrl": f"http://example.org/Patient/{i}",
                "resource": patient
            })
            
            birth_date = datetime.strptime(patient['birthDate'], '%Y-%m-%d')
            diagnosis_date = self.generate_diagnosis_date(birth_date)
            
            # Generate condition with stage and histologic type
            condition = self.generate_condition(i, diagnosis_date)
            bundle["entry"].append({
                "fullUrl": f"http://example.org/Condition/condition-{i}",
                "resource": condition
            })
            
            # Generate lab observations
            lab_date = datetime.now() - timedelta(days=random.randint(1, 30))
            for obs in self.generate_lab_observations(i, lab_date):
                bundle["entry"].append(obs)
            
            # Generate biomarker observations
            for obs in self.generate_biomarker_observations(i, diagnosis_date):
                bundle["entry"].append(obs)
            
            # Generate genetic mutation observations
            for obs in self.generate_genetic_mutations(i, diagnosis_date):
                bundle["entry"].append(obs)
            
            # Generate prior therapy (medication statements)
            for med in self.generate_prior_therapy(i, diagnosis_date):
                bundle["entry"].append(med)
        
        return bundle

    def generate_patient(self, patient_id, first_name, last_name):
        """Generate FHIR Patient resource with US address"""
        birth_date = self.generate_random_date(1950, 2005)
        
        # US locations
        us_locations = [
            ('New York', 'NY'), ('Los Angeles', 'CA'), ('Chicago', 'IL'),
            ('Houston', 'TX'), ('Boston', 'MA'), ('Miami', 'FL'),
            ('Phoenix', 'AZ'), ('Philadelphia', 'PA'), ('San Antonio', 'TX'),
            ('San Diego', 'CA'), ('Dallas', 'TX'), ('San Jose', 'CA'),
            ('Austin', 'TX'), ('Jacksonville', 'FL'), ('Fort Worth', 'TX'),
            ('Columbus', 'OH'), ('Charlotte', 'NC'), ('Seattle', 'WA'),
            ('Denver', 'CO'), ('Portland', 'OR'), ('Atlanta', 'GA'),
        ]
        
        city, state = random.choice(us_locations)
        zip_code = f"{random.randint(10000, 99999)}"
        phone = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        
        return {
            "resourceType": "Patient",
            "id": str(patient_id),
            "name": [{
                "use": "official",
                "family": last_name,
                "given": [first_name]
            }],
            "gender": "female",
            "birthDate": birth_date.strftime('%Y-%m-%d'),
            "telecom": [{
                "system": "phone",
                "value": phone,
                "use": "home"
            }],
            "address": [{
                "use": "home",
                "type": "both",
                "line": [f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Maple', 'Cedar', 'Pine'])} Street"],
                "city": city,
                "state": state,
                "postalCode": zip_code,
                "country": "United States"
            }]
        }

    def generate_condition(self, patient_id, diagnosis_date):
        """Generate breast cancer condition with stage and histologic type"""
        histologic_types = [
            "Invasive ductal carcinoma",
            "Invasive lobular carcinoma",
            "Ductal carcinoma in situ",
            "Medullary carcinoma",
            "Tubular carcinoma",
            "Mucinous carcinoma"
        ]
        
        stages = ["I", "IA", "IB", "II", "IIA", "IIB", "III", "IIIA", "IIIB", "IIIC", "IV"]
        
        histologic_type = random.choice(histologic_types)
        stage = random.choice(stages)
        
        return {
            "resourceType": "Condition",
            "id": f"condition-{patient_id}",
            "clinicalStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                    "code": "active"
                }]
            },
            "verificationStatus": {
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                    "code": "confirmed"
                }]
            },
            "category": [{
                "coding": [{
                    "system": "http://terminology.hl7.org/CodeSystem/condition-category",
                    "code": "encounter-diagnosis"
                }]
            }],
            "code": {
                "coding": [{
                    "system": "http://snomed.info/sct",
                    "code": "254837009",
                    "display": "Malignant neoplasm of breast"
                }],
                "text": histologic_type
            },
            "subject": {
                "reference": f"Patient/{patient_id}"
            },
            "onsetDateTime": diagnosis_date.strftime('%Y-%m-%d'),
            "recordedDate": diagnosis_date.strftime('%Y-%m-%d'),
            "stage": [{
                "summary": {
                    "coding": [{
                        "system": "http://cancerstaging.org",
                        "code": stage
                    }],
                    "text": f"Breast Cancer Stage {stage}"
                },
                "type": {
                    "coding": [{
                        "system": "http://snomed.info/sct",
                        "code": "260998006",
                        "display": "Clinical staging"
                    }]
                }
            }],
            "note": [{
                "text": f"Histologic type: {histologic_type}"
            }]
        }

    def generate_lab_observations(self, patient_id, lab_date):
        """Generate lab observations (CBC, liver, kidney function)"""
        observations = []
        
        labs = [
            ("hemoglobin", round(random.uniform(9.5, 15.0), 1), "g/dL", "718-7", "Hemoglobin", (12.0, 16.0)),
            ("wbc", round(random.uniform(3.5, 11.0), 1), "10*3/uL", "6690-2", "White blood cell count", (4.0, 11.0)),
            ("anc", round(random.uniform(1.5, 7.0), 1), "10*3/uL", "751-8", "Neutrophils", (1.5, 8.0)),
            ("platelets", random.randint(100, 400), "10*3/uL", "777-3", "Platelets", (150, 400)),
            ("creatinine", round(random.uniform(0.6, 1.8), 2), "mg/dL", "2160-0", "Creatinine", (0.6, 1.2)),
            ("alt", random.randint(10, 100), "U/L", "1742-6", "ALT", (7, 56)),
            ("ast", random.randint(10, 100), "U/L", "1920-8", "AST", (8, 48)),
            ("bilirubin", round(random.uniform(0.2, 2.0), 1), "mg/dL", "1975-2", "Total Bilirubin", (0.1, 1.2)),
            ("albumin", round(random.uniform(3.0, 5.0), 1), "g/dL", "1751-7", "Albumin", (3.5, 5.5)),
        ]
        
        for name, value, unit, loinc_code, display, ref_range in labs:
            obs = {
                "fullUrl": f"http://example.org/Observation/obs-{patient_id}-{name}",
                "resource": {
                    "resourceType": "Observation",
                    "id": f"obs-{patient_id}-{name}",
                    "status": "final",
                    "category": [{
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "laboratory"
                        }]
                    }],
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": loinc_code,
                            "display": display
                        }],
                        "text": display
                    },
                    "subject": {
                        "reference": f"Patient/{patient_id}"
                    },
                    "effectiveDateTime": lab_date.strftime('%Y-%m-%d'),
                    "valueQuantity": {
                        "value": value,
                        "unit": unit,
                        "system": "http://unitsofmeasure.org",
                        "code": unit
                    },
                    "referenceRange": [{
                        "low": {"value": ref_range[0], "unit": unit},
                        "high": {"value": ref_range[1], "unit": unit}
                    }]
                }
            }
            observations.append(obs)
        
        return observations

    def generate_biomarker_observations(self, patient_id, diagnosis_date):
        """Generate biomarker observations (HER2, ER, PR)"""
        observations = []
        
        # 15% chance of TNBC (all negative)
        is_tnbc = random.random() < 0.15
        
        if is_tnbc:
            her2 = "Negative"
            er = "Negative"
            pr = "Negative"
        else:
            her2 = random.choice(["Positive", "Negative", "Negative"])  # ~30% HER2+
            er = random.choice(["Positive", "Positive", "Positive", "Negative"])  # ~75% ER+
            pr = random.choice(["Positive", "Positive", "Negative"])  # ~65% PR+
        
        biomarkers = [
            ("HER2", her2, "48676-1", "HER2 receptor"),
            ("ER", er, "16112-5", "Estrogen receptor"),
            ("PR", pr, "16113-3", "Progesterone receptor"),
        ]
        
        for name, status, loinc_code, display in biomarkers:
            obs = {
                "fullUrl": f"http://example.org/Observation/obs-{patient_id}-{name}",
                "resource": {
                    "resourceType": "Observation",
                    "id": f"obs-{patient_id}-{name}",
                    "status": "final",
                    "category": [{
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "laboratory"
                        }]
                    }],
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": loinc_code,
                            "display": display
                        }],
                        "text": display
                    },
                    "subject": {
                        "reference": f"Patient/{patient_id}"
                    },
                    "effectiveDateTime": diagnosis_date.strftime('%Y-%m-%d'),
                    "valueCodeableConcept": {
                        "coding": [{
                            "system": "http://snomed.info/sct",
                            "code": "10828004" if status == "Positive" else "260385009",
                            "display": status
                        }],
                        "text": status
                    }
                }
            }
            observations.append(obs)
        
        return observations

    def generate_genetic_mutations(self, patient_id, diagnosis_date):
        """Generate genetic mutation observations"""
        observations = []
        
        # 10-15% have BRCA mutations
        has_brca = random.random() < 0.12
        
        mutations = []
        if has_brca:
            # BRCA1 or BRCA2
            mutations.append(("BRCA1" if random.random() < 0.5 else "BRCA2", "Detected"))
        
        # Other common mutations (30-40% have one or more)
        if random.random() < 0.35:
            mutations.append(("TP53", "Detected"))
        if random.random() < 0.30:
            mutations.append(("PIK3CA", "Detected"))
        if random.random() < 0.15:
            mutations.append(("PTEN", "Detected"))
        if random.random() < 0.10:
            mutations.append(("ATM", "Detected"))
        if random.random() < 0.08:
            mutations.append(("CHEK2", "Detected"))
        if random.random() < 0.05:
            mutations.append(("PALB2", "Detected"))
        
        # If no mutations, add "No significant mutations detected"
        if not mutations:
            mutations.append(("Genomic", "No significant mutations detected"))
        
        gene_loinc_codes = {
            "BRCA1": "21636-6",
            "BRCA2": "21637-4",
            "TP53": "47423-8",
            "PIK3CA": "55233-1",
            "PTEN": "48676-1",
            "ATM": "48675-3",
            "CHEK2": "48004-6",
            "PALB2": "88039-1",
            "Genomic": "81247-9"
        }
        
        for gene, status in mutations:
            loinc_code = gene_loinc_codes.get(gene, "81247-9")
            obs = {
                "fullUrl": f"http://example.org/Observation/obs-{patient_id}-{gene}",
                "resource": {
                    "resourceType": "Observation",
                    "id": f"obs-{patient_id}-{gene}",
                    "status": "final",
                    "category": [{
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/observation-category",
                            "code": "laboratory"
                        }]
                    }],
                    "code": {
                        "coding": [{
                            "system": "http://loinc.org",
                            "code": loinc_code,
                            "display": f"{gene} gene mutation"
                        }],
                        "text": f"{gene} mutation analysis"
                    },
                    "subject": {
                        "reference": f"Patient/{patient_id}"
                    },
                    "effectiveDateTime": diagnosis_date.strftime('%Y-%m-%d'),
                    "valueString": status
                }
            }
            observations.append(obs)
        
        return observations

    def generate_prior_therapy(self, patient_id, diagnosis_date):
        """Generate prior lines of therapy (MedicationStatement resources)"""
        medications = []
        
        # Number of prior lines (0-3)
        num_lines = random.choices([0, 1, 2, 3], weights=[0.2, 0.4, 0.3, 0.1])[0]
        
        therapy_options = [
            ("Doxorubicin", "3002", "Anthracycline"),
            ("Cyclophosphamide", "3007", "Alkylating agent"),
            ("Paclitaxel", "1716024", "Taxane"),
            ("Docetaxel", "72962", "Taxane"),
            ("Trastuzumab", "224905", "HER2 targeted therapy"),
            ("Pertuzumab", "1298944", "HER2 targeted therapy"),
            ("Bevacizumab", "351859", "Anti-angiogenic"),
            ("Capecitabine", "194000", "Oral chemotherapy"),
            ("Carboplatin", "40223", "Platinum agent"),
            ("Tamoxifen", "10324", "Hormonal therapy"),
            ("Letrozole", "73274", "Aromatase inhibitor"),
        ]
        
        for line_num in range(1, num_lines + 1):
            # 2-3 drugs per line
            num_drugs = random.randint(2, 3)
            line_drugs = random.sample(therapy_options, num_drugs)
            
            # Start therapy 6-18 months ago, each line 3-6 months apart
            therapy_start = diagnosis_date + timedelta(days=random.randint(30, 90) + (line_num - 1) * 120)
            therapy_end = therapy_start + timedelta(days=random.randint(90, 180))
            
            for drug_name, rxnorm_code, drug_class in line_drugs:
                med = {
                    "fullUrl": f"http://example.org/MedicationStatement/med-{patient_id}-line{line_num}-{drug_name}",
                    "resource": {
                        "resourceType": "MedicationStatement",
                        "id": f"med-{patient_id}-line{line_num}-{drug_name}",
                        "status": "completed",
                        "medicationCodeableConcept": {
                            "coding": [{
                                "system": "http://www.nlm.nih.gov/research/umls/rxnorm",
                                "code": rxnorm_code,
                                "display": drug_name
                            }],
                            "text": drug_name
                        },
                        "subject": {
                            "reference": f"Patient/{patient_id}"
                        },
                        "effectivePeriod": {
                            "start": therapy_start.strftime('%Y-%m-%d'),
                            "end": therapy_end.strftime('%Y-%m-%d')
                        },
                        "note": [{
                            "text": f"Line {line_num} therapy - {drug_class}"
                        }]
                    }
                }
                medications.append(med)
        
        return medications

    def generate_random_date(self, start_year, end_year):
        """Generate random date between years"""
        start_date = datetime(start_year, 1, 1)
        end_date = datetime(end_year, 12, 31)
        time_between = end_date - start_date
        days_between = time_between.days
        random_days = random.randrange(days_between)
        return start_date + timedelta(days=random_days)

    def generate_diagnosis_date(self, birth_date):
        """Generate diagnosis date (between age 30 and current age)"""
        today = datetime.now()
        min_diagnosis = birth_date + timedelta(days=30*365)
        max_diagnosis = min(today, birth_date + timedelta(days=80*365))
        
        if min_diagnosis >= max_diagnosis:
            return today - timedelta(days=random.randint(365, 3650))
        
        time_between = max_diagnosis - min_diagnosis
        days_between = time_between.days
        if days_between <= 0:
            return today - timedelta(days=random.randint(365, 3650))
        
        random_days = random.randrange(days_between)
        return min_diagnosis + timedelta(days=random_days)

    def get_first_names(self):
        return [
            "Emma", "Olivia", "Ava", "Isabella", "Sophia", "Mia", "Charlotte", "Amelia",
            "Harper", "Evelyn", "Abigail", "Emily", "Elizabeth", "Sofia", "Avery", "Ella",
            "Scarlett", "Grace", "Chloe", "Victoria", "Riley", "Aria", "Lily", "Aubrey",
            "Zoey", "Penelope", "Lillian", "Addison", "Layla", "Natalie", "Camila", "Hannah"
        ]

    def get_last_names(self):
        return [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
            "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White",
            "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young"
        ]
