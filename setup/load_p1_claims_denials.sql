-- ============================================================
-- P1: Claims Denial Triage Agent — Data Loader
-- ============================================================
-- This script loads the synthetic claims-denial dataset from
-- the public GitHub repo into your Snowflake account.
--
-- PREREQUISITE: Run setup/00_common.sql first. It creates the
-- database (HCLS_LAB), warehouse, git repo connection and CSV
-- file format that this script depends on.
-- ============================================================

-- Switch to the lab database created by 00_common.sql
USE DATABASE HCLS_LAB;

-- ============================================================
-- STEP 1: Create a dedicated schema for the P1 track
-- ============================================================
-- Each track gets its own schema so tables don't collide if
-- multiple teams share one account.
CREATE SCHEMA IF NOT EXISTS P1_CLAIMS_DENIALS;
USE SCHEMA P1_CLAIMS_DENIALS;

-- ============================================================
-- STEP 2: Create the tables
-- ============================================================

-- Health plan members (2,000 rows)
-- Each member belongs to a plan, group and payer.
CREATE OR REPLACE TABLE MEMBERS (
    MEMBER_ID VARCHAR(20),       -- Unique member identifier (e.g. MBR-00001)
    FIRST_NAME VARCHAR(50),
    LAST_NAME VARCHAR(50),
    DOB DATE,                    -- Date of birth
    GENDER VARCHAR(1),           -- M or F
    STATE VARCHAR(2),            -- US state abbreviation
    ZIP VARCHAR(10),
    PLAN_ID VARCHAR(20),         -- e.g. PREMIER-500, VALUE-250
    PLAN_TYPE VARCHAR(10),       -- PPO, HMO, EPO, etc.
    GROUP_NUMBER VARCHAR(20),    -- Employer group
    PAYER_ID VARCHAR(20),        -- Links to PAYER_POLICIES
    EFFECTIVE_DATE DATE,         -- Coverage start date
    TERM_DATE DATE               -- NULL if still active
);

-- Healthcare providers (200 rows)
-- Includes specialty and network status for denial analysis.
CREATE OR REPLACE TABLE PROVIDERS (
    PROVIDER_ID VARCHAR(20),     -- Unique provider identifier (e.g. PRV-00001)
    PROVIDER_NPI VARCHAR(15),    -- National Provider Identifier
    PROVIDER_NAME VARCHAR(100),
    SPECIALTY VARCHAR(50),       -- e.g. Orthopedics, Cardiology
    FACILITY_NAME VARCHAR(100),
    STATE VARCHAR(2),
    NETWORK_STATUS VARCHAR(5)    -- IN or OUT of network
);

-- Medical claims (20,000 rows)
-- Each claim has a status (PAID or DENIED). Denied claims carry
-- a CARC denial code, a human-readable reason, a category and a
-- flag indicating whether the denial was preventable.
CREATE OR REPLACE TABLE CLAIMS (
    CLAIM_ID VARCHAR(20),
    MEMBER_ID VARCHAR(20),       -- FK to MEMBERS
    PROVIDER_ID VARCHAR(20),     -- FK to PROVIDERS
    PROVIDER_NPI VARCHAR(15),
    PROVIDER_NAME VARCHAR(100),
    FACILITY_NAME VARCHAR(100),
    PAYER_ID VARCHAR(20),
    DATE_OF_SERVICE DATE,
    CLAIM_TYPE VARCHAR(20),      -- Professional or Institutional
    PLACE_OF_SERVICE VARCHAR(5), -- CMS place-of-service code
    PRIMARY_DIAGNOSIS VARCHAR(10),    -- ICD-10-CM code
    DIAGNOSIS_DESCRIPTION VARCHAR(200),
    DIAGNOSIS_CATEGORY VARCHAR(50),   -- e.g. Musculoskeletal, Cardiovascular
    CPT_CODE VARCHAR(10),             -- Procedure code
    CPT_DESCRIPTION VARCHAR(200),
    TOTAL_BILLED NUMBER(12,2),
    TOTAL_ALLOWED NUMBER(12,2),
    TOTAL_PAID NUMBER(12,2),          -- 0.00 if denied
    STATUS VARCHAR(10),               -- PAID or DENIED
    DENIAL_CODE VARCHAR(10),          -- CARC code (e.g. CO-197) — empty if paid
    DENIAL_REASON VARCHAR(500),       -- Human-readable reason — empty if paid
    DENIAL_CATEGORY VARCHAR(50),      -- e.g. Missing Authorization, Coding Error
    IS_PREVENTABLE BOOLEAN            -- TRUE if the denial could have been avoided
);

-- Free-text denial notes (~2,800 rows, one per denied claim)
-- These are the unstructured text that AI_CLASSIFY will process
-- to label root causes and preventability.
CREATE OR REPLACE TABLE DENIAL_NOTES (
    DENIAL_NOTE_ID VARCHAR(20),
    CLAIM_ID VARCHAR(20),         -- FK to CLAIMS
    NOTE_DATE DATE,               -- When the note was written
    DENIAL_CODE VARCHAR(10),      -- CARC code for reference
    NOTE_TEXT VARCHAR(16777216)    -- The full adjudication note text
);

-- Payer policy documents (5 rows)
-- Short policy texts covering prior auth, timely filing, medical
-- necessity, coding guidelines and appeals process. These will be
-- indexed by Cortex Search so the agent can cite policy language.
CREATE OR REPLACE TABLE PAYER_POLICIES (
    POLICY_ID VARCHAR(20),
    PAYER_ID VARCHAR(20),         -- Which payer this policy belongs to
    POLICY_TITLE VARCHAR(200),    -- e.g. "Prior Authorization Requirements"
    POLICY_TEXT VARCHAR(16777216)  -- Full policy document text
);

-- ============================================================
-- STEP 3: Copy CSV files from the git repo to an internal stage
-- ============================================================
-- Snowflake cannot COPY INTO a table directly from a git repo
-- stage, so we first copy the files to an internal stage, then
-- load from there.

CREATE OR REPLACE STAGE P1_DATA;

COPY FILES
  INTO @P1_DATA
  FROM @HCLS_LAB.PUBLIC.HCLS_LAB_REPO/branches/main/tracks/p1_claims_denials/data/;

-- ============================================================
-- STEP 4: Load data from the internal stage into tables
-- ============================================================

COPY INTO MEMBERS FROM @P1_DATA/members.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO PROVIDERS FROM @P1_DATA/providers.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO CLAIMS FROM @P1_DATA/claims.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO DENIAL_NOTES FROM @P1_DATA/denial_notes.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO PAYER_POLICIES FROM @P1_DATA/payer_policies.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

-- ============================================================
-- STEP 5: Verify the load
-- ============================================================
-- Expected counts: MEMBERS=2000, PROVIDERS=200, CLAIMS=20000,
-- DENIAL_NOTES=~2800, PAYER_POLICIES=5.
-- If any table shows 0, check that 00_common.sql ran successfully.

SELECT 'MEMBERS' AS TABLE_NAME, COUNT(*) AS ROW_COUNT FROM MEMBERS
UNION ALL SELECT 'PROVIDERS', COUNT(*) FROM PROVIDERS
UNION ALL SELECT 'CLAIMS', COUNT(*) FROM CLAIMS
UNION ALL SELECT 'DENIAL_NOTES', COUNT(*) FROM DENIAL_NOTES
UNION ALL SELECT 'PAYER_POLICIES', COUNT(*) FROM PAYER_POLICIES;
