"""
Create synthetic OMOP CDM records for local testing.

Creates Person, Location, Concept, ConditionOccurrence, Measurement,
Observation, DrugExposure, and Episode records for patients across the
4 supported diseases (MM, FL, BC, CLL).

After running this, derive PatientInfo with:
    python manage.py populate_patient_info --force-update
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from datetime import date, datetime

from omop_core.models import (
    Concept, Person, Location, ConditionOccurrence, Measurement,
    Observation, DrugExposure, Vocabulary, Domain, ConceptClass,
)
from omop_oncology.models import Episode


# ── Auto-incrementing ID counters ──────────────────────────────────────
_id_counters = {}


def _next_id(table, start=5001):
    _id_counters.setdefault(table, start)
    val = _id_counters[table]
    _id_counters[table] += 1
    return val


class Command(BaseCommand):
    help = (
        'Create synthetic OMOP CDM records for 4 cancer patients '
        '(MM, FL, BC, CLL). Run populate_patient_info afterwards.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Delete ALL existing OMOP records before seeding.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self._clear()

        self._ensure_vocab_infra()

        persons = [
            self._create_mm_patient(),
            self._create_fl_patient(),
            self._create_bc_patient(),
            self._create_cll_patient(),
        ]

        self.stdout.write(self.style.SUCCESS(
            f'Created {len(persons)} patients with OMOP records.\n'
            f'Now run:  python manage.py populate_patient_info --force-update'
        ))

    # ── Infrastructure ─────────────────────────────────────────────────

    def _clear(self):
        for model in [Observation, Measurement, DrugExposure,
                      ConditionOccurrence, Episode, Person, Location, Concept,
                      ConceptClass, Domain, Vocabulary]:
            model.objects.all().delete()
        self.stdout.write('Cleared existing data.')

    def _ensure_vocab_infra(self):
        Vocabulary.objects.get_or_create(
            vocabulary_id='None',
            defaults={'vocabulary_name': 'OMOP Standardized Vocabularies',
                      'vocabulary_concept_id': 44819096})
        Vocabulary.objects.get_or_create(
            vocabulary_id='SNOMED',
            defaults={'vocabulary_name': 'SNOMED CT',
                      'vocabulary_reference': 'http://www.snomed.org/',
                      'vocabulary_concept_id': 0})
        Vocabulary.objects.get_or_create(
            vocabulary_id='LOINC',
            defaults={'vocabulary_name': 'Logical Observation Identifiers',
                      'vocabulary_concept_id': 0})
        Domain.objects.get_or_create(
            domain_id='Condition',
            defaults={'domain_name': 'Condition', 'domain_concept_id': 19})
        Domain.objects.get_or_create(
            domain_id='Measurement',
            defaults={'domain_name': 'Measurement', 'domain_concept_id': 21})
        Domain.objects.get_or_create(
            domain_id='Observation',
            defaults={'domain_name': 'Observation', 'domain_concept_id': 27})
        Domain.objects.get_or_create(
            domain_id='Drug',
            defaults={'domain_name': 'Drug', 'domain_concept_id': 13})
        Domain.objects.get_or_create(
            domain_id='General',
            defaults={'domain_name': 'General', 'domain_concept_id': 0})
        ConceptClass.objects.get_or_create(
            concept_class_id='Clinical Finding',
            defaults={'concept_class_name': 'Clinical Finding',
                      'concept_class_concept_id': 44819234})
        ConceptClass.objects.get_or_create(
            concept_class_id='General',
            defaults={'concept_class_name': 'General',
                      'concept_class_concept_id': 0})

    def _concept(self, concept_id, name, domain_id='General',
                 vocabulary_id='SNOMED', concept_class_id='General'):
        c, _ = Concept.objects.get_or_create(
            concept_id=concept_id,
            defaults={
                'concept_name': name,
                'domain_id': domain_id,
                'vocabulary_id': vocabulary_id,
                'concept_class_id': concept_class_id,
                'standard_concept': 'S',
                'concept_code': str(concept_id),
                'valid_start_date': date(2000, 1, 1),
                'valid_end_date': date(2099, 12, 31),
            })
        return c

    def _measurement(self, person, concept, mdate, value,
                     unit_source=None, value_as_string=None):
        type_concept = self._concept(44818701, 'From physical examination')
        return Measurement.objects.create(
            measurement_id=_next_id('measurement'),
            person=person,
            measurement_concept=concept,
            measurement_date=mdate,
            measurement_type_concept=type_concept,
            value_as_number=Decimal(str(value)) if value is not None else None,
            value_as_string=value_as_string,
            unit_source_value=unit_source,
        )

    def _observation(self, person, concept, odate,
                     value_as_number=None, value_as_string=None):
        type_concept = self._concept(38000280, 'Observation recorded from EHR')
        return Observation.objects.create(
            observation_id=_next_id('observation'),
            person=person,
            observation_concept=concept,
            observation_date=odate,
            observation_type_concept=type_concept,
            value_as_number=Decimal(str(value_as_number)) if value_as_number is not None else None,
            value_as_string=value_as_string,
        )

    def _condition(self, person, concept, start_date, source_value=None):
        type_concept = self._concept(32020, 'EHR')
        return ConditionOccurrence.objects.create(
            condition_occurrence_id=_next_id('condition'),
            person=person,
            condition_concept=concept,
            condition_start_date=start_date,
            condition_start_datetime=timezone.make_aware(
                datetime.combine(start_date, datetime.min.time())),
            condition_type_concept=type_concept,
            condition_source_value=source_value,
        )

    def _drug(self, person, concept, start_date, end_date, source_value=None):
        type_concept = self._concept(32838, 'EHR dispensing')
        return DrugExposure.objects.create(
            drug_exposure_id=_next_id('drug'),
            person=person,
            drug_concept=concept,
            drug_exposure_start_date=start_date,
            drug_exposure_end_date=end_date,
            drug_type_concept=type_concept,
            drug_source_value=source_value,
        )

    def _person(self, person_id, year_of_birth, gender_label, gender_concept_id,
                location=None):
        gender_concept = self._concept(gender_concept_id, gender_label)
        person, _ = Person.objects.get_or_create(
            person_id=person_id,
            defaults={
                'gender_concept': gender_concept,
                'gender_source_value': gender_label,
                'year_of_birth': year_of_birth,
            })
        return person

    # ── Shared lab concepts (created once, reused) ─────────────────────

    def _lab_concepts(self):
        """Return a dict of commonly used LOINC measurement concepts."""
        if hasattr(self, '_labs'):
            return self._labs
        self._labs = {
            'weight': self._concept(3025315, 'Body weight', 'Measurement', 'LOINC'),
            'height': self._concept(3036277, 'Body height', 'Measurement', 'LOINC'),
            'systolic': self._concept(3004249, 'Systolic BP', 'Measurement', 'LOINC'),
            'diastolic': self._concept(3012888, 'Diastolic BP', 'Measurement', 'LOINC'),
            'hemoglobin': self._concept(3000963, 'Hemoglobin', 'Measurement', 'LOINC'),
            'platelet': self._concept(3024929, 'Platelet count', 'Measurement', 'LOINC'),
            'wbc': self._concept(3010813, 'WBC count', 'Measurement', 'LOINC'),
            'creatinine': self._concept(3016723, 'Serum creatinine', 'Measurement', 'LOINC'),
            'calcium': self._concept(3006906, 'Serum calcium', 'Measurement', 'LOINC'),
            'alc': self._concept(3019897, 'Absolute lymphocyte count', 'Measurement', 'LOINC'),
            'beta2m': self._concept(3001582, 'Beta-2 microglobulin', 'Measurement', 'LOINC'),
            'ldh': self._concept(3003458, 'LDH', 'Measurement', 'LOINC'),
            'albumin': self._concept(3024561, 'Albumin', 'Measurement', 'LOINC'),
            'ast': self._concept(3013721, 'AST', 'Measurement', 'LOINC'),
            'alt': self._concept(3006923, 'ALT', 'Measurement', 'LOINC'),
            'bilirubin_total': self._concept(3024128, 'Total bilirubin', 'Measurement', 'LOINC'),
            'kappa_flc': self._concept(3016407, 'Kappa FLC', 'Measurement', 'LOINC'),
            'lambda_flc': self._concept(3001668, 'Lambda FLC', 'Measurement', 'LOINC'),
            'ecog': self._concept(3005629, 'ECOG performance status', 'Observation', 'LOINC'),
        }
        return self._labs

    def _common_vitals(self, person, d, weight, height, systolic, diastolic):
        labs = self._lab_concepts()
        self._measurement(person, labs['weight'], d, weight, 'kg')
        self._measurement(person, labs['height'], d, height, 'cm')
        self._measurement(person, labs['systolic'], d, systolic, 'mmHg')
        self._measurement(person, labs['diastolic'], d, diastolic, 'mmHg')

    # ── Patient: Multiple Myeloma ──────────────────────────────────────

    def _create_mm_patient(self):
        person = self._person(8001, 1958, 'Male', 8507)
        d = date(2024, 6, 1)
        labs = self._lab_concepts()

        # Diagnosis
        self._condition(person,
                        self._concept(4228429, 'Multiple myeloma'),
                        date(2024, 1, 10), 'C90.0')

        # Vitals
        self._common_vitals(person, d, 82.5, 178, 132, 78)

        # Labs
        self._measurement(person, labs['hemoglobin'], d, 10.2, 'g/dL')
        self._measurement(person, labs['creatinine'], d, 1.4, 'mg/dL')
        self._measurement(person, labs['calcium'], d, 10.8, 'mg/dL')
        self._measurement(person, labs['platelet'], d, 165000, 'cells/uL')
        self._measurement(person, labs['wbc'], d, 5200, 'cells/L')
        self._measurement(person, labs['albumin'], d, 3.2, 'g/dL')
        self._measurement(person, labs['ldh'], d, 280)
        self._measurement(person, labs['kappa_flc'], d, 185)
        self._measurement(person, labs['lambda_flc'], d, 12)
        self._measurement(person, labs['ast'], d, 28, 'U/L')
        self._measurement(person, labs['alt'], d, 22, 'U/L')
        self._measurement(person, labs['bilirubin_total'], d, 0.8, 'mg/dL')

        # ECOG
        self._observation(person, labs['ecog'], d, value_as_number=1)

        # Treatment: VRd first line
        vrd = self._concept(4300901, 'Bortezomib + Lenalidomide + Dexamethasone')
        self._drug(person, vrd, date(2024, 2, 1), date(2024, 8, 1),
                   'VRd')

        self.stdout.write(f'  person_id=8001  [multiple myeloma]  born=1958')
        return person

    # ── Patient: Follicular Lymphoma ───────────────────────────────────

    def _create_fl_patient(self):
        person = self._person(8002, 1965, 'Female', 8532)
        d = date(2024, 5, 15)
        labs = self._lab_concepts()

        self._condition(person,
                        self._concept(4103534, 'Follicular lymphoma'),
                        date(2024, 3, 1), 'C82.10')

        self._common_vitals(person, d, 68.0, 165, 118, 72)

        self._measurement(person, labs['hemoglobin'], d, 11.8, 'g/dL')
        self._measurement(person, labs['platelet'], d, 210000, 'cells/uL')
        self._measurement(person, labs['wbc'], d, 6100, 'cells/L')
        self._measurement(person, labs['creatinine'], d, 0.9, 'mg/dL')
        self._measurement(person, labs['ldh'], d, 320)
        self._measurement(person, labs['albumin'], d, 3.8, 'g/dL')
        self._measurement(person, labs['ast'], d, 25, 'U/L')
        self._measurement(person, labs['alt'], d, 20, 'U/L')
        self._measurement(person, labs['bilirubin_total'], d, 0.6, 'mg/dL')

        self._observation(person, labs['ecog'], d, value_as_number=1)

        # FLIPI score
        flipi_concept = self._concept(3005800, 'FLIPI score', 'Observation', 'LOINC')
        self._observation(person, flipi_concept, d, value_as_number=3,
                          value_as_string='Intermediate')

        # Tumor grade
        tumor_grade_concept = self._concept(3005801, 'Tumor grade', 'Observation')
        self._observation(person, tumor_grade_concept, d, value_as_number=2)

        # Treatment: R-CHOP
        rchop = self._concept(4301001, 'Rituximab + CHOP')
        self._drug(person, rchop, date(2024, 4, 1), date(2024, 9, 1), 'R-CHOP')

        self.stdout.write(f'  person_id=8002  [follicular lymphoma]  born=1965')
        return person

    # ── Patient: Breast Cancer ─────────────────────────────────────────

    def _create_bc_patient(self):
        person = self._person(8003, 1977, 'Female', 8532)
        d = date(2024, 7, 10)
        labs = self._lab_concepts()

        self._condition(person,
                        self._concept(4112853, 'Breast cancer'),
                        date(2024, 4, 20), 'C50.9')

        self._common_vitals(person, d, 64.0, 162, 122, 76)

        self._measurement(person, labs['hemoglobin'], d, 12.5, 'g/dL')
        self._measurement(person, labs['platelet'], d, 245000, 'cells/uL')
        self._measurement(person, labs['wbc'], d, 7200, 'cells/L')
        self._measurement(person, labs['creatinine'], d, 0.8, 'mg/dL')
        self._measurement(person, labs['albumin'], d, 4.1, 'g/dL')
        self._measurement(person, labs['ast'], d, 22, 'U/L')
        self._measurement(person, labs['alt'], d, 18, 'U/L')
        self._measurement(person, labs['bilirubin_total'], d, 0.5, 'mg/dL')

        self._observation(person, labs['ecog'], d, value_as_number=0)

        # Biomarkers as Observations
        er_concept = self._concept(3006238, 'ER status', 'Observation')
        self._observation(person, er_concept, d, value_as_string='Negative')

        pr_concept = self._concept(3006239, 'PR status', 'Observation')
        self._observation(person, pr_concept, d, value_as_string='Negative')

        her2_concept = self._concept(3006240, 'HER2 status', 'Observation')
        self._observation(person, her2_concept, d, value_as_string='Negative')

        # Ki-67
        ki67_concept = self._concept(3006241, 'Ki-67 index', 'Measurement', 'LOINC')
        self._measurement(person, ki67_concept, d, 42, '%')

        # Treatment: AC-T
        act = self._concept(4301002, 'Doxorubicin + Cyclophosphamide + Paclitaxel')
        self._drug(person, act, date(2024, 5, 15), date(2024, 10, 15), 'AC-T')

        self.stdout.write(f'  person_id=8003  [breast cancer]  born=1977')
        return person

    # ── Patient: CLL ───────────────────────────────────────────────────

    def _create_cll_patient(self):
        person = self._person(8004, 1952, 'Male', 8507)
        d = date(2024, 8, 1)
        labs = self._lab_concepts()

        self._condition(person,
                        self._concept(4177242, 'Chronic lymphocytic leukemia'),
                        date(2023, 6, 15), 'C91.10')

        self._common_vitals(person, d, 90.0, 175, 140, 82)

        self._measurement(person, labs['hemoglobin'], d, 11.0, 'g/dL')
        self._measurement(person, labs['platelet'], d, 135000, 'cells/uL')
        self._measurement(person, labs['wbc'], d, 45000, 'cells/L')
        self._measurement(person, labs['creatinine'], d, 1.1, 'mg/dL')
        self._measurement(person, labs['alc'], d, 38000)
        self._measurement(person, labs['beta2m'], d, 4.2, 'mg/L')
        self._measurement(person, labs['albumin'], d, 3.5, 'g/dL')
        self._measurement(person, labs['ast'], d, 30, 'U/L')
        self._measurement(person, labs['alt'], d, 26, 'U/L')
        self._measurement(person, labs['bilirubin_total'], d, 0.9, 'mg/dL')
        self._measurement(person, labs['ldh'], d, 310)

        # Second ALC measurement (3 months later) for doubling time calc
        self._measurement(person, labs['alc'], date(2024, 11, 1), 52000)

        self._observation(person, labs['ecog'], d, value_as_number=1)

        # Binet stage
        binet_concept = self._concept(3005802, 'Binet stage', 'Observation')
        self._observation(person, binet_concept, d, value_as_string='B')

        # Splenomegaly
        spleno_concept = self._concept(3005803, 'Splenomegaly', 'Observation')
        self._observation(person, spleno_concept, d, value_as_string='Yes')

        # Lymphadenopathy
        lymph_concept = self._concept(3005804, 'Lymphadenopathy', 'Observation')
        self._observation(person, lymph_concept, d, value_as_string='Yes')

        # Treatment: Ibrutinib (BTK inhibitor)
        ibrutinib = self._concept(4301003, 'Ibrutinib')
        self._drug(person, ibrutinib, date(2023, 9, 1), date(2024, 6, 1),
                   'Ibrutinib')

        self.stdout.write(f'  person_id=8004  [CLL]  born=1952')
        return person
