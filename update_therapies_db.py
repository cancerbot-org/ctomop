import os
import django
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ctomop.settings")
django.setup()

from omop_core.models import PatientInfo

FIRST_LINE = [
    'Watchful Waiting (Active Surveillance)', 'Lumpectomy (Lumpectomy)', 'Mastectomy (Mastectomy)',
    'Aromatase Inhibitor (Aromatase Inhibitor)', 'Trastuzumab (Herceptin) (Trastuzumab)',
    'Pertuzumab (Perjeta) (Pertuzumab)', 'Genomic Testing (Genomic Testing)', 'Tamoxifen (Tamoxifen)',
    'Letrozole (Letrozole)', 'Anastrozole (Arimidex) (Anastrozole)', 'Exemestane (Exemestane)',
    'Lumpectomy + Radiation (Lumpectomy, Ipsilateral Breast Radiation, Adjuvant Radiotherapy)',
    'Mastectomy + Radiation (Mastectomy, Ipsilateral Breast Radiation, Adjuvant Radiotherapy)',
    'Axillary LND + Lumpectomy + Radiation (Lumpectomy, Axillary Lymph Node Dissection (ALND), Ipsilateral Breast Radiation, Adjuvant Radiotherapy)',
    'Axillary LND + Mastectomy (Mastectomy, Axillary Lymph Node Dissection (ALND))',
    'Axillary LND + Mastectomy + Radiation (Mastectomy, Axillary Lymph Node Dissection (ALND), Ipsilateral Breast Radiation, Adjuvant Radiotherapy)'
]

SECOND_LINE = [
    'Fulvestrant (Faslodex) (Fulvestrant)', 'Exemestane + Everolimus (Exemestane, Everolimus)',
    'Atezolizumab (Atezolizumab)', 'Sacituzumab Govitecan (Sacituzumab Govitecan)',
    'Platinum-Based Chemotherapy (Platinum-Based Chemotherapy)', 'PARP Inhibitor (PARP Inhibitor)',
    'Other Chemotherapy (Other Chemotherapy)', 'Capivasertib (Capivasertib)',
    'Axillary LND + Lumpectomy + Radiation (Lumpectomy, Axillary Lymph Node Dissection (ALND), Ipsilateral Breast Radiation, Adjuvant Radiotherapy)',
    'Axillary LND + Mastectomy (Mastectomy, Axillary Lymph Node Dissection (ALND))',
    'Axillary LND + Mastectomy + Radiation (Mastectomy, Axillary Lymph Node Dissection (ALND), Ipsilateral Breast Radiation, Adjuvant Radiotherapy)'
]

LATER_LINES = [
    'Fulvestrant (Faslodex) (Fulvestrant)', 'Exemestane + Everolimus (Exemestane, Everolimus)',
    'Sacituzumab Govitecan (Sacituzumab Govitecan)', 'Alpelisib + Fulvestrant (Alpelisib, Fulvestrant)',
    'Capivasertib + Fulvestrant (Fulvestrant, Capivasertib)', 'Elacestrant (Elacestrant)',
    'Tamoxifen (Tamoxifen)', 'Megestrol acetate (Megestrol acetate)', 'Capecitabine (Capecitabine)',
    'Eribulin (Eribulin)', 'Vinorelbine (Vinorelbine)', 'Gemcitabine (Gemcitabine)',
    'Paclitaxel (Paclitaxel)', 'Docetaxel (Docetaxel)', 'Trastuzumab deruxtecan (T-DXd / Enhertu) (Trastuzumab Deruxtecan)',
    'Tucatinib + Trastuzumab + Capecitabine (Trastuzumab, Capecitabine, Tucatinib)', 'Lapatinib (Tykerb) (Lapatinib)',
    'Neratinib (Nerlynx) (Neratinib)', 'Trastuzumab emtansine (T-DM1 / Kadcyla) (Trastuzumab Emtansine)',
    'Atezolizumab + Nab-Paclitaxel (Atezolizumab, Nab-Paclitaxel)', 'Pembrolizumab + Chemotherapy (Pembrolizumab)',
    'Olaparib (Olaparib)', 'Talazoparib (Talazoparib)', 'Carboplatin (Carboplatin)', 'Cisplatin (Cisplatin)',
    'Alpelisib (Piqray) Monotherapy (Alpelisib)', 'Capivasertib (Capivasertib)', 'Larotrectinib (Larotrectinib)',
    'Entrectinib (Entrectinib)', 'Liposomal Doxorubicin (Doxorubicin)',
    'Axillary LND + Radiation (Axillary Lymph Node Dissection (ALND), Ipsilateral Breast Radiation)',
    'Axillary LND + Mastectomy (Mastectomy, Axillary Lymph Node Dissection (ALND))',
    'Axillary LND + Mastectomy + Radiation (Mastectomy, Axillary Lymph Node Dissection (ALND), Ipsilateral Breast Radiation, Adjuvant Radiotherapy)'
]

PLANNED = [
    'No planned therapy', 'Surgery', 'breast-conserving surgery (lumpectomy)', 'mastectomy',
    'axillary lymph node dissection', 'Neoadjuvant Chemotherapy', 'Neoadjuvant Anthracycline-based Chemotherapy',
    'Neoadjuvant Taxane-based Chemotherapy', 'Neoadjuvant Platinum-based Chemotherapy',
    'Neoadjuvant Endocrine/Hormonal Therapy', 'Neoadjuvant Aromatase inhibitors (e.g., letrozole, anastrozole)',
    'Neoadjuvant Tamoxifen', 'Neoadjuvant Ovarian suppression (e.g., goserelin)', 'Neoadjuvant HER2-Targeted Therapy',
    'Neoadjuvant Trastuzumab (Herceptin)', 'Neoadjuvant Pertuzumab (Perjeta)', 'Neoadjuvant Trastuzumab emtansine (T-DM1)',
    'Neoadjuvant Immunotherapy', 'Neoadjuvant Checkpoint inhibitors (e.g., pembrolizumab, atezolizumab)',
    'Neoadjuvant Radiotherapy', 'Neoadjuvant External beam radiation therapy', 'Neoadjuvant Targeted intraoperative radiotherapy',
    'Adjuvant Chemotherapy', 'Adjuvant Endocrine/Hormonal Therapy', 'Adjuvant HER2-Targeted Therapy',
    'Adjuvant trastuzumab', 'Adjuvant Radiotherapy', 'Chemotherapy', 'Anthracycline-based Chemotherapy',
    'Taxane-based Chemotherapy', 'Platinum-based Chemotherapy', 'Endocrine/Hormonal Therapy',
    'Aromatase inhibitors (e.g., letrozole, anastrozole)', 'Tamoxifen', 'Ovarian suppression (e.g., goserelin)',
    'Trastuzumab (Herceptin)', 'Pertuzumab (Perjeta)', 'Trastuzumab emtansine (T-DM1)', 'Immunotherapy',
    'Checkpoint inhibitors (experimental)', 'Radiotherapy', 'External beam radiation therapy',
    'Targeted intraoperative radiotherapy', 'Bone-Modifying Agents', 'Bisphosphonates (e.g., zoledronic acid)',
    'Denosumab', 'Targeted therapy', 'Sentinel Lymph Node Biopsy (SLNB)', 'Anti-HER2 ADCs',
    'Anti-HER2 Monoclonal Antibodies', 'HER2 Tyrosine Kinase Inhibitors'
]

updated_count = 0
for p in PatientInfo.objects.all():
    changed = False
    
    if p.first_line_therapy:
        p.first_line_therapy = random.choice(FIRST_LINE)
        changed = True
    if p.second_line_therapy:
        p.second_line_therapy = random.choice(SECOND_LINE)
        changed = True
    if p.later_therapy:
        p.later_therapy = random.choice(LATER_LINES)
        changed = True
    if p.planned_therapies:
        p.planned_therapies = random.choice(PLANNED)
        changed = True
        
    if changed:
        p.save()
        updated_count += 1

print(f"Updated {updated_count} patients with new therapy values.")
