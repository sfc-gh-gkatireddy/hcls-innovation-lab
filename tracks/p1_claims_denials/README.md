# P1: Claims Denial Triage Agent

## The problem

Health plans and providers lose billions to denied claims that are never worked. Denial notes pile up, but nobody can quickly see which denials are preventable, which providers are driving them, or which claims are worth appealing first.

## Persona

Payment integrity or revenue cycle analyst who needs a prioritized worklist, not another static report.

## Your data

| Table | Rows | What is in it |
|-------|------|---------------|
| MEMBERS | 2,000 | Member demographics, plan, payer |
| PROVIDERS | 200 | Provider NPI, specialty, facility, network status |
| CLAIMS | 20,000 | Claims with billed/paid amounts, CARC denial codes, diagnosis and procedure |
| DENIAL_NOTES | ~2,800 | Free-text adjudication and denial notes |
| PAYER_POLICIES | 5 | Short policy documents (prior auth, timely filing, medical necessity, coding, appeals) |

## Business questions your agent should answer

1. What are the top denial drivers by provider and category?
2. How many dollars are at risk from preventable denials?
3. Which providers show unusual denial patterns?
4. Which claims should we appeal first, and why?
5. What does our policy say about the top denial reason?

## AI functions to use

- **AI_CLASSIFY** on denial note text: label each as preventable vs. not preventable and assign a root-cause category (missing auth, coding error, eligibility, etc.)
- **Cortex Search** on the payer policy documents so the agent can cite the relevant policy

## Agent tools

- **Cortex Analyst** on a semantic view over claims, denials and providers (for the numbers)
- **Cortex Search** on the payer policies (for the text)

## What done looks like

An agent in Snowflake CoWork that ranks the denials worth appealing, explains the root cause and the dollars behind each one, and cites the relevant policy.

## Stretch goal

Have the agent draft an appeal letter for a top claim using AI_COMPLETE, citing the policy passage returned by Cortex Search.

## Hidden pattern

Two providers in the dataset have disproportionately high rates of preventable denials. Your agent should find them.
