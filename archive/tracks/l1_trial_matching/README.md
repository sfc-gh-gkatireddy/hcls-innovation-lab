# L1: Clinical Trial Patient and Site Matching

## The problem

Patient recruitment is one of the biggest causes of trial delays. Eligibility criteria live in long protocol documents while the patients who might qualify live in structured data. Connecting the two is slow and manual.

## Persona

Clinical operations or feasibility lead deciding where to open sites and whether the protocol is too restrictive.

## Your data

| Table | Rows | What is in it |
|-------|------|---------------|
| PATIENTS | 5,000 | Patient demographics and site affiliation |
| DIAGNOSES | ~11,000 | ICD-10 coded conditions per patient |
| LABS | 20,000 | Lab results (HbA1c, eGFR, ALT, creatinine) with dates |
| MEDICATIONS | ~8,600 | Current and past medications with class and route |
| SITES | 40 | Trial sites across US, India, Europe, Asia and others |
| Protocol (staged) | 1 document | Synthetic Phase 3 protocol for SNF-2847 (Type 2 diabetes) with full inclusion/exclusion criteria |

## Business questions your agent should answer

1. How many patients are eligible at each site?
2. Which inclusion/exclusion criterion is most limiting?
3. Which sites have the largest untapped eligible pool?
4. Why was a specific patient excluded?
5. What does the protocol say about prior therapies?

## AI functions to use

- **AI_PARSE_DOCUMENT** to read the protocol from the internal stage
- **AI_EXTRACT** to turn the eligibility criteria into structured rules, then apply them with SQL
- **Cortex Search** on the parsed protocol so the agent can answer questions about trial design

## Agent tools

- **Cortex Analyst** on a semantic view over patients, eligibility results and sites (for the numbers)
- **Cortex Search** on the protocol document (for the text)

## What done looks like

An agent that reports eligible patients per site, names the most restrictive criterion, and explains individual patient eligibility.

## Stretch goal

Run a what-if: relax one criterion (e.g. eGFR threshold) and compare the projected enrollment.

## Hidden pattern

The eGFR < 30 exclusion criterion eliminates the most patients. Three sites in Bangalore and Hyderabad have large untapped pools of eligible patients relative to their volume.
