"""
P1 Claims Denial Triage — Synthetic Data Generator
Generates: members.csv, providers.csv, claims.csv, denial_notes.csv, payer_policies.csv
Schema modeled on sf-hcls-solutions-incubator/hcls_operations_reimagined
"""
import csv
import os
import random
import hashlib
from datetime import date, timedelta

SEED = 42
random.seed(SEED)
OUT = os.path.join(os.path.dirname(__file__), '..', 'tracks', 'p1_claims_denials', 'data')
os.makedirs(OUT, exist_ok=True)

# --- helpers ---
def uid(prefix, i):
    return f"{prefix}-{i:05d}"

def pick(lst):
    return random.choice(lst)

def date_between(start, end):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

# --- reference data ---
FIRST_NAMES = ['James','Sarah','Michael','Emily','Robert','Jessica','David','Ashley','William','Jennifer',
               'Richard','Amanda','Thomas','Stephanie','Daniel','Nicole','Matthew','Elizabeth','Andrew','Megan',
               'Christopher','Lauren','Joseph','Rachel','Charles','Samantha','Joshua','Katherine','Brian','Olivia']
LAST_NAMES = ['Mitchell','Chen','Rodriguez','Patel','Thompson','Williams','Johnson','Brown','Garcia','Martinez',
              'Anderson','Taylor','Thomas','Jackson','White','Harris','Martin','Lee','Clark','Lewis',
              'Robinson','Walker','Young','Allen','King','Wright','Scott','Green','Baker','Adams']
STATES = ['CO','TX','CA','FL','NY','IL','OH','GA','NC','WA','AZ','PA','MI','NJ','VA']
PLAN_IDS = ['PREMIER-500','VALUE-250','ESSENTIAL-100','GOLD-PPO','SILVER-HMO']
PLAN_TYPES = ['PPO','HMO','EPO','POS','HDHP']
PAYER_IDS = ['PAY-200','PAY-300','PAY-400','PAY-500']
GROUP_NUMBERS = [f'GRP-{x}' for x in ['METRO-100','SUMMIT-200','PEAK-300','VALLEY-400','RIDGE-500']]

SPECIALTIES = ['Orthopedics','Cardiology','Internal Medicine','Neurology','Oncology',
               'Pulmonology','Gastroenterology','Endocrinology','Rheumatology','General Surgery']
FACILITY_NAMES = ['Metro Medical Center','Summit Health Associates','Peak Regional Hospital',
                  'Valley Orthopedic Clinic','Ridge Cardiology Group','Lakeview Internal Medicine',
                  'Crestwood Surgical Center','Horizon Neurology Associates','Pinnacle Oncology Center',
                  'Evergreen Pulmonary Clinic']

CLAIM_TYPES = ['Professional','Institutional']
POS_CODES = ['11','21','22','23','24','31','32','41','51','61']

# ICD-10 codes grouped by category
DX_CODES = {
    'Musculoskeletal': [('M17.11','Primary osteoarthritis, right knee'),('M54.5','Low back pain'),
                        ('M75.11','Rotator cuff tear, right shoulder'),('M79.3','Panniculitis, unspecified')],
    'Cardiovascular': [('I48.91','Atrial fibrillation, unspecified'),('I10','Essential hypertension'),
                       ('I25.10','Atherosclerotic heart disease'),('I50.9','Heart failure, unspecified')],
    'Respiratory': [('J44.1','COPD with acute exacerbation'),('J18.9','Pneumonia, unspecified'),
                    ('J45.41','Moderate persistent asthma with acute exacerbation')],
    'Endocrine': [('E11.9','Type 2 diabetes mellitus without complications'),('E11.65','Type 2 DM with hyperglycemia'),
                  ('E78.5','Dyslipidemia, unspecified')],
    'Oncology': [('C34.90','Malignant neoplasm of lung, unspecified'),('C50.919','Malignant neoplasm of breast'),
                 ('C61','Malignant neoplasm of prostate')],
}

CPT_CODES = [('99213','Office visit, established, low complexity'),('99214','Office visit, established, moderate'),
             ('99215','Office visit, established, high complexity'),('29881','Arthroscopy knee, meniscectomy'),
             ('93000','Electrocardiogram, complete'),('71046','Chest X-ray, 2 views'),
             ('72148','MRI lumbar spine without contrast'),('43239','Upper GI endoscopy with biopsy'),
             ('27447','Total knee arthroplasty'),('33533','CABG, single arterial graft'),
             ('96413','Chemotherapy administration, IV push')]

# CARC denial codes — the heart of P1
DENIAL_CODES = [
    ('CO-197','Precertification/authorization/notification absent','Missing Authorization',True),
    ('CO-50','Non-covered service','Non-Covered Service',False),
    ('CO-55','Procedure/treatment/drug is deemed experimental','Experimental/Investigational',False),
    ('CO-96','Non-covered charge(s)','Non-Covered Charge',False),
    ('CO-4','Procedure code is inconsistent with modifier or missing modifier','Coding Error',True),
    ('CO-16','Claim/service lacks information needed for adjudication','Missing Information',True),
    ('CO-29','Time limit for filing has expired','Timely Filing',True),
    ('CO-18','Duplicate claim/service','Duplicate Claim',True),
    ('PR-1','Deductible amount','Patient Responsibility',False),
    ('PR-2','Coinsurance amount','Patient Responsibility',False),
    ('CO-11','Diagnosis is inconsistent with procedure','Coding Error',True),
    ('CO-15','Authorization number is missing/invalid/not applicable','Missing Authorization',True),
    ('CO-27','Expenses incurred after coverage terminated','Eligibility',False),
    ('OA-23','Payment adjusted: charges are covered under capitation','Capitation',False),
]

# --- planted patterns ---
# Provider PRV-00003 and PRV-00007 will have disproportionately high preventable denial rates
HIGH_DENIAL_PROVIDERS = {2, 6}  # 0-indexed

# --- generate members ---
def gen_members(n=2000):
    rows = []
    for i in range(n):
        rows.append({
            'MEMBER_ID': uid('MBR', i+1),
            'FIRST_NAME': pick(FIRST_NAMES),
            'LAST_NAME': pick(LAST_NAMES),
            'DOB': date_between(date(1945,1,1), date(2005,12,31)).isoformat(),
            'GENDER': pick(['M','F']),
            'STATE': pick(STATES),
            'ZIP': f'{random.randint(10000,99999)}',
            'PLAN_ID': pick(PLAN_IDS),
            'PLAN_TYPE': pick(PLAN_TYPES),
            'GROUP_NUMBER': pick(GROUP_NUMBERS),
            'PAYER_ID': pick(PAYER_IDS),
            'EFFECTIVE_DATE': date_between(date(2024,1,1), date(2025,6,1)).isoformat(),
            'TERM_DATE': '',
        })
    write_csv(os.path.join(OUT, 'members.csv'), rows)
    return rows

# --- generate providers ---
def gen_providers(n=200):
    rows = []
    for i in range(n):
        rows.append({
            'PROVIDER_ID': uid('PRV', i+1),
            'PROVIDER_NPI': f'{1000000000 + i}',
            'PROVIDER_NAME': f'Dr. {pick(FIRST_NAMES)} {pick(LAST_NAMES)}',
            'SPECIALTY': pick(SPECIALTIES),
            'FACILITY_NAME': pick(FACILITY_NAMES),
            'STATE': pick(STATES),
            'NETWORK_STATUS': pick(['IN','IN','IN','OUT']),  # 75% in-network
        })
    write_csv(os.path.join(OUT, 'providers.csv'), rows)
    return rows

# --- generate claims + denials ---
def gen_claims_and_denials(members, providers, n_claims=20000):
    claims = []
    denial_notes = []
    denial_id = 0

    for i in range(n_claims):
        member = pick(members)
        prov_idx = random.randint(0, len(providers)-1)
        provider = providers[prov_idx]
        dos = date_between(date(2025,7,1), date(2026,9,30))
        dx_cat = pick(list(DX_CODES.keys()))
        dx_code, dx_desc = pick(DX_CODES[dx_cat])
        cpt_code, cpt_desc = pick(CPT_CODES)
        billed = round(random.uniform(150, 45000), 2)
        allowed = round(billed * random.uniform(0.55, 0.95), 2)

        # denial logic — overall ~18% denial rate
        is_denied = False
        denial_code_row = None
        if prov_idx in HIGH_DENIAL_PROVIDERS:
            # these providers have ~45% denial rate, mostly preventable
            if random.random() < 0.45:
                is_denied = True
                denial_code_row = pick([d for d in DENIAL_CODES if d[3]])  # preventable
        else:
            if random.random() < 0.14:
                is_denied = True
                denial_code_row = pick(DENIAL_CODES)

        paid = 0.0 if is_denied else round(allowed * random.uniform(0.75, 1.0), 2)
        status = 'DENIED' if is_denied else 'PAID'

        claim_id = uid('CLM', i+1)
        claims.append({
            'CLAIM_ID': claim_id,
            'MEMBER_ID': member['MEMBER_ID'],
            'PROVIDER_ID': provider['PROVIDER_ID'],
            'PROVIDER_NPI': provider['PROVIDER_NPI'],
            'PROVIDER_NAME': provider['PROVIDER_NAME'],
            'FACILITY_NAME': provider['FACILITY_NAME'],
            'PAYER_ID': member['PAYER_ID'],
            'DATE_OF_SERVICE': dos.isoformat(),
            'CLAIM_TYPE': pick(CLAIM_TYPES),
            'PLACE_OF_SERVICE': pick(POS_CODES),
            'PRIMARY_DIAGNOSIS': dx_code,
            'DIAGNOSIS_DESCRIPTION': dx_desc,
            'DIAGNOSIS_CATEGORY': dx_cat,
            'CPT_CODE': cpt_code,
            'CPT_DESCRIPTION': cpt_desc,
            'TOTAL_BILLED': billed,
            'TOTAL_ALLOWED': allowed,
            'TOTAL_PAID': paid,
            'STATUS': status,
            'DENIAL_CODE': denial_code_row[0] if is_denied else '',
            'DENIAL_REASON': denial_code_row[1] if is_denied else '',
            'DENIAL_CATEGORY': denial_code_row[2] if is_denied else '',
            'IS_PREVENTABLE': denial_code_row[3] if is_denied else '',
        })

        if is_denied:
            denial_id += 1
            note = gen_denial_note(claim_id, member, provider, denial_code_row, dx_desc, cpt_desc, dos)
            denial_notes.append({
                'DENIAL_NOTE_ID': uid('DNT', denial_id),
                'CLAIM_ID': claim_id,
                'NOTE_DATE': (dos + timedelta(days=random.randint(5,20))).isoformat(),
                'DENIAL_CODE': denial_code_row[0],
                'NOTE_TEXT': note,
            })

    write_csv(os.path.join(OUT, 'claims.csv'), claims)
    write_csv(os.path.join(OUT, 'denial_notes.csv'), denial_notes)
    return claims, denial_notes

def gen_denial_note(claim_id, member, provider, denial_row, dx_desc, cpt_desc, dos):
    code, reason, category, preventable = denial_row
    templates = {
        'Missing Authorization': [
            f"Claim {claim_id} for {cpt_desc} on {dos} was denied: no prior authorization on file. "
            f"Provider {provider['PROVIDER_NAME']} ({provider['FACILITY_NAME']}) did not submit auth request. "
            f"Patient diagnosis: {dx_desc}. Recommend contacting provider to obtain retro-auth within appeal window.",
            f"Denied {code}: precertification was required for {cpt_desc} but not obtained. "
            f"Service date {dos}, member {member['MEMBER_ID']}, plan {member['PLAN_ID']}. "
            f"This is a preventable denial. Provider should have submitted auth prior to service.",
        ],
        'Coding Error': [
            f"Claim {claim_id} denied due to coding inconsistency. Procedure {cpt_desc} does not align with "
            f"diagnosis {dx_desc} ({member['MEMBER_ID']}). Review suggests incorrect modifier or diagnosis code. "
            f"Corrected claim may be resubmitted.",
            f"Denied {code}: the procedure code is inconsistent with the submitted diagnosis. "
            f"Provider {provider['PROVIDER_NAME']} should verify coding and resubmit with correct modifiers.",
        ],
        'Missing Information': [
            f"Claim {claim_id} pended and denied: insufficient documentation to adjudicate. "
            f"Missing clinical notes supporting medical necessity for {cpt_desc}. "
            f"Provider {provider['PROVIDER_NAME']} should submit supporting documentation.",
        ],
        'Timely Filing': [
            f"Claim {claim_id} denied: submitted beyond the {random.choice([90,120,180])}-day filing limit. "
            f"Service date {dos}, received {(dos + timedelta(days=random.randint(100,200))).isoformat()}. "
            f"Provider {provider['PROVIDER_NAME']} may appeal with proof of timely submission.",
        ],
        'Duplicate Claim': [
            f"Claim {claim_id} flagged as duplicate submission for {cpt_desc} on {dos}. "
            f"An identical claim was previously processed. If this is a distinct service, "
            f"resubmit with modifier -59 or documentation of separate encounter.",
        ],
    }
    default = [
        f"Claim {claim_id} denied with code {code}: {reason}. "
        f"Service: {cpt_desc} for {dx_desc} on {dos}. Provider: {provider['PROVIDER_NAME']}. "
        f"Member: {member['MEMBER_ID']}, Plan: {member['PLAN_ID']}."
    ]
    options = templates.get(category, default)
    return pick(options)

# --- payer policies (short text docs for Cortex Search) ---
def gen_payer_policies():
    policies = [
        {'POLICY_ID': 'POL-001', 'PAYER_ID': 'PAY-200', 'POLICY_TITLE': 'Prior Authorization Requirements',
         'POLICY_TEXT': """Prior Authorization Policy - PAY-200 Premier Health Plan

All elective surgical procedures require prior authorization submitted at least 14 business days before the scheduled service date. Emergency and urgent services are exempt from pre-authorization but require notification within 48 hours of admission.

Authorization requests must include: (1) patient demographics and member ID, (2) ICD-10 diagnosis codes, (3) CPT procedure codes, (4) clinical justification with supporting documentation, (5) provider NPI and facility information.

Failure to obtain required authorization will result in denial under CARC code CO-197. Providers may request retro-authorization within 30 days of service for urgent cases only.

Covered surgical categories requiring auth: orthopedic joint procedures, cardiac catheterization and interventions, oncology treatments, spinal procedures, and all inpatient admissions exceeding 23-hour observation."""},

        {'POLICY_ID': 'POL-002', 'PAYER_ID': 'PAY-200', 'POLICY_TITLE': 'Timely Filing Requirements',
         'POLICY_TEXT': """Timely Filing Policy - PAY-200 Premier Health Plan

In-network providers must submit claims within 90 days of the date of service or discharge date, whichever is later. Out-of-network providers have 120 days. Claims received after the filing deadline will be denied under CARC code CO-29.

Appeals of timely filing denials must include proof of original submission (e.g., clearinghouse confirmation, electronic receipt) within 60 days of the denial date. The plan will not consider appeals received after the 60-day window.

For coordination of benefits (COB) claims, the filing clock starts on the date the primary payer processes the claim. Providers must submit the secondary claim within 90 days of the primary EOB date."""},

        {'POLICY_ID': 'POL-003', 'PAYER_ID': 'PAY-300', 'POLICY_TITLE': 'Medical Necessity Criteria - Orthopedic Surgery',
         'POLICY_TEXT': """Medical Necessity - Orthopedic Procedures - PAY-300 Summit Care

Total knee arthroplasty (CPT 27447) is considered medically necessary when ALL of the following criteria are met:
1. Radiographic evidence of moderate-to-severe osteoarthritis (Kellgren-Lawrence grade 3 or 4)
2. Failure of conservative treatment for at least 3 months including: physical therapy, NSAIDs, and at least one corticosteroid injection
3. Significant functional limitation documented by validated outcome measure (e.g., WOMAC score)
4. BMI below 45 (patients with BMI 40-45 require additional surgical risk assessment)

Arthroscopic knee surgery (CPT 29881) requires documentation of mechanical symptoms (locking, catching) or acute meniscal tear confirmed by MRI. Arthroscopy for isolated osteoarthritis without mechanical symptoms is not covered per current evidence guidelines.

Denial code CO-50 applies when medical necessity criteria are not met. Appeals must include updated clinical documentation addressing each criterion."""},

        {'POLICY_ID': 'POL-004', 'PAYER_ID': 'PAY-400', 'POLICY_TITLE': 'Coding and Billing Guidelines',
         'POLICY_TEXT': """Coding and Billing Policy - PAY-400 Valley Health Partners

Claims must be submitted with valid ICD-10-CM diagnosis codes to the highest level of specificity. Unspecified codes (e.g., codes ending in .9) will be accepted only when clinical documentation does not support a more specific code.

Modifier usage requirements:
- Modifier -25: Significant, separately identifiable E/M service on the same day as a procedure. Documentation must clearly support the separate E/M service.
- Modifier -59: Distinct procedural service. Required when procedures that are typically bundled are performed on separate anatomical sites or during separate encounters.

Common denial scenarios (CARC CO-4, CO-11):
- Procedure code does not match the diagnosis (e.g., cardiac procedure with musculoskeletal diagnosis)
- Missing required modifiers for unbundled services
- Diagnosis code laterality does not match procedure laterality

Corrected claims must be submitted with frequency code 7 (replacement) or 8 (void) within 120 days of the original denial."""},

        {'POLICY_ID': 'POL-005', 'PAYER_ID': 'PAY-300', 'POLICY_TITLE': 'Appeals and Grievances Process',
         'POLICY_TEXT': """Appeals Process - PAY-300 Summit Care

Level 1 (Internal Appeal): Must be filed within 60 days of denial. Submit written appeal with:
- Original claim information and denial reference
- Clinical documentation supporting medical necessity
- Peer-reviewed literature if applicable
- Letter of medical necessity from treating physician

Turnaround: standard appeals within 30 calendar days; expedited appeals for urgent/concurrent care within 72 hours.

Level 2 (External Review): Available if Level 1 appeal is upheld. Must be requested within 60 days of Level 1 decision. Conducted by an independent review organization (IRO).

For preventable denials (authorization, coding, timely filing): providers should correct and resubmit rather than appeal. Corrected claim resubmission is faster and has a higher success rate than the formal appeal process.

Historical overturn rates by denial category:
- Missing authorization (CO-197): 42% overturn when retro-auth is obtained
- Coding errors (CO-4, CO-11): 68% overturn with corrected claim
- Medical necessity (CO-50): 31% overturn with additional documentation
- Timely filing (CO-29): 15% overturn (requires proof of original submission)"""},
    ]
    write_csv(os.path.join(OUT, 'payer_policies.csv'), policies)

def write_csv(path, rows):
    if not rows:
        return
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

if __name__ == '__main__':
    print("Generating P1 Claims Denial Triage data...")
    members = gen_members(2000)
    providers = gen_providers(200)
    claims, denials = gen_claims_and_denials(members, providers, 20000)
    gen_payer_policies()
    denied_count = sum(1 for c in claims if c['STATUS'] == 'DENIED')
    preventable = sum(1 for c in claims if c['IS_PREVENTABLE'] == True)
    print(f"  Members: {len(members)}")
    print(f"  Providers: {len(providers)}")
    print(f"  Claims: {len(claims)} ({denied_count} denied, {preventable} preventable)")
    print(f"  Denial notes: {len(denials)}")
    print(f"  Payer policies: 5")
    print(f"  Output: {OUT}")
