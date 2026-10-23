# HCLS Innovation Lab: AI Agents in Action

Synthetic data and setup scripts for the hands-on lab at the HCLS Innovation Lab events (Bengaluru 27 Oct, Hyderabad 30 Oct 2026).

## Quick start

1. Sign in to your Snowflake trial account.
2. Run `setup/00_common.sql` in a worksheet to create the database, warehouse and connect this repo.
3. Run the loader script for your track:
   - `setup/load_p1_claims_denials.sql`
   - `setup/load_p2_hedis_gaps.sql`
   - `setup/load_l3_commercial_hcp360.sql`
   - `setup/load_l4_rwe_treatment_patterns.sql`
4. Open CoCo and start building.

## Tracks

| Track | Domain | Problem |
|-------|--------|---------|
| [P1](tracks/p1_claims_denials/) | Payer | Claims denial triage and payment integrity |
| [P2](tracks/p2_hedis_gaps/) | Payer | HEDIS care gap closure from clinical notes |
| [L3](tracks/l3_commercial_hcp360/) | Life Sciences | Commercial HCP 360 and next best action |
| [L4](tracks/l4_rwe_treatment_patterns/) | Life Sciences | Real world evidence treatment patterns on OMOP |

See [guides/working_with_coco.md](guides/working_with_coco.md) for general CoCo guidance and [guides/pitch_template.md](guides/pitch_template.md) for the 90-second pitch format.

## Data

All data in this repo is fully synthetic. It contains no real patient information. Each dataset includes planted patterns for teams to discover.

The `generator/` directory contains the Python scripts used to produce the CSVs, so the data can be regenerated with a different seed if needed.

Retired tracks (L1 trial matching, L2 pharmacovigilance) are kept in `archive/`.
