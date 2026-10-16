"""
P2 HEDIS Care Gap Closure from Clinical Notes — Synthetic Data Generator
Generates: members.csv, measure_gaps.csv, claims.csv, visit_notes.csv
Schema inspired by clinical-quality-agent + clinical-nlp skill + cost-of-care demo
"""
import csv
import os
import random
from datetime import date, timedelta

SEED = 42
random.seed(SEED)
OUT = os.path.join(os.path.dirname(__file__), '..', 'tracks', 'p2_hedis_gaps', 'data')
os.makedirs(OUT, exist_ok=True)

def uid(prefix, i):
    return f"{prefix}-{i:05d}"

def pick(lst):
    return random.choice(lst)

def date_between(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

def write_csv(path, rows):
    if not rows:
        return
    with open(path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)

# --- HEDIS measures ---
MEASURES = [
    ('CDC-HBA1C', 'Comprehensive Diabetes Care: HbA1c Testing', 'Diabetes',
     'HbA1c test performed in measurement year', 'E11'),
    ('CDC-EYE', 'Comprehensive Diabetes Care: Eye Exam', 'Diabetes',
     'Dilated retinal eye exam in measurement year or negative exam in prior year', 'E11'),
    ('CDC-BP', 'Comprehensive Diabetes Care: Blood Pressure Control', 'Diabetes',
     'Most recent BP reading < 140/90 mmHg', 'E11'),
    ('BCS', 'Breast Cancer Screening', 'Preventive',
     'Mammogram in past 2 years for women 50-74', None),
    ('COL', 'Colorectal Cancer Screening', 'Preventive',
     'Colonoscopy in past 10 years, FIT in past year, or FIT-DNA in past 3 years for ages 45-75', None),
    ('CCS', 'Cervical Cancer Screening', 'Preventive',
     'Pap test in past 3 years (ages 21-64) or HPV co-test in past 5 years (ages 30-64)', None),
    ('CBP', 'Controlling High Blood Pressure', 'Cardiovascular',
     'Most recent BP reading < 140/90 mmHg for hypertension patients', 'I10'),
    ('SPD', 'Statin Therapy for Patients with Diabetes', 'Diabetes',
     'Received statin therapy during measurement year', 'E11'),
    ('PPC-PRE', 'Prenatal and Postpartum Care: Timeliness of Prenatal Care', 'Maternal',
     'Prenatal visit in first trimester or within 42 days of enrollment', None),
    ('FUH-30', 'Follow-Up After Hospitalization for Mental Illness (30 day)', 'Behavioral',
     'Follow-up visit within 30 days of discharge', 'F'),
]

FIRST_NAMES = ['Maria','Patricia','Jennifer','Linda','Barbara','Elizabeth','Susan','Jessica','Sarah','Karen',
               'Lisa','Nancy','Betty','Margaret','Sandra','Ashley','Dorothy','Kimberly','Emily','Donna',
               'James','Robert','John','Michael','David','William','Richard','Joseph','Thomas','Charles']
LAST_NAMES = ['Smith','Johnson','Williams','Brown','Jones','Garcia','Miller','Davis','Rodriguez','Martinez',
              'Hernandez','Lopez','Wilson','Anderson','Thomas','Taylor','Moore','Jackson','Martin','Lee']
STATES = ['NY','CA','TX','FL','IL','PA','OH','GA','NC','MI','NJ','VA','WA','AZ','MA']
PLAN_TYPES = ['HMO','PPO','Medicaid','Medicare Advantage','EPO']

# --- note templates ---
def note_with_evidence(member, measure, visit_date):
    """Generate a visit note that contains evidence closing the gap."""
    templates = {
        'CDC-HBA1C': [
            f"PROGRESS NOTE\nDate: {visit_date}\nPatient: {member['FIRST_NAME']} {member['LAST_NAME']}, DOB: {member['DOB']}\n\n"
            f"CC: Diabetes follow-up\n\n"
            f"HPI: {member['FIRST_NAME']} returns for routine diabetes management. Reports good medication compliance. "
            f"Checking feet daily, no new wounds. Diet adherence has improved.\n\n"
            f"LABS (drawn {(visit_date - timedelta(days=random.randint(2,7))).isoformat()}):\n"
            f"  HbA1c: {round(random.uniform(6.5, 9.2), 1)}%\n"
            f"  Fasting glucose: {random.randint(95, 180)} mg/dL\n"
            f"  Creatinine: {round(random.uniform(0.7, 1.4), 2)} mg/dL\n"
            f"  eGFR: {random.randint(45, 110)} mL/min\n\n"
            f"ASSESSMENT: Type 2 diabetes, {pick(['well controlled','suboptimally controlled','poorly controlled'])}.\n"
            f"PLAN: Continue current regimen. Recheck HbA1c in 3 months. Reinforce dietary counseling.",
        ],
        'CDC-EYE': [
            f"PROGRESS NOTE\nDate: {visit_date}\nPatient: {member['FIRST_NAME']} {member['LAST_NAME']}\n\n"
            f"Diabetes follow-up. Patient reports completing dilated eye exam with Dr. {pick(LAST_NAMES)} "
            f"at {pick(['Metro Eye Associates','Valley Vision Center','City Ophthalmology'])} on "
            f"{(visit_date - timedelta(days=random.randint(10,60))).isoformat()}. "
            f"Results: {pick(['No diabetic retinopathy noted','Mild non-proliferative diabetic retinopathy, stable','Background diabetic retinopathy, unchanged from prior year'])}. "
            f"Follow-up eye exam recommended in {pick(['6 months','12 months'])}.",
        ],
        'CDC-BP': [
            f"PROGRESS NOTE\nDate: {visit_date}\nPatient: {member['FIRST_NAME']} {member['LAST_NAME']}\n\n"
            f"VITALS:\n"
            f"  BP: {random.randint(110, 138)}/{random.randint(65, 88)} mmHg\n"
            f"  HR: {random.randint(62, 88)} bpm\n"
            f"  Weight: {random.randint(140, 240)} lbs\n\n"
            f"Diabetes and hypertension follow-up. Blood pressure at goal today. "
            f"Continue current antihypertensive regimen. Patient tolerating medications well.",
        ],
        'BCS': [
            f"ANNUAL WELLNESS VISIT\nDate: {visit_date}\nPatient: {member['FIRST_NAME']} {member['LAST_NAME']}\n\n"
            f"Preventive care review. Patient reports completing screening mammogram on "
            f"{(visit_date - timedelta(days=random.randint(5,45))).isoformat()} at {pick(['Metro Imaging','Regional Radiology','Women Health Center'])}. "
            f"Results: {pick(['BI-RADS 1 - Negative','BI-RADS 2 - Benign finding','BI-RADS 1 - No abnormality detected'])}. "
            f"Next mammogram recommended in 12 months.",
        ],
        'COL': [
            f"PROGRESS NOTE\nDate: {visit_date}\nPatient: {member['FIRST_NAME']} {member['LAST_NAME']}\n\n"
            f"Patient completed {pick(['colonoscopy','FIT test','Cologuard (FIT-DNA)'])} on "
            f"{(visit_date - timedelta(days=random.randint(7,90))).isoformat()}. "
            f"Result: {pick(['Normal colonoscopy, no polyps','One small hyperplastic polyp removed, benign','FIT negative','Cologuard negative'])}. "
            f"Next screening per guidelines.",
        ],
        'CBP': [
            f"OFFICE VISIT\nDate: {visit_date}\nPatient: {member['FIRST_NAME']} {member['LAST_NAME']}\n\n"
            f"Hypertension management.\n"
            f"VITALS: BP {random.randint(112, 136)}/{random.randint(68, 86)} mmHg (seated, resting 5 min)\n\n"
            f"Blood pressure at goal. Continue lisinopril {pick(['10mg','20mg'])} daily. "
            f"Patient reports good adherence. No side effects.",
        ],
        'SPD': [
            f"PROGRESS NOTE\nDate: {visit_date}\nPatient: {member['FIRST_NAME']} {member['LAST_NAME']}\n\n"
            f"Diabetes management. Currently on atorvastatin {pick(['20mg','40mg'])} daily. "
            f"Recent lipid panel: LDL {random.randint(55, 95)} mg/dL, HDL {random.randint(38, 65)} mg/dL, "
            f"triglycerides {random.randint(100, 200)} mg/dL. Statin therapy continued per ADA guidelines.",
        ],
    }
    default = [
        f"OFFICE VISIT\nDate: {visit_date}\nPatient: {member['FIRST_NAME']} {member['LAST_NAME']}\n\n"
        f"Routine follow-up. {pick(['All preventive screenings up to date.','Care plan reviewed.','Discussed preventive care schedule.'])} "
        f"Documented completion of recommended screening per measure {measure['MEASURE_ID']}."
    ]
    return pick(templates.get(measure['MEASURE_ID'], default))

def note_without_evidence(member, visit_date):
    """Generate a visit note that does NOT contain gap-closing evidence."""
    templates = [
        f"PROGRESS NOTE\nDate: {visit_date}\nPatient: {member['FIRST_NAME']} {member['LAST_NAME']}, DOB: {member['DOB']}\n\n"
        f"CC: {pick(['Acute upper respiratory infection','Follow-up for medication refill','Low back pain','Knee pain','Headache'])}\n\n"
        f"HPI: {member['FIRST_NAME']} presents with {pick(['3 days of nasal congestion and sore throat','request for routine medication refills','worsening low back pain for 2 weeks'])}. "
        f"No fever, no shortness of breath.\n\n"
        f"EXAM: {pick(['HEENT: mild pharyngeal erythema, no exudates','MSK: tenderness over lumbar paraspinals','General: well-appearing, NAD'])}\n\n"
        f"ASSESSMENT: {pick(['Acute pharyngitis, likely viral','Chronic low back pain','Tension headache'])}.\n"
        f"PLAN: {pick(['Supportive care, rest, fluids. Return if symptoms worsen.','Continue current medications. Follow up in 4 weeks.','OTC analgesics, stretching exercises.'])}",

        f"TELEPHONE ENCOUNTER\nDate: {visit_date}\nPatient: {member['FIRST_NAME']} {member['LAST_NAME']}\n\n"
        f"Patient called regarding {pick(['medication side effects','prescription refill','lab result inquiry'])}. "
        f"Advised to {pick(['continue current medications','schedule in-office follow-up','monitor symptoms and call back if worsening'])}. "
        f"No acute concerns at this time.",

        f"OFFICE VISIT\nDate: {visit_date}\nPatient: {member['FIRST_NAME']} {member['LAST_NAME']}\n\n"
        f"Annual wellness visit. Reviewed medications and allergies. Updated family history. "
        f"Discussed importance of preventive screenings. Patient declined {pick(['colonoscopy referral','mammogram scheduling','eye exam referral'])} at this time "
        f"due to {pick(['scheduling conflicts','financial concerns','personal preference'])}. Will revisit at next appointment.",
    ]
    return pick(templates)

def gen_members(n=2000):
    rows = []
    for i in range(n):
        age = random.randint(21, 85)
        sex = pick(['M','F'])
        rows.append({
            'MEMBER_ID': uid('MBR', i+1),
            'FIRST_NAME': pick(FIRST_NAMES),
            'LAST_NAME': pick(LAST_NAMES),
            'DOB': (date(2026,1,1) - timedelta(days=age*365 + random.randint(0,364))).isoformat(),
            'AGE': age,
            'SEX': sex,
            'STATE': pick(STATES),
            'PLAN_TYPE': pick(PLAN_TYPES),
            'PCP_PROVIDER': f'Dr. {pick(FIRST_NAMES)} {pick(LAST_NAMES)}',
            'RISK_SCORE': round(random.uniform(0.5, 4.5), 2),
        })
    write_csv(os.path.join(OUT, 'members.csv'), rows)
    return rows

def gen_gaps_and_notes(members):
    gaps = []
    notes = []
    note_id = 0

    for member in members:
        age = member['AGE']
        sex = member['SEX']
        applicable_measures = []

        for m in MEASURES:
            mid, mname, mcat, mdesc, dx_prefix = m
            measure = {'MEASURE_ID': mid, 'MEASURE_NAME': mname, 'CATEGORY': mcat, 'DESCRIPTION': mdesc}

            # age/sex eligibility
            if mid in ('BCS',) and (sex != 'F' or age < 50 or age > 74):
                continue
            if mid in ('CCS',) and (sex != 'F' or age < 21 or age > 64):
                continue
            if mid in ('COL',) and (age < 45 or age > 75):
                continue
            if mid.startswith('CDC-') or mid == 'SPD':
                if random.random() > 0.25:  # ~25% are diabetic
                    continue
            if mid == 'CBP':
                if random.random() > 0.35:  # ~35% have HTN
                    continue
            if mid.startswith('PPC'):
                if sex != 'F' or age < 18 or age > 44 or random.random() > 0.03:
                    continue
            if mid == 'FUH-30':
                if random.random() > 0.02:
                    continue

            applicable_measures.append(measure)

        for measure in applicable_measures:
            # ~40% of gaps are already closed via claims
            closed_via_claims = random.random() < 0.40
            # of the remaining open gaps, ~30% have evidence in notes (planted pattern)
            has_note_evidence = not closed_via_claims and random.random() < 0.30

            gaps.append({
                'GAP_ID': uid('GAP', len(gaps)+1),
                'MEMBER_ID': member['MEMBER_ID'],
                'MEASURE_ID': measure['MEASURE_ID'],
                'MEASURE_NAME': measure['MEASURE_NAME'],
                'CATEGORY': measure['CATEGORY'],
                'MEASUREMENT_YEAR': 2026,
                'GAP_STATUS': 'CLOSED' if closed_via_claims else 'OPEN',
                'CLOSED_BY': 'CLAIMS' if closed_via_claims else '',
                'EVIDENCE_IN_NOTES': has_note_evidence,
            })

            # generate visit notes
            if has_note_evidence:
                note_id += 1
                visit_date = date_between(date(2026, 1, 15), date(2026, 9, 15))
                notes.append({
                    'NOTE_ID': uid('NOTE', note_id),
                    'MEMBER_ID': member['MEMBER_ID'],
                    'VISIT_DATE': visit_date.isoformat(),
                    'PROVIDER': member['PCP_PROVIDER'],
                    'NOTE_TYPE': pick(['PROGRESS','ANNUAL_WELLNESS','OFFICE_VISIT']),
                    'NOTE_TEXT': note_with_evidence(member, measure, visit_date),
                })

        # add some noise notes without gap-closing evidence
        for _ in range(random.randint(0, 2)):
            note_id += 1
            visit_date = date_between(date(2025, 6, 1), date(2026, 9, 15))
            notes.append({
                'NOTE_ID': uid('NOTE', note_id),
                'MEMBER_ID': member['MEMBER_ID'],
                'VISIT_DATE': visit_date.isoformat(),
                'PROVIDER': member['PCP_PROVIDER'],
                'NOTE_TYPE': pick(['PROGRESS','TELEPHONE','ACUTE_VISIT']),
                'NOTE_TEXT': note_without_evidence(member, visit_date),
            })

    write_csv(os.path.join(OUT, 'measure_gaps.csv'), gaps)
    write_csv(os.path.join(OUT, 'visit_notes.csv'), notes)
    return gaps, notes

def gen_claims(members, n=15000):
    dx_codes = [('E11.9','Type 2 diabetes'),('I10','Essential hypertension'),('J06.9','URI'),
                ('M54.5','Low back pain'),('Z00.00','General adult exam'),('Z12.31','Screening mammogram'),
                ('Z12.11','Screening colonoscopy'),('Z01.00','Eye exam'),('E78.5','Dyslipidemia'),
                ('F32.1','Major depressive disorder')]
    cpt_codes = [('99213','Office visit, est, low'),('99214','Office visit, est, mod'),
                 ('99215','Office visit, est, high'),('99395','Preventive visit, 18-39'),
                 ('99396','Preventive visit, 40-64'),('99397','Preventive visit, 65+'),
                 ('77067','Screening mammogram'),('45378','Colonoscopy'),('83036','HbA1c test'),
                 ('92004','Eye exam, new patient')]
    rows = []
    for i in range(n):
        m = pick(members)
        dx = pick(dx_codes)
        cpt = pick(cpt_codes)
        dos = date_between(date(2025,1,1), date(2026,9,30))
        rows.append({
            'CLAIM_ID': uid('CLM', i+1),
            'MEMBER_ID': m['MEMBER_ID'],
            'DATE_OF_SERVICE': dos.isoformat(),
            'DIAGNOSIS_CODE': dx[0],
            'DIAGNOSIS_DESCRIPTION': dx[1],
            'CPT_CODE': cpt[0],
            'CPT_DESCRIPTION': cpt[1],
            'PROVIDER': m['PCP_PROVIDER'],
            'BILLED_AMOUNT': round(random.uniform(75, 1500), 2),
            'PAID_AMOUNT': round(random.uniform(50, 1200), 2),
        })
    write_csv(os.path.join(OUT, 'claims.csv'), rows)
    return rows

if __name__ == '__main__':
    print("Generating P2 HEDIS Care Gap Closure data...")
    members = gen_members(2000)
    gaps, notes = gen_gaps_and_notes(members)
    claims = gen_claims(members, 15000)
    open_gaps = [g for g in gaps if g['GAP_STATUS'] == 'OPEN']
    note_evidence = [g for g in gaps if g['EVIDENCE_IN_NOTES']]
    print(f"  Members: {len(members)}")
    print(f"  Measure gaps: {len(gaps)} ({len(open_gaps)} open, {len([g for g in gaps if g['GAP_STATUS']=='CLOSED'])} closed)")
    print(f"  Gaps with note evidence: {len(note_evidence)} (these are the ones AI should find)")
    print(f"  Visit notes: {len(notes)}")
    print(f"  Claims: {len(claims)}")
    print(f"  Output: {OUT}")
