# L2: Pharmacovigilance Adverse Event Signal Detection

## The problem

Drug safety teams must review a constant stream of adverse event reports, much of it free-text narrative. Spotting an emerging safety signal early protects patients and is a regulatory obligation.

## Persona

Drug safety or pharmacovigilance scientist who needs to triage cases and spot trends across products.

## Your data

| Table | Rows | What is in it |
|-------|------|---------------|
| PRODUCTS | 10 | Synthetic drug products with therapeutic area |
| AE_CASES | 5,000 | Cases with report date, product, MedDRA-style preferred term, seriousness, outcome, patient demographics |
| CASE_NARRATIVES | ~460 | Free-text case narratives describing the adverse event, clinical context and outcome |

## Business questions your agent should answer

1. Which product and event combinations are trending up?
2. How many serious cases occurred by product this quarter?
3. Summarize the recent cases for product X.
4. Which patient groups are most affected?
5. Find cases similar to this narrative.

## AI functions to use

- **AI_CLASSIFY** on narratives: classify by seriousness and event type
- **AI_AGG** to summarize many case narratives for a product in one call
- **Cortex Search** on the case narratives to find and quote similar cases

## Agent tools

- **Cortex Analyst** on a semantic view over cases, products and classifications (for the numbers and trends)
- **Cortex Search** on the case narratives (for the text)

## What done looks like

An agent that surfaces emerging product-event signals over time and summarizes the cases behind them on request.

## Stretch goal

Calculate a simple disproportionality score (Proportional Reporting Ratio, PRR) for each product-event pair. Signal threshold: PRR >= 2 AND case count >= 3.

## Hidden pattern

PROD-04 (Osteovance / Denosumab) has an emerging hepatotoxicity signal starting in Q2 2026. This is unexpected because it is a bone drug, not a liver drug. Your agent should find this signal.
