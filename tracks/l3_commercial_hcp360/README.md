# L3: Commercial HCP 360 & Next Best Action

## The problem

Pharma field teams have more data than ever (prescriptions, CRM calls, rep notes) but brand teams still can't quickly answer *why* a brand is slowing in a territory or *which* doctors a rep should see next. The answer is usually split between the numbers (Rx trends) and the text (what doctors are telling reps).

## Persona

Brand manager or commercial excellence lead for **Glucavia**, a once-weekly GLP-1 for type 2 diabetes, who needs to explain performance and give the field a prioritized, evidence-backed call plan.

## Your data

| Table | Rows | What is in it |
|-------|------|---------------|
| BRANDS | 4 | Glucavia (our brand) and three competitors |
| TERRITORIES | 12 | Sales territories across India with assigned reps |
| HCPS | 2,000 | Doctors with specialty, territory, decile (prescribing potential) and target tier |
| RX_MONTHLY | 96,000 | Monthly TRx / NRx per doctor per brand, Oct 2025 to Sep 2026 |
| CALLS | ~10,450 | Rep call activity: date, channel, samples |
| CALL_NOTES | ~1,460 | Free-text notes reps wrote after calls |
| MESSAGING_DOCS | 8 | Approved messaging, objection handling and a formulary bulletin |

## Business questions your agent should answer

1. Where is Glucavia growing or declining, by territory and specialty?
2. What objections are doctors raising, and how is that changing?
3. Which territories show the strongest competitor pressure?
4. Which high-potential doctors haven't been seen recently and should be called next?
5. What does our approved messaging say about handling the top objection?

## AI functions to use

- **AI_CLASSIFY** on call notes: objection type (access, efficacy, safety, cost, competitor, positive) and sentiment
- **AI_EXTRACT** or **AI_FILTER** to pull competitor names or find notes about a specific topic
- **AI_AGG** to summarize what doctors in one territory are saying
- **Cortex Search** on the messaging documents (and optionally the call notes)

## Agent tools

- **Cortex Analyst** on a semantic view over HCPs, Rx, calls and classified notes (the numbers)
- **Cortex Search** on the approved messaging docs (what to say)

## What done looks like

An agent that explains where Glucavia is slipping and why, then recommends which doctors to call next and what approved message to use.

## Stretch goal

Build a simple next-best-action score per HCP (for example decile × declining NRx × days since last call) and have the agent draft a pre-call brief for the top doctor, using the right objection-handling guidance.

## Hidden patterns

- Territory **T07 (Pune West)**: Glucavia NRx drops sharply from **May 2026**. The notes there are dominated by prior authorization and access objections, and the May 2026 formulary bulletin explains why.
- Territory **T03 (Hyderabad Central)**: competitor Sematra gains share, with rising competitor mentions in the notes.
- About **40 decile 8-10 doctors** have had no call since June 2026.
