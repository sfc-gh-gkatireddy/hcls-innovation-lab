"""
L1 Clinical Trial Patient/Site Matching — Synthetic Data Generator
Generates: patients.csv, diagnoses.csv, labs.csv, medications.csv, sites.csv, protocol.txt
Schema inspired by scientific-workbench + clinical-trial-protocol skill
"""
import csv
import os
import random
from datetime import date, timedelta

SEED = 42
random.seed(SEED)
OUT = os.path.join(os.path.dirname(__file__), '..', 'tracks', 'l1_trial_matching', 'data')
DOCS = os.path.join(os.path.dirname(__file__), '..', 'tracks', 'l1_trial_matching', 'docs')
os.makedirs(OUT, exist_ok=True)
os.makedirs(DOCS, exist_ok=True)

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

# --- reference data ---
SITES = [
    ('SITE-01','Metro Cancer Center','New York','NY','US',120),
    ('SITE-02','Pacific Oncology Institute','San Francisco','CA','US',95),
    ('SITE-03','Midwest Clinical Research','Chicago','IL','US',80),
    ('SITE-04','Southern Medical Center','Houston','TX','US',110),
    ('SITE-05','Atlantic Research Hospital','Boston','MA','US',90),
    ('SITE-06','Mountain View Medical','Denver','CO','US',60),
    ('SITE-07','Lakeside University Hospital','Cleveland','OH','US',75),
    ('SITE-08','Suncoast Cancer Institute','Tampa','FL','US',85),
    ('SITE-09','Cascadia Medical Center','Seattle','WA','US',70),
    ('SITE-10','Valley Health Research','Phoenix','AZ','US',65),
    ('SITE-11','Capital Oncology Associates','Washington','DC','US',55),
    ('SITE-12','Heartland Clinical Trials','Kansas City','MO','US',50),
    ('SITE-13','Piedmont Cancer Research','Charlotte','NC','US',45),
    ('SITE-14','Great Lakes Medical Center','Detroit','MI','US',70),
    ('SITE-15','Rocky Mountain Research','Salt Lake City','UT','US',40),
    ('SITE-16','Gulf Coast Oncology','New Orleans','LA','US',55),
    ('SITE-17','Appalachian Health Center','Pittsburgh','PA','US',60),
    ('SITE-18','Desert Research Institute','Albuquerque','NM','US',35),
    ('SITE-19','Northstar Medical Center','Minneapolis','MN','US',80),
    ('SITE-20','Harbor Clinical Research','Los Angeles','CA','US',100),
    ('SITE-21','Tata Memorial Centre','Mumbai','MH','IN',150),
    ('SITE-22','Apollo Hospitals','Chennai','TN','IN',120),
    ('SITE-23','AIIMS Delhi','New Delhi','DL','IN',130),
    ('SITE-24','Max Super Speciality','Bangalore','KA','IN',90),
    ('SITE-25','Fortis Oncology Center','Hyderabad','TS','IN',85),
    ('SITE-26','Christian Medical College','Vellore','TN','IN',75),
    ('SITE-27','Manipal Hospital','Bangalore','KA','IN',80),
    ('SITE-28','Rajiv Gandhi Cancer Institute','Delhi','DL','IN',100),
    ('SITE-29','Nizam Institute','Hyderabad','TS','IN',60),
    ('SITE-30','Kidwai Memorial Institute','Bangalore','KA','IN',55),
    ('SITE-31','Kings College Hospital','London','LDN','GB',90),
    ('SITE-32','Charite Research Center','Berlin','BER','DE',85),
    ('SITE-33','Gustave Roussy','Paris','IDF','FR',110),
    ('SITE-34','National Cancer Centre','Tokyo','TKY','JP',100),
    ('SITE-35','Princess Margaret Cancer Centre','Toronto','ON','CA',95),
    ('SITE-36','Peter MacCallum Cancer Centre','Melbourne','VIC','AU',80),
    ('SITE-37','Samsung Medical Center','Seoul','SEL','KR',90),
    ('SITE-38','Sheba Medical Center','Tel Aviv','TA','IL',70),
    ('SITE-39','Hospital Israelita Albert Einstein','Sao Paulo','SP','BR',85),
    ('SITE-40','University of Cape Town','Cape Town','WC','ZA',50),
]

FIRST_NAMES = ['James','Sarah','Michael','Emily','Robert','Jessica','David','Ashley','Rajesh','Priya',
               'Amit','Sunita','Wei','Mei','Takeshi','Yuki','Carlos','Maria','Hans','Sophie',
               'Ahmed','Fatima','Kenji','Sakura','Ravi','Anita','Li','Jun','Pierre','Claire']
LAST_NAMES = ['Smith','Johnson','Williams','Patel','Kumar','Singh','Chen','Wang','Tanaka','Kim',
              'Garcia','Martinez','Mueller','Dubois','Anderson','Thompson','Sharma','Reddy','Gupta','Das']

# Type 2 diabetes trial — this is our protocol
# Planted pattern: eGFR < 30 is the most restrictive criterion
# Sites 24,25,27,30 (Bangalore/Hyderabad) have large untapped pools

DX_CODES_T2D = [
    ('E11.9','Type 2 diabetes mellitus without complications'),
    ('E11.65','Type 2 DM with hyperglycemia'),
    ('E11.22','Type 2 DM with diabetic chronic kidney disease'),
    ('E11.40','Type 2 DM with diabetic neuropathy'),
    ('E11.311','Type 2 DM with unspecified diabetic retinopathy with macular edema'),
]
DX_CODES_OTHER = [
    ('I10','Essential hypertension'),('E78.5','Dyslipidemia'),
    ('J44.1','COPD with acute exacerbation'),('I25.10','Atherosclerotic heart disease'),
    ('N18.3','Chronic kidney disease, stage 3'),('N18.4','CKD stage 4'),('N18.5','CKD stage 5'),
    ('K76.0','Fatty liver disease'),('F32.1','Major depressive disorder, moderate'),
]

MEDICATIONS_T2D = [
    ('Metformin 1000mg','Metformin','Oral','BID'),
    ('Metformin 500mg','Metformin','Oral','BID'),
    ('Glimepiride 2mg','Sulfonylurea','Oral','QD'),
    ('Sitagliptin 100mg','DPP-4 Inhibitor','Oral','QD'),
    ('Empagliflozin 25mg','SGLT2 Inhibitor','Oral','QD'),
    ('Insulin Glargine 20U','Basal Insulin','Subcutaneous','QD'),
    ('Liraglutide 1.8mg','GLP-1 RA','Subcutaneous','QD'),
    ('Semaglutide 1mg','GLP-1 RA','Subcutaneous','QW'),
]
MEDICATIONS_OTHER = [
    ('Lisinopril 10mg','ACE Inhibitor','Oral','QD'),
    ('Amlodipine 5mg','CCB','Oral','QD'),
    ('Atorvastatin 40mg','Statin','Oral','QD'),
    ('Aspirin 81mg','Antiplatelet','Oral','QD'),
]

def gen_sites():
    rows = [{'SITE_ID': s[0], 'SITE_NAME': s[1], 'CITY': s[2], 'STATE': s[3],
             'COUNTRY': s[4], 'ANNUAL_PATIENT_VOLUME': s[5]} for s in SITES]
    write_csv(os.path.join(OUT, 'sites.csv'), rows)

def gen_patients(n=5000):
    patients = []
    diagnoses = []
    labs = []
    medications = []

    for i in range(n):
        pid = uid('PAT', i+1)
        site = pick(SITES)
        age = random.randint(25, 85)
        sex = pick(['M','F'])
        has_t2d = random.random() < 0.35  # 35% have T2D

        patients.append({
            'PATIENT_ID': pid,
            'SITE_ID': site[0],
            'AGE': age,
            'SEX': sex,
            'RACE': pick(['White','Black','Asian','Hispanic','Other']),
            'COUNTRY': site[4],
        })

        # diagnoses
        if has_t2d:
            dx = pick(DX_CODES_T2D)
            diagnoses.append({
                'PATIENT_ID': pid, 'DIAGNOSIS_CODE': dx[0], 'DIAGNOSIS_DESCRIPTION': dx[1],
                'DIAGNOSIS_DATE': date_between(date(2020,1,1), date(2025,12,31)).isoformat(),
                'STATUS': 'Active',
            })
            # often have comorbidities
            for _ in range(random.randint(0,3)):
                cdx = pick(DX_CODES_OTHER)
                diagnoses.append({
                    'PATIENT_ID': pid, 'DIAGNOSIS_CODE': cdx[0], 'DIAGNOSIS_DESCRIPTION': cdx[1],
                    'DIAGNOSIS_DATE': date_between(date(2020,1,1), date(2025,12,31)).isoformat(),
                    'STATUS': 'Active',
                })
        else:
            for _ in range(random.randint(1,3)):
                cdx = pick(DX_CODES_OTHER)
                diagnoses.append({
                    'PATIENT_ID': pid, 'DIAGNOSIS_CODE': cdx[0], 'DIAGNOSIS_DESCRIPTION': cdx[1],
                    'DIAGNOSIS_DATE': date_between(date(2020,1,1), date(2025,12,31)).isoformat(),
                    'STATUS': 'Active',
                })

        # labs — HbA1c, eGFR, ALT, creatinine
        hba1c = round(random.gauss(7.8 if has_t2d else 5.4, 1.2 if has_t2d else 0.4), 1)
        hba1c = max(4.0, min(14.0, hba1c))

        # planted pattern: eGFR < 30 excludes the most patients
        if has_t2d:
            egfr = round(random.gauss(55, 25))  # T2D patients have lower eGFR on average
        else:
            egfr = round(random.gauss(85, 20))
        egfr = max(5, min(140, egfr))

        alt = round(random.gauss(30, 15))
        alt = max(5, min(200, alt))
        creatinine = round(random.gauss(1.1 if has_t2d else 0.9, 0.4), 2)
        creatinine = max(0.4, min(6.0, creatinine))

        lab_date = date_between(date(2026,1,1), date(2026,9,1)).isoformat()
        labs.extend([
            {'PATIENT_ID': pid, 'LAB_CODE': 'HBA1C', 'LAB_NAME': 'Hemoglobin A1c',
             'VALUE': hba1c, 'UNIT': '%', 'LAB_DATE': lab_date, 'NORMAL_LOW': 4.0, 'NORMAL_HIGH': 5.6},
            {'PATIENT_ID': pid, 'LAB_CODE': 'EGFR', 'LAB_NAME': 'Estimated GFR',
             'VALUE': egfr, 'UNIT': 'mL/min/1.73m2', 'LAB_DATE': lab_date, 'NORMAL_LOW': 60, 'NORMAL_HIGH': 120},
            {'PATIENT_ID': pid, 'LAB_CODE': 'ALT', 'LAB_NAME': 'Alanine Aminotransferase',
             'VALUE': alt, 'UNIT': 'U/L', 'LAB_DATE': lab_date, 'NORMAL_LOW': 7, 'NORMAL_HIGH': 56},
            {'PATIENT_ID': pid, 'LAB_CODE': 'CREATININE', 'LAB_NAME': 'Serum Creatinine',
             'VALUE': creatinine, 'UNIT': 'mg/dL', 'LAB_DATE': lab_date, 'NORMAL_LOW': 0.6, 'NORMAL_HIGH': 1.2},
        ])

        # medications
        if has_t2d:
            for _ in range(random.randint(1,3)):
                med = pick(MEDICATIONS_T2D)
                medications.append({
                    'PATIENT_ID': pid, 'MEDICATION_NAME': med[0], 'MEDICATION_CLASS': med[1],
                    'ROUTE': med[2], 'FREQUENCY': med[3], 'STATUS': 'Active',
                    'START_DATE': date_between(date(2022,1,1), date(2026,6,1)).isoformat(),
                })
        for _ in range(random.randint(0,2)):
            med = pick(MEDICATIONS_OTHER)
            medications.append({
                'PATIENT_ID': pid, 'MEDICATION_NAME': med[0], 'MEDICATION_CLASS': med[1],
                'ROUTE': med[2], 'FREQUENCY': med[3], 'STATUS': 'Active',
                'START_DATE': date_between(date(2022,1,1), date(2026,6,1)).isoformat(),
            })

    write_csv(os.path.join(OUT, 'patients.csv'), patients)
    write_csv(os.path.join(OUT, 'diagnoses.csv'), diagnoses)
    write_csv(os.path.join(OUT, 'labs.csv'), labs)
    write_csv(os.path.join(OUT, 'medications.csv'), medications)
    return patients, diagnoses, labs, medications

def gen_protocol():
    protocol = """CLINICAL TRIAL PROTOCOL
Study Title: A Phase 3, Randomized, Double-Blind, Placebo-Controlled Study to Evaluate the Efficacy and Safety of SNF-2847 (Glucobalance) as Add-On Therapy in Patients with Inadequately Controlled Type 2 Diabetes Mellitus

Protocol Number: SNF-2847-T2D-301
Sponsor: Snowflake Therapeutics, Inc.
Phase: 3
IND Number: 123456

1. STUDY SYNOPSIS

1.1 Background
Type 2 diabetes mellitus (T2DM) remains a global health challenge affecting over 500 million adults worldwide. Despite the availability of multiple glucose-lowering agents, a significant proportion of patients fail to achieve glycemic targets. SNF-2847 is a novel dual GLP-1/GIP receptor agonist that has shown promising results in Phase 2 trials, demonstrating superior HbA1c reduction compared to existing therapies.

1.2 Study Objectives
Primary: To evaluate the efficacy of SNF-2847 versus placebo in reducing HbA1c at Week 52.
Secondary: To assess the effect on fasting plasma glucose, body weight, and proportion of patients achieving HbA1c < 7.0%.

1.3 Study Design
Randomized 2:1 (SNF-2847 : placebo), double-blind, parallel-group, multicenter study. Total duration: 52 weeks of treatment + 4-week safety follow-up.

2. STUDY POPULATION

2.1 Target Population
Adults with inadequately controlled T2DM on stable metformin therapy.

2.2 Planned Enrollment
Approximately 1,200 patients across 40 sites globally.

3. ELIGIBILITY CRITERIA

3.1 Inclusion Criteria
Patients must meet ALL of the following criteria to be eligible:
  IC-1: Age 18 to 75 years, inclusive, at the time of informed consent.
  IC-2: Documented diagnosis of Type 2 diabetes mellitus (ICD-10: E11.x) for at least 12 months prior to screening.
  IC-3: HbA1c between 7.5% and 10.5%, inclusive, at screening.
  IC-4: Currently on stable metformin therapy (at least 1000 mg/day) for at least 8 weeks prior to screening.
  IC-5: Body mass index (BMI) between 25 and 45 kg/m2, inclusive.
  IC-6: Estimated glomerular filtration rate (eGFR) greater than or equal to 30 mL/min/1.73m2 at screening.
  IC-7: Willing and able to provide written informed consent.

3.2 Exclusion Criteria
Patients meeting ANY of the following criteria are excluded:
  EC-1: Type 1 diabetes mellitus or history of diabetic ketoacidosis.
  EC-2: Current use of any GLP-1 receptor agonist, SGLT2 inhibitor, or insulin within 12 weeks prior to screening.
  EC-3: History of pancreatitis or medullary thyroid carcinoma.
  EC-4: ALT or AST greater than 3 times the upper limit of normal at screening.
  EC-5: Severe cardiovascular event (myocardial infarction, stroke, or heart failure hospitalization) within 6 months prior to screening.
  EC-6: eGFR less than 30 mL/min/1.73m2 or currently on dialysis.
  EC-7: Pregnant, breastfeeding, or planning to become pregnant during the study period.
  EC-8: Known hypersensitivity to study drug or any of its excipients.
  EC-9: Participation in another interventional clinical trial within 30 days prior to screening.
  EC-10: Any condition that, in the investigator's opinion, would compromise patient safety or data quality.

4. STUDY PROCEDURES

4.1 Screening (Week -4 to Week 0)
- Informed consent
- Medical history and physical examination
- Laboratory assessments: HbA1c, fasting plasma glucose, comprehensive metabolic panel (including eGFR, ALT, AST), CBC, lipid panel, urinalysis, pregnancy test (if applicable)
- ECG
- Vital signs and anthropometrics (height, weight, BMI, waist circumference)

4.2 Treatment Period (Week 0 to Week 52)
- SNF-2847 10mg subcutaneous injection once weekly OR matching placebo
- Visits at Weeks 0, 2, 4, 8, 12, 16, 24, 36, 44, 52
- HbA1c measured at Weeks 12, 24, 36, and 52

4.3 Safety Follow-Up (Week 52 to Week 56)
- Final safety assessment 4 weeks after last dose

5. ENDPOINTS

5.1 Primary Endpoint
Change from baseline in HbA1c at Week 52.

5.2 Key Secondary Endpoints
- Change from baseline in fasting plasma glucose at Week 52
- Change from baseline in body weight at Week 52
- Proportion of patients achieving HbA1c < 7.0% at Week 52

5.3 Safety Endpoints
- Incidence and severity of adverse events
- Incidence of hypoglycemic events
- Changes in vital signs, ECG, and laboratory parameters

6. STATISTICAL CONSIDERATIONS

6.1 Sample Size
1,200 patients (800 SNF-2847, 400 placebo) provides >90% power to detect a 0.5% difference in HbA1c change from baseline, assuming a standard deviation of 1.2%, two-sided alpha of 0.05, and 15% dropout rate.

6.2 Analysis Populations
- ITT: All randomized patients
- mITT: All randomized patients with at least one post-baseline HbA1c
- Per-protocol: mITT patients without major protocol deviations
- Safety: All patients who received at least one dose

7. REGULATORY AND ETHICAL CONSIDERATIONS
This study will be conducted in accordance with ICH-GCP guidelines, the Declaration of Helsinki, and applicable local regulations. The protocol, informed consent, and all study-related documents will be approved by the relevant IRB/IEC at each participating site.
"""
    with open(os.path.join(DOCS, 'protocol_SNF2847_T2D_301.txt'), 'w') as f:
        f.write(protocol)

if __name__ == '__main__':
    print("Generating L1 Clinical Trial Matching data...")
    gen_sites()
    patients, diagnoses, labs, medications = gen_patients(5000)
    gen_protocol()
    t2d = [d for d in diagnoses if d['DIAGNOSIS_CODE'].startswith('E11')]
    t2d_pats = set(d['PATIENT_ID'] for d in t2d)
    print(f"  Sites: {len(SITES)}")
    print(f"  Patients: {len(patients)} ({len(t2d_pats)} with T2D)")
    print(f"  Diagnoses: {len(diagnoses)}")
    print(f"  Lab results: {len(labs)}")
    print(f"  Medications: {len(medications)}")
    print(f"  Protocol: protocol_SNF2847_T2D_301.txt")
    print(f"  Output: {OUT}")
