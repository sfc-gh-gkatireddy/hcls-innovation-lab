# P2: HEDIS Care Gap Closure from Clinical Notes

## The problem

Quality teams use manual chart review to find care that was delivered but never made it into claims. That evidence sits in clinical notes, and finding it directly moves Star ratings and reimbursement.

## Persona

Quality / Stars program manager who needs a ranked worklist so reviewers only look at charts that will close a gap.

## Your data

| Table | Rows | What is in it |
|-------|------|---------------|
| MEMBERS | 2,000 | Member demographics, plan type, PCP, risk score |
| MEASURE_GAPS | ~4,800 | Open and closed gaps by HEDIS measure (HbA1c, BCS, COL, CBP, etc.) |
| CLAIMS | 15,000 | Medical claims with diagnosis and procedure codes |
| VISIT_NOTES | ~2,800 | Free-text clinical visit notes (progress notes, wellness visits, telephone encounters) |

## Business questions your agent should answer

1. Which open care gaps have supporting evidence in the notes?
2. What is the potential gap closure lift by measure?
3. Which members should reviewers look at first?
4. Which measures have the biggest documentation gap?
5. Show me the note passage that closes this member's gap.

## AI functions to use

- **AI_EXTRACT** on visit notes: pull out structured evidence (test performed, date, result) that matches an open gap
- **AI_FILTER** to narrow to notes that mention a specific measure or test
- **Cortex Search** on visit notes so the agent can retrieve and quote the supporting passage

## Agent tools

- **Cortex Analyst** on a semantic view over members, gaps and evidence (for the counts and rankings)
- **Cortex Search** on the visit notes (for the supporting text)

## What done looks like

A ranked reviewer worklist of gaps likely closable from chart evidence, plus an agent that explains the evidence it found for any member.

## Stretch goal

Estimate the impact on measure rates and the Star rating if the identified gaps are closed.

## Hidden pattern

About 30% of open gaps have closing evidence buried in the visit notes. The AI extraction step should surface them. Diabetes measures (HbA1c, eye exam, BP control) have the highest note-evidence rates.
