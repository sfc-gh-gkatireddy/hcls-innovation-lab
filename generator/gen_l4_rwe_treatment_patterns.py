"""
L4 Real World Evidence: Treatment Patterns on OMOP — Synthetic Data Generator
Generates: person.csv, condition_occurrence.csv, drug_exposure.csv, measurement.csv,
           visit_occurrence.csv, note.csv
Schema modeled on OMOP CDM v5.4 (hcls-provider-cdata-omop skill in the HCLS
incubator repo), simplified to the columns a 90-minute lab needs. Concept IDs
are real OMOP standard concepts where shown.

The dataset includes planted patterns for teams to discover.
"""
import csv
import os
import random
from datetime import date, timedelta

SEED = 42
random.seed(SEED)
OUT = os.path.join(os.path.dirname(__file__), '..', 'tracks', 'l4_rwe_treatment_patterns', 'data')
os.makedirs(OUT, exist_ok=True)


def write_csv(name, rows):
    with open(os.path.join(OUT, name), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader()
        w.writerows(rows)


STUDY_START, STUDY_END = date(2024, 1, 1), date(2026, 9, 30)

# Real OMOP standard concepts
GENDER = {'M': 8507, 'F': 8532}
COND = [  # (concept_id, ICD10 source, name, prevalence)
    (201826, 'E11.9', 'Type 2 diabetes mellitus', 1.0),
    (320128, 'I10', 'Essential hypertension', 0.62),
    (432867, 'E78.5', 'Hyperlipidemia', 0.55),
    (433736, 'E66.9', 'Obesity', 0.48),
    (46271022, 'N18.3', 'Chronic kidney disease stage 3', 0.18),
    (4185932, 'I25.10', 'Ischemic heart disease', 0.14),
    (31317, 'K21.9', 'Gastroesophageal reflux disease', 0.12),
]
DRUGS = {  # name -> (concept_id, class, base monthly persistence hazard)
    'Metformin': (1503297, 'Biguanide'),
    'Glucavia': (99000101, 'GLP-1 RA'),  # fictional brand: non-standard local concept
    'Sematra': (99000102, 'GLP-1 RA'),   # fictional competitor
    'Empaflo': (99000103, 'SGLT2 inhibitor'),
    'Sitaglen': (99000104, 'DPP-4 inhibitor'),
    'Insulin glargine': (1502905, 'Basal insulin'),
}
MEAS = {'HbA1c': (3004410, '%'), 'BMI': (3038553, 'kg/m2'), 'eGFR': (3049187, 'mL/min/1.73m2')}
STATES = ['Karnataka', 'Telangana', 'Maharashtra', 'Tamil Nadu', 'Delhi', 'Gujarat', 'West Bengal', 'Kerala']

persons, conds, drugs, meas, visits, notes = [], [], [], [], [], []
ids = {'cond': 0, 'drug': 0, 'meas': 0, 'visit': 0, 'note': 0}


def nid(k):
    ids[k] += 1
    return ids[k]


def add_meas(pid, name, d, v):
    cid, unit = MEAS[name]
    meas.append(dict(MEASUREMENT_ID=nid('meas'), PERSON_ID=pid, MEASUREMENT_CONCEPT_ID=cid,
                     MEASUREMENT_NAME=name, MEASUREMENT_DATE=d.isoformat(),
                     VALUE_AS_NUMBER=round(v, 1), UNIT=unit))


def add_note(pid, d, ntype, text):
    notes.append(dict(NOTE_ID=nid('note'), PERSON_ID=pid, NOTE_DATE=d.isoformat(),
                      NOTE_TYPE=ntype, NOTE_TEXT=text))


GI_STOP = [
    "Patient reports persistent nausea and two episodes of vomiting since starting {d}. Unable to tolerate; {d} discontinued today. Will consider {alt}.",
    "Severe GI intolerance on {d} (nausea, early satiety, vomiting). Patient chose to stop therapy. Plan: switch to {alt}.",
    "Stopped {d} after 6 weeks due to nausea and diarrhea affecting daily activities. Titration was rapid per patient.",
]
COST_STOP = [
    "Patient stopped {d} due to cost; insurance prior authorization was denied. Restarting {alt}.",
    "Discontinued {d}: unable to afford monthly refills. Discussed patient assistance options.",
]
EFFICACY_STOP = [
    "HbA1c remains above target on {d} after 6 months. Escalating therapy to {alt}.",
    "Inadequate glycemic response to {d}. Discontinued and started {alt}.",
]
OTHER_STOP = [
    "Patient stopped {d} on own accord, reports fear of injections. Counselled; will revisit at next visit.",
    "{d} paused during hospitalization for unrelated surgery and not restarted.",
]
TITRATION = [
    "Started {d} at the lowest dose with a slow titration plan, increasing every 4 weeks. Counselled on smaller meals to reduce nausea.",
    "Initiated {d} 0.25 mg weekly; extended titration schedule given patient age. Dietary counselling provided for GI side effects.",
]
STANDARD_START = [
    "Started {d} weekly for glycemic control and weight reduction. Reviewed injection technique.",
    "Initiating {d}. HbA1c above goal on metformin. Patient agreeable to weekly injection.",
]
CONTINUE = [
    "Doing well on {d}. Mild nausea in the first weeks has resolved. HbA1c improving, weight down.",
    "Follow-up: tolerating {d} well. Continue current dose.",
]

for pid in range(1, 3001):
    age = int(random.triangular(30, 85, 58))
    sex = random.choice('MF')
    yob = 2026 - age
    persons.append(dict(PERSON_ID=pid, GENDER_CONCEPT_ID=GENDER[sex], GENDER=sex, YEAR_OF_BIRTH=yob,
                        AGE_AT_INDEX=age, STATE=random.choice(STATES)))
    dx_date = STUDY_START + timedelta(days=random.randint(0, 200))
    for cid, src, name, p in COND:
        if random.random() < p:
            conds.append(dict(CONDITION_OCCURRENCE_ID=nid('cond'), PERSON_ID=pid, CONDITION_CONCEPT_ID=cid,
                              CONDITION_SOURCE_VALUE=src, CONDITION_NAME=name,
                              CONDITION_START_DATE=(dx_date - timedelta(days=random.randint(0, 900))).isoformat()))
    # baseline labs
    a1c = random.uniform(7.4, 10.5)
    bmi = random.uniform(24, 40)
    add_meas(pid, 'HbA1c', dx_date, a1c)
    add_meas(pid, 'BMI', dx_date, bmi)
    add_meas(pid, 'eGFR', dx_date, random.uniform(40, 100))
    # line 1: metformin for everyone
    drugs.append(dict(DRUG_EXPOSURE_ID=nid('drug'), PERSON_ID=pid, DRUG_CONCEPT_ID=DRUGS['Metformin'][0],
                      DRUG_NAME='Metformin', DRUG_CLASS='Biguanide', DRUG_EXPOSURE_START_DATE=dx_date.isoformat(),
                      DRUG_EXPOSURE_END_DATE=STUDY_END.isoformat(), DAYS_SUPPLY=30, LINE_OF_THERAPY=1,
                      STOP_REASON_STRUCTURED=''))
    # line 2 add-on
    add_on = random.choices(['Glucavia', 'Sematra', 'Empaflo', 'Sitaglen'], [38, 22, 25, 15])[0]
    start = dx_date + timedelta(days=random.randint(90, 420))
    if start > STUDY_END - timedelta(days=120):
        continue
    slow_titration = add_on in ('Glucavia', 'Sematra') and random.random() < (0.55 if age >= 65 else 0.35)
    # persistence model (days on therapy)
    if add_on == 'Glucavia':
        p_gi = 0.30 * (2.0 if age >= 65 else 1.0) * (0.35 if slow_titration else 1.0)
    elif add_on == 'Sematra':
        p_gi = 0.18 * (1.6 if age >= 65 else 1.0) * (0.5 if slow_titration else 1.0)
    else:
        p_gi = 0.04
    r = random.random()
    if r < p_gi:
        reason, days = 'GI intolerance', random.randint(30, 95)
    elif r < p_gi + 0.08:
        reason, days = 'Cost / access', random.randint(60, 300)
    elif r < p_gi + 0.08 + (0.07 if add_on in ('Glucavia', 'Sematra') else 0.15):
        reason, days = 'Inadequate response', random.randint(150, 360)
    elif r < p_gi + 0.08 + 0.15 + 0.05:
        reason, days = 'Other', random.randint(40, 400)
    else:
        reason, days = None, None
    end = start + timedelta(days=days) if days else STUDY_END
    end = min(end, STUDY_END)
    drugs.append(dict(DRUG_EXPOSURE_ID=nid('drug'), PERSON_ID=pid, DRUG_CONCEPT_ID=DRUGS[add_on][0],
                      DRUG_NAME=add_on, DRUG_CLASS=DRUGS[add_on][1], DRUG_EXPOSURE_START_DATE=start.isoformat(),
                      DRUG_EXPOSURE_END_DATE=end.isoformat(), DAYS_SUPPLY=28 if 'GLP' in DRUGS[add_on][1] else 30,
                      LINE_OF_THERAPY=2,
                      # structured stop reason is mostly missing, as in real EHR data
                      STOP_REASON_STRUCTURED=('Adverse event' if reason == 'GI intolerance' and random.random() < 0.2 else '')))
    visits.append(dict(VISIT_OCCURRENCE_ID=nid('visit'), PERSON_ID=pid, VISIT_TYPE='Outpatient',
                       VISIT_START_DATE=start.isoformat()))
    # start note
    if add_on in ('Glucavia', 'Sematra') and random.random() < 0.7:
        tmpl = TITRATION if slow_titration else STANDARD_START
        add_note(pid, start, 'Progress note', random.choice(tmpl).format(d=add_on))
    # follow-up outcome labs
    on_days = (end - start).days
    eff = {'Glucavia': 1.6, 'Sematra': 1.3, 'Empaflo': 0.9, 'Sitaglen': 0.7}[add_on]
    frac = min(1.0, on_days / 180)
    fu = start + timedelta(days=min(on_days, 180) + random.randint(5, 30))
    if fu <= STUDY_END:
        add_meas(pid, 'HbA1c', fu, max(5.6, a1c - eff * frac + random.gauss(0, 0.4)))
        wl = {'Glucavia': 0.07, 'Sematra': 0.05, 'Empaflo': 0.02, 'Sitaglen': 0.0}[add_on]
        add_meas(pid, 'BMI', fu, bmi * (1 - wl * frac) + random.gauss(0, 0.4))
        visits.append(dict(VISIT_OCCURRENCE_ID=nid('visit'), PERSON_ID=pid, VISIT_TYPE='Outpatient',
                           VISIT_START_DATE=fu.isoformat()))
    # stop or continue note
    alt = random.choice(['Empaflo', 'Sitaglen', 'Insulin glargine'])
    if reason and random.random() < 0.85:
        tmpl = {'GI intolerance': GI_STOP, 'Cost / access': COST_STOP,
                'Inadequate response': EFFICACY_STOP, 'Other': OTHER_STOP}[reason]
        add_note(pid, end, 'Progress note', random.choice(tmpl).format(d=add_on, alt=alt))
    elif not reason and add_on in ('Glucavia', 'Sematra') and random.random() < 0.4:
        add_note(pid, start + timedelta(days=random.randint(60, 120)), 'Progress note',
                 random.choice(CONTINUE).format(d=add_on))

write_csv('person.csv', persons)
write_csv('condition_occurrence.csv', conds)
write_csv('drug_exposure.csv', drugs)
write_csv('measurement.csv', meas)
write_csv('visit_occurrence.csv', visits)
write_csv('note.csv', notes)
print(f"person={len(persons)} condition_occurrence={len(conds)} drug_exposure={len(drugs)} "
      f"measurement={len(meas)} visit_occurrence={len(visits)} note={len(notes)}")
