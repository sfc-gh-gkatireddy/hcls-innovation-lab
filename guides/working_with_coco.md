# Working with CoCo

General guidance for the hands-on lab. These are approaches, not scripts. Adapt them to your track and your team's style.

## How to start

1. **Explore first.** Ask CoCo to profile your tables before building anything. Understand the row counts, column names, data types and distributions. Look at a few sample rows.

2. **Plan before you build.** Use CoCo's plan mode to describe the problem, the persona and the business questions. Let CoCo propose a plan. Review it as a team and adjust before you start writing SQL.

3. **Build one step at a time.** Each step below should work and produce visible output before you move on:
   - Step 1: Get the data loaded and verify the row counts.
   - Step 2: Apply the AI function(s) to the unstructured text or documents. Check the results on a few rows.
   - Step 3: Build a semantic view over the tables (including the AI-enriched output).
   - Step 4: Create a Cortex Search service on the text or documents.
   - Step 5: Create a Cortex Agent that uses both the semantic view and the search service as tools.
   - Step 6: Test the agent with your business questions. Iterate on the semantic view or the agent instructions.

4. **Verify each result.** After the AI step, spot-check the output. After the semantic view, ask Cortex Analyst a question and confirm the SQL is correct. After the agent, check that it uses the right tool for each question.

## Team roles

Split the work so everyone stays busy:

| Role | What they do |
|------|-------------|
| Data builder (1-2 people) | Load the data, profile it, verify row counts |
| AI step owner (1-2 people) | Apply AI_EXTRACT / AI_CLASSIFY / AI_COMPLETE / AI_PARSE_DOCUMENT and validate the output |
| Agent builder (1 person) | Build the semantic view, search service and agent; test the business questions |
| Storyteller (1 person) | Write the business problem, pick the demo questions, prepare the 90-second pitch |

## Milestone timeline

| Time | Milestone |
|------|-----------|
| 7:10-7:20 | Pick a track, assign roles, agree on 3-5 business questions |
| 7:20-7:40 | Data loaded and profiled |
| 7:40-8:05 | AI step working and validated |
| 8:05-8:25 | Semantic view, search service and agent answering questions |
| 8:25-8:40 | Stretch goal or polish; rehearse the pitch |

## Tips

- CoCo can write the CREATE TABLE, COPY INTO, semantic view YAML, search service DDL and agent DDL for you. Describe what you want, and iterate.
- If an AI function returns unexpected results, ask CoCo to show you the raw output first, then refine the prompt or the input.
- The agent works best when the semantic view has clear metric and dimension definitions. Spend time on good column descriptions.
- If you get stuck, call a facilitator. That is what they are there for.
