# L4: Real World Evidence — Treatment Patterns on OMOP

## The problem

Medical affairs and HEOR teams use real-world data to understand how drugs perform outside trials: who gets them, how long patients stay on therapy, and why they stop. The structured data shows *that* patients stop. The *why* is usually only in clinical notes.

## Persona

RWE / medical affairs scientist for **Glucavia**, a once-weekly GLP-1 for type 2 diabetes, who needs to explain real-world persistence and outcomes to the brand and clinical teams.

## Your data

The tables follow the **OMOP Common Data Model (CDM v5.4)**, the standard used by most real-world data networks, simplified for the lab. Concept IDs for conditions, labs and gender are real OMOP standard concepts.

| Table | Rows | What is in it |
|-------|------|---------------|
| PERSON | 3,000 | Adults with type 2 diabetes: sex, birth year, age, state |
| CONDITION_OCCURRENCE | ~9,240 | Diagnoses with OMOP concept and ICD-10 source code (T2DM, hypertension, obesity, CKD…) |
| DRUG_EXPOSURE | 6,000 | Metformin (line 1) plus one add-on therapy (line 2): Glucavia, Sematra, Empaflo or Sitaglen, with start and end dates |
| MEASUREMENT | 15,000 | HbA1c, BMI and eGFR at baseline and follow-up |
| VISIT_OCCURRENCE | 6,000 | Outpatient visits |
| NOTE | ~2,730 | Free-text clinician progress notes |

Note: a drug end date of 2026-09-30 means the patient was still on therapy at the data cut. The structured `STOP_REASON_STRUCTURED` column is mostly empty, just like real EHR data.

## Business questions your agent should answer

1. How many patients started each add-on therapy, and what do they look like (age, comorbidities)?
2. What is 6-month persistence by drug, and how does it differ by age group?
3. How much do HbA1c and BMI change on each drug?
4. Why are patients discontinuing Glucavia, and when?
5. What do the notes say about patients who stayed on therapy?

## AI functions to use

- **AI_CLASSIFY** on notes: discontinuation reason (GI intolerance, cost/access, inadequate response, other, not a stop)
- **AI_EXTRACT** to pull details such as the side effect, switch-to drug, or whether slow titration was used
- **AI_AGG** to summarize notes for a cohort
- **Cortex Search** on the progress notes to find and quote patient evidence

## Agent tools

- **Cortex Analyst** on a semantic view over persons, drug exposures, measurements and classified notes (the numbers)
- **Cortex Search** on the clinical notes (the evidence)

## What done looks like

An agent that reports persistence and outcomes by drug and cohort, explains why patients stop, and quotes the notes behind each answer.

## Stretch goal

Build a time-to-discontinuation view (days on therapy with censoring at the data cut) and compare Kaplan-Meier style persistence curves by drug or by titration approach.

## Hidden patterns

- Glucavia has the best HbA1c and weight reduction, but a **discontinuation spike between day 30 and 90**, driven by **GI intolerance**.
- Patients **aged 65+** stop Glucavia about twice as often as younger patients.
- Patients whose notes mention a **slow titration schedule** stay on therapy much longer. This is only visible in the notes.
