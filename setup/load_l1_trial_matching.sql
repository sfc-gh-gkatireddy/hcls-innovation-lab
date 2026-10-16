-- ============================================================
-- L1: Clinical Trial Patient/Site Matching — Data Loader
-- ============================================================
-- This script loads the synthetic clinical trial dataset from
-- the public GitHub repo into your Snowflake account, including
-- a trial protocol document staged for AI_PARSE_DOCUMENT.
--
-- PREREQUISITE: Run setup/00_common.sql first. It creates the
-- database (HCLS_LAB), warehouse, git repo connection and CSV
-- file format that this script depends on.
-- ============================================================

-- Switch to the lab database created by 00_common.sql
USE DATABASE HCLS_LAB;

-- ============================================================
-- STEP 1: Create a dedicated schema for the L1 track
-- ============================================================
CREATE SCHEMA IF NOT EXISTS L1_TRIAL_MATCHING;
USE SCHEMA L1_TRIAL_MATCHING;

-- ============================================================
-- STEP 2: Create the tables
-- ============================================================

-- Candidate patients (5,000 rows)
-- Each patient is affiliated with a site. ~35% have Type 2 diabetes.
CREATE OR REPLACE TABLE PATIENTS (
    PATIENT_ID VARCHAR(20),      -- Unique patient identifier (e.g. PAT-00001)
    SITE_ID VARCHAR(20),         -- FK to SITES — which trial site this patient is at
    AGE INT,
    SEX VARCHAR(1),              -- M or F
    RACE VARCHAR(20),
    COUNTRY VARCHAR(5)           -- ISO country code (US, IN, GB, DE, etc.)
);

-- Patient diagnoses (~11,000 rows)
-- ICD-10 coded conditions. Patients with E11.x codes have Type 2 diabetes.
CREATE OR REPLACE TABLE DIAGNOSES (
    PATIENT_ID VARCHAR(20),      -- FK to PATIENTS
    DIAGNOSIS_CODE VARCHAR(10),  -- ICD-10-CM code (e.g. E11.9, I10)
    DIAGNOSIS_DESCRIPTION VARCHAR(200),
    DIAGNOSIS_DATE DATE,
    STATUS VARCHAR(10)           -- Active or Resolved
);

-- Lab results (20,000 rows — 4 labs per patient)
-- Key labs for trial eligibility: HbA1c, eGFR, ALT, Creatinine.
-- Each row includes the normal reference range for comparison.
CREATE OR REPLACE TABLE LABS (
    PATIENT_ID VARCHAR(20),      -- FK to PATIENTS
    LAB_CODE VARCHAR(20),        -- e.g. HBA1C, EGFR, ALT, CREATININE
    LAB_NAME VARCHAR(100),       -- Human-readable lab name
    VALUE NUMBER(10,2),          -- The measured value
    UNIT VARCHAR(30),            -- e.g. %, mL/min/1.73m2, U/L, mg/dL
    LAB_DATE DATE,
    NORMAL_LOW NUMBER(10,2),     -- Lower bound of normal range
    NORMAL_HIGH NUMBER(10,2)     -- Upper bound of normal range
);

-- Current medications (~8,600 rows)
-- Includes diabetes drugs (metformin, insulin, GLP-1 RAs, SGLT2i) and
-- common co-medications. Protocol exclusion EC-2 bars GLP-1 RA, SGLT2i
-- and insulin use within 12 weeks of screening.
CREATE OR REPLACE TABLE MEDICATIONS (
    PATIENT_ID VARCHAR(20),      -- FK to PATIENTS
    MEDICATION_NAME VARCHAR(100),
    MEDICATION_CLASS VARCHAR(50), -- e.g. Metformin, GLP-1 RA, Basal Insulin
    ROUTE VARCHAR(20),           -- Oral, Subcutaneous, etc.
    FREQUENCY VARCHAR(10),       -- QD, BID, QW
    STATUS VARCHAR(10),          -- Active or Discontinued
    START_DATE DATE
);

-- Trial sites (40 rows)
-- Sites across US, India, Europe and Asia-Pacific. Volume tells you
-- how many patients the site sees per year.
CREATE OR REPLACE TABLE SITES (
    SITE_ID VARCHAR(20),         -- Unique site identifier (e.g. SITE-01)
    SITE_NAME VARCHAR(100),
    CITY VARCHAR(50),
    STATE VARCHAR(5),
    COUNTRY VARCHAR(5),
    ANNUAL_PATIENT_VOLUME INT    -- Approximate patients per year
);

-- ============================================================
-- STEP 3: Create an internal stage for the protocol document
-- ============================================================
-- The protocol is a text file with the full Phase 3 trial design,
-- including inclusion/exclusion criteria (Sections 3.1 and 3.2).
-- We copy it to an internal stage so AI_PARSE_DOCUMENT and
-- Cortex Search can access it.
CREATE OR REPLACE STAGE L1_DOCS;

-- ============================================================
-- STEP 4: Load structured data from the GitHub repo
-- ============================================================
-- The COPY INTO commands read CSV files directly from the git
-- repository stage created in 00_common.sql.

COPY INTO PATIENTS
  FROM @HCLS_LAB.PUBLIC.HCLS_LAB_REPO/branches/main/tracks/l1_trial_matching/data/patients.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO DIAGNOSES
  FROM @HCLS_LAB.PUBLIC.HCLS_LAB_REPO/branches/main/tracks/l1_trial_matching/data/diagnoses.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO LABS
  FROM @HCLS_LAB.PUBLIC.HCLS_LAB_REPO/branches/main/tracks/l1_trial_matching/data/labs.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO MEDICATIONS
  FROM @HCLS_LAB.PUBLIC.HCLS_LAB_REPO/branches/main/tracks/l1_trial_matching/data/medications.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO SITES
  FROM @HCLS_LAB.PUBLIC.HCLS_LAB_REPO/branches/main/tracks/l1_trial_matching/data/sites.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

-- ============================================================
-- STEP 5: Copy the protocol document to the internal stage
-- ============================================================
-- COPY FILES moves the protocol text file from the git repo stage
-- into the internal stage @L1_DOCS. This is needed because
-- AI_PARSE_DOCUMENT reads from internal or external stages, not
-- directly from git repo stages.

COPY FILES
  INTO @L1_DOCS
  FROM @HCLS_LAB.PUBLIC.HCLS_LAB_REPO/branches/main/tracks/l1_trial_matching/docs/;

-- ============================================================
-- STEP 6: Verify the load
-- ============================================================
-- Expected counts: PATIENTS=5000, DIAGNOSES=~11000, LABS=20000,
-- MEDICATIONS=~8600, SITES=40.
-- If any table shows 0, check that 00_common.sql ran successfully.

SELECT 'PATIENTS' AS TABLE_NAME, COUNT(*) AS ROW_COUNT FROM PATIENTS
UNION ALL SELECT 'DIAGNOSES', COUNT(*) FROM DIAGNOSES
UNION ALL SELECT 'LABS', COUNT(*) FROM LABS
UNION ALL SELECT 'MEDICATIONS', COUNT(*) FROM MEDICATIONS
UNION ALL SELECT 'SITES', COUNT(*) FROM SITES;

-- Verify the protocol document was staged successfully.
-- You should see one file: protocol_SNF2847_T2D_301.txt
LIST @L1_DOCS;
