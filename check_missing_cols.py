import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ctomop.settings')
django.setup()
from django.db import connection

with connection.cursor() as c:
    c.execute("SELECT column_name FROM information_schema.columns WHERE table_name='patient_info' ORDER BY column_name")
    existing = {r[0] for r in c.fetchall()}

migration_cols = [
    'absolute_lymphocyte_count', 'alkaline_phosphatase', 'androgen_receptor_status',
    'autoimmune_cytopenias_refractory_to_steroids', 'bcl2_inhibitor_refractory',
    'binet_stage', 'bone_marrow_involvement', 'btk_inhibitor_refractory',
    'clonal_b_lymphocyte_count', 'clonal_bone_marrow_b_lymphocytes',
    'disease_activity', 'ecog_assessment_date', 'first_line_discontinuation_reason',
    'first_line_end_date', 'first_line_intent', 'first_line_start_date',
    'flipi_score', 'flipi_score_options', 'gelf_criteria_status', 'hepatomegaly',
    'languages_skills', 'largest_lymph_node_size',
    'later_discontinuation_reason', 'later_end_date', 'later_intent', 'later_start_date',
    'later_therapies', 'ldh', 'lymphadenopathy', 'lymphocyte_doubling_time',
    'magnesium', 'measurable_disease_imwg', 'measurable_disease_iwcll',
    'oncotype_dx_score', 'phosphorus', 'pregnancy_test_date',
    'pregnancy_test_result_value', 'protein_expressions', 'qtcf_value',
    'reason_for_discontinuation', 'report_interpretation', 'richter_transformation',
    'second_line_discontinuation_reason', 'second_line_end_date',
    'second_line_intent', 'second_line_start_date', 'serum_beta2_microglobulin_level',
    'spleen_size', 'splenomegaly', 'status', 'supportive_therapy_end_date',
    'supportive_therapy_intent', 'supportive_therapy_start_date',
    'test_date', 'test_methodology', 'test_specimen_type', 'therapy_intent',
    'tp53_disruption', 'tumor_burden', 'tumor_grade',
]
missing = [col for col in migration_cols if col not in existing]
print('Missing columns:', missing)
