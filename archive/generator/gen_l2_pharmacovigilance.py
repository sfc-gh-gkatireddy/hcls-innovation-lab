"""
L2 Pharmacovigilance Signal Detection — Synthetic Data Generator
Generates: products.csv, ae_cases.csv, case_narratives.csv
Schema modeled on FDA FAERS (hcls-pharma-dsafety-pharmacovigilance skill)
"""
import csv
import os
import random
from datetime import date, timedelta

SEED = 42
random.seed(SEED)
OUT = os.path.join(os.path.dirname(__file__), '..', 'tracks', 'l2_pharmacovigilance', 'data')
os.makedirs(OUT, exist_ok=True)

def uid(prefix, i):
    return f"{prefix}-{i:05d}"

def pick(lst):
    return random.choice(lst)

def date_between(start, end):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(0, delta)))

def write_csv(path, rows):
    if not rows:
        return
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

# --- products ---
PRODUCTS = [
    ('PROD-01','Cardivex','Metoprolol Succinate','Cardiovascular','Beta blocker for hypertension and heart failure'),
    ('PROD-02','Gluconorm','Metformin HCl','Endocrine','Biguanide for type 2 diabetes'),
    ('PROD-03','Relivex','Adalimumab','Autoimmune','TNF-alpha inhibitor for rheumatoid arthritis'),
    ('PROD-04','Osteovance','Denosumab','Musculoskeletal','RANK ligand inhibitor for osteoporosis'),
    ('PROD-05','Neurozan','Levetiracetam','Neurology','Anti-epileptic for seizure disorders'),
    ('PROD-06','Oncoshield','Pembrolizumab','Oncology','PD-1 checkpoint inhibitor'),
    ('PROD-07','Respirex','Fluticasone/Salmeterol','Respiratory','Combination ICS/LABA inhaler'),
    ('PROD-08','Lipitrex','Atorvastatin','Cardiovascular','HMG-CoA reductase inhibitor'),
    ('PROD-09','Immunex-B','Rituximab','Oncology/Autoimmune','Anti-CD20 monoclonal antibody'),
    ('PROD-10','Thyrovex','Levothyroxine','Endocrine','Thyroid hormone replacement'),
]

# MedDRA-style preferred terms grouped by SOC
PT_BY_SOC = {
    'Gastrointestinal': ['Nausea','Vomiting','Diarrhoea','Abdominal pain','Constipation','Dyspepsia'],
    'General': ['Fatigue','Pyrexia','Malaise','Oedema peripheral','Asthenia','Chills'],
    'Skin': ['Rash','Pruritus','Urticaria','Alopecia','Dermatitis','Injection site reaction'],
    'Nervous system': ['Headache','Dizziness','Tremor','Paraesthesia','Somnolence','Syncope'],
    'Musculoskeletal': ['Arthralgia','Myalgia','Back pain','Muscle spasm','Osteonecrosis of jaw'],
    'Hepatobiliary': ['Hepatotoxicity','Hepatitis','Jaundice','Liver enzyme increased','Hepatic failure'],
    'Cardiac': ['Tachycardia','Bradycardia','Palpitations','Atrial fibrillation','QT prolongation'],
    'Immune system': ['Anaphylactic reaction','Hypersensitivity','Angioedema','Serum sickness'],
    'Infections': ['Pneumonia','Upper respiratory tract infection','Urinary tract infection','Sepsis'],
    'Blood': ['Neutropenia','Thrombocytopenia','Anaemia','Pancytopenia','Febrile neutropenia'],
}

OUTCOMES = {
    'DE': 'Death', 'LT': 'Life-Threatening', 'HO': 'Hospitalization',
    'DS': 'Disability', 'CA': 'Congenital Anomaly', 'RI': 'Required Intervention', 'OT': 'Other Serious',
}

REPORTER_TYPES = ['Physician','Pharmacist','Nurse','Consumer','Health Professional','Manufacturer']
COUNTRIES = ['US','US','US','US','GB','DE','FR','JP','CA','AU','IN','BR']
ROUTES = ['Oral','Intravenous','Subcutaneous','Inhalation','Topical','Intramuscular']
SEXES = ['M','F']
ROLE_CODES = {'PS': 'Primary Suspect', 'SS': 'Secondary Suspect', 'C': 'Concomitant'}

# --- planted signal ---
# PROD-04 (Osteovance/Denosumab) will have an emerging hepatotoxicity signal in recent quarters
# This is the pattern teams should discover: unexpected liver events for a bone drug
SIGNAL_PRODUCT = 'PROD-04'
SIGNAL_PTS = ['Hepatotoxicity','Hepatitis','Liver enzyme increased','Hepatic failure']
SIGNAL_START = date(2026, 4, 1)  # signal emerges in Q2 2026

def gen_products():
    rows = [{'PRODUCT_ID': p[0], 'PRODUCT_NAME': p[1], 'ACTIVE_INGREDIENT': p[2],
             'THERAPEUTIC_AREA': p[3], 'DESCRIPTION': p[4]} for p in PRODUCTS]
    write_csv(os.path.join(OUT, 'products.csv'), rows)

def gen_cases(n=5000):
    cases = []
    narratives = []

    for i in range(n):
        case_id = uid('AE', i+1)
        product = pick(PRODUCTS)
        prod_id = product[0]
        prod_name = product[1]
        active = product[2]
        therapeutic = product[3]

        report_date = date_between(date(2025, 1, 1), date(2026, 9, 30))
        age = random.randint(18, 92)
        sex = pick(SEXES)
        country = pick(COUNTRIES)
        reporter = pick(REPORTER_TYPES)
        route = pick(ROUTES)

        # pick adverse event
        if prod_id == SIGNAL_PRODUCT and report_date >= SIGNAL_START and random.random() < 0.35:
            pt = pick(SIGNAL_PTS)
            soc = 'Hepatobiliary'
        else:
            soc = pick(list(PT_BY_SOC.keys()))
            pt = pick(PT_BY_SOC[soc])

        # seriousness
        serious_pts = {'Hepatotoxicity','Hepatic failure','Anaphylactic reaction','Sepsis','Syncope',
                       'Pancytopenia','Febrile neutropenia','Osteonecrosis of jaw','QT prolongation',
                       'Neutropenia','Death'}
        is_serious = pt in serious_pts or random.random() < 0.2
        if pt in ('Hepatic failure','Sepsis','Pancytopenia') and random.random() < 0.15:
            outcome = 'DE'
        elif is_serious:
            outcome = pick(['LT','HO','HO','HO','DS','RI'])
        else:
            outcome = 'OT'

        event_date = report_date - timedelta(days=random.randint(1, 60))

        cases.append({
            'CASE_ID': case_id,
            'PRODUCT_ID': prod_id,
            'PRODUCT_NAME': prod_name,
            'ACTIVE_INGREDIENT': active,
            'DRUG_ROLE': 'PS' if random.random() < 0.85 else pick(['SS','C']),
            'ROUTE_OF_ADMIN': route,
            'REPORT_DATE': report_date.isoformat(),
            'EVENT_DATE': event_date.isoformat(),
            'PREFERRED_TERM': pt,
            'SOC': soc,
            'SERIOUSNESS': 'Serious' if is_serious else 'Non-Serious',
            'OUTCOME_CODE': outcome,
            'OUTCOME_DESCRIPTION': OUTCOMES[outcome],
            'PATIENT_AGE': age,
            'PATIENT_SEX': sex,
            'REPORTER_TYPE': reporter,
            'REPORTER_COUNTRY': country,
            'REPORT_QUARTER': f"{report_date.year}Q{(report_date.month-1)//3+1}",
        })

        # generate narrative for ~8% of cases (400 total target)
        if random.random() < 0.08 or (prod_id == SIGNAL_PRODUCT and soc == 'Hepatobiliary'):
            narrative = gen_narrative(case_id, prod_name, active, pt, soc, age, sex, event_date,
                                      outcome, route, reporter)
            narratives.append({
                'CASE_ID': case_id,
                'NARRATIVE_TYPE': pick(['REPORTER','MANUFACTURER']),
                'NARRATIVE_TEXT': narrative,
            })

    write_csv(os.path.join(OUT, 'ae_cases.csv'), cases)
    write_csv(os.path.join(OUT, 'case_narratives.csv'), narratives)
    return cases, narratives

def gen_narrative(case_id, prod_name, active, pt, soc, age, sex, event_date, outcome, route, reporter):
    sex_word = 'male' if sex == 'M' else 'female'
    outcome_phrase = {
        'DE': 'The patient subsequently expired.',
        'LT': 'The event was considered life-threatening.',
        'HO': f'The patient was hospitalized on {event_date.isoformat()}.',
        'DS': 'The event resulted in persistent disability.',
        'RI': 'Medical intervention was required to prevent permanent damage.',
        'OT': 'The event resolved without sequelae.',
    }

    if soc == 'Hepatobiliary':
        templates = [
            f"A {age}-year-old {sex_word} patient was treated with {prod_name} ({active}) via {route.lower()} route. "
            f"Approximately {random.randint(2,16)} weeks after initiation, the patient presented with {pt.lower()}. "
            f"Laboratory findings showed ALT {random.randint(150,800)} U/L (normal <40), AST {random.randint(120,600)} U/L, "
            f"total bilirubin {round(random.uniform(1.5,8.0),1)} mg/dL. "
            f"{prod_name} was discontinued. {outcome_phrase[outcome]} "
            f"The reporter ({reporter.lower()}) considered the event possibly related to {prod_name}. "
            f"No prior history of liver disease was reported.",

            f"This case was reported by a {reporter.lower()} regarding a {age}-year-old {sex_word} who developed "
            f"{pt.lower()} during treatment with {prod_name}. The patient had been on therapy for "
            f"{random.randint(1,12)} months. Liver function tests were markedly elevated. "
            f"The drug was stopped and supportive care was initiated. {outcome_phrase[outcome]} "
            f"Causality assessment: possible. Dechallenge: positive (enzymes trended down after discontinuation).",
        ]
    else:
        templates = [
            f"A {age}-year-old {sex_word} patient experienced {pt.lower()} while receiving {prod_name} "
            f"({active}) via {route.lower()} route for {random.randint(1,24)} months. "
            f"The event occurred on {event_date.isoformat()}. {outcome_phrase[outcome]} "
            f"The {reporter.lower()} assessed causality as {'probable' if random.random() < 0.3 else 'possible'}.",

            f"Spontaneous report from a {reporter.lower()}: {age}-year-old {sex_word}, "
            f"treated with {prod_name} ({active}), developed {pt.lower()}. "
            f"Onset was approximately {random.randint(3,90)} days after starting therapy. "
            f"{outcome_phrase[outcome]} No relevant medical history reported.",

            f"Case involves a {age}-year-old {sex_word} patient on {prod_name} who presented with {pt.lower()}. "
            f"The attending {reporter.lower()} reported the event on {event_date.isoformat()}. "
            f"Treatment with {prod_name} was {'discontinued' if random.random() < 0.6 else 'continued with dose reduction'}. "
            f"{outcome_phrase[outcome]}",
        ]

    return pick(templates)

if __name__ == '__main__':
    print("Generating L2 Pharmacovigilance data...")
    gen_products()
    cases, narratives = gen_cases(5000)
    signal_cases = [c for c in cases if c['PRODUCT_ID'] == SIGNAL_PRODUCT and c['SOC'] == 'Hepatobiliary']
    print(f"  Products: {len(PRODUCTS)}")
    print(f"  AE cases: {len(cases)}")
    print(f"  Case narratives: {len(narratives)}")
    print(f"  Planted signal (PROD-04 hepatobiliary): {len(signal_cases)} cases")
    print(f"  Output: {OUT}")
