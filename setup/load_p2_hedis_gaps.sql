-- ============================================================
-- P2: HEDIS Care Gap Closure — Data Loader
-- ============================================================
-- This script loads the synthetic HEDIS care-gap dataset from
-- the public GitHub repo into your Snowflake account.
--
-- PREREQUISITE: Run setup/00_common.sql first. It creates the
-- database (HCLS_LAB), warehouse, git repo connection and CSV
-- file format that this script depends on.
-- ============================================================

-- Switch to the lab database created by 00_common.sql
USE DATABASE HCLS_LAB;

-- ============================================================
-- STEP 1: Create a dedicated schema for the P2 track
-- ============================================================
CREATE SCHEMA IF NOT EXISTS P2_HEDIS_GAPS;
USE SCHEMA P2_HEDIS_GAPS;

-- ============================================================
-- STEP 2: Create the tables
-- ============================================================

-- Health plan members (2,000 rows)
-- Includes a risk score and PCP assignment for prioritization.
CREATE OR REPLACE TABLE MEMBERS (
    MEMBER_ID VARCHAR(20),       -- Unique member identifier (e.g. MBR-00001)
    FIRST_NAME VARCHAR(50),
    LAST_NAME VARCHAR(50),
    DOB DATE,
    AGE INT,
    SEX VARCHAR(1),              -- M or F
    STATE VARCHAR(2),
    PLAN_TYPE VARCHAR(30),       -- HMO, PPO, Medicaid, Medicare Advantage, etc.
    PCP_PROVIDER VARCHAR(100),   -- Assigned primary care provider name
    RISK_SCORE NUMBER(4,2)       -- Higher = more complex patient (0.5 to 4.5)
);

-- HEDIS quality measure gaps (~4,800 rows)
-- Each row is one measure for one member. GAP_STATUS is OPEN (not
-- yet satisfied via claims) or CLOSED. The EVIDENCE_IN_NOTES flag
-- marks gaps where the visit notes contain closing evidence that
-- claims missed — this is what teams should discover with AI.
CREATE OR REPLACE TABLE MEASURE_GAPS (
    GAP_ID VARCHAR(20),
    MEMBER_ID VARCHAR(20),        -- FK to MEMBERS
    MEASURE_ID VARCHAR(20),       -- e.g. CDC-HBA1C, BCS, COL, CBP
    MEASURE_NAME VARCHAR(200),    -- Full HEDIS measure name
    CATEGORY VARCHAR(50),         -- Diabetes, Preventive, Cardiovascular, etc.
    MEASUREMENT_YEAR INT,         -- 2026
    GAP_STATUS VARCHAR(10),       -- OPEN or CLOSED
    CLOSED_BY VARCHAR(20),        -- CLAIMS if closed via claims data, else empty
    EVIDENCE_IN_NOTES BOOLEAN     -- TRUE if the visit notes contain closing evidence
);

-- Medical claims (15,000 rows)
-- Standard claims with diagnosis and procedure codes. Some claims
-- close gaps directly (e.g. a mammogram CPT code closes BCS).
CREATE OR REPLACE TABLE CLAIMS (
    CLAIM_ID VARCHAR(20),
    MEMBER_ID VARCHAR(20),        -- FK to MEMBERS
    DATE_OF_SERVICE DATE,
    DIAGNOSIS_CODE VARCHAR(10),   -- ICD-10-CM code
    DIAGNOSIS_DESCRIPTION VARCHAR(200),
    CPT_CODE VARCHAR(10),         -- Procedure code (e.g. 83036 = HbA1c test)
    CPT_DESCRIPTION VARCHAR(200),
    PROVIDER VARCHAR(100),
    BILLED_AMOUNT NUMBER(12,2),
    PAID_AMOUNT NUMBER(12,2)
);

-- Clinical visit notes (~2,800 rows)
-- Free-text progress notes, wellness visits and telephone encounters.
-- About 30% of open gaps have closing evidence buried in these notes
-- (e.g. "HbA1c: 7.2%" in a progress note closes the CDC-HBA1C gap).
-- Teams will use AI_EXTRACT to find this evidence and Cortex Search
-- to let the agent quote the supporting passage.
CREATE OR REPLACE TABLE VISIT_NOTES (
    NOTE_ID VARCHAR(20),
    MEMBER_ID VARCHAR(20),        -- FK to MEMBERS
    VISIT_DATE DATE,
    PROVIDER VARCHAR(100),
    NOTE_TYPE VARCHAR(30),        -- PROGRESS, ANNUAL_WELLNESS, TELEPHONE, ACUTE_VISIT
    NOTE_TEXT VARCHAR(16777216)    -- Full clinical note text
);

-- ============================================================
-- STEP 3: Load data from the GitHub repo
-- ============================================================
-- The COPY INTO commands read CSV files directly from the git
-- repository stage created in 00_common.sql.

COPY INTO MEMBERS
  FROM @HCLS_LAB.PUBLIC.HCLS_LAB_REPO/branches/main/tracks/p2_hedis_gaps/data/members.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO MEASURE_GAPS
  FROM @HCLS_LAB.PUBLIC.HCLS_LAB_REPO/branches/main/tracks/p2_hedis_gaps/data/measure_gaps.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO CLAIMS
  FROM @HCLS_LAB.PUBLIC.HCLS_LAB_REPO/branches/main/tracks/p2_hedis_gaps/data/claims.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO VISIT_NOTES
  FROM @HCLS_LAB.PUBLIC.HCLS_LAB_REPO/branches/main/tracks/p2_hedis_gaps/data/visit_notes.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

-- ============================================================
-- STEP 4: Verify the load
-- ============================================================
-- Expected counts: MEMBERS=2000, MEASURE_GAPS=~4800,
-- CLAIMS=15000, VISIT_NOTES=~2800.
-- If any table shows 0, check that 00_common.sql ran successfully.

SELECT 'MEMBERS' AS TABLE_NAME, COUNT(*) AS ROW_COUNT FROM MEMBERS
UNION ALL SELECT 'MEASURE_GAPS', COUNT(*) FROM MEASURE_GAPS
UNION ALL SELECT 'CLAIMS', COUNT(*) FROM CLAIMS
UNION ALL SELECT 'VISIT_NOTES', COUNT(*) FROM VISIT_NOTES;
