-- ============================================================
-- L4: Real World Evidence — Treatment Patterns on OMOP — Data Loader
-- ============================================================
-- This script loads a synthetic real-world dataset shaped like the
-- OMOP Common Data Model (CDM v5.4) from the public GitHub repo.
-- 3,000 adults with type 2 diabetes, their conditions, drug
-- exposures, lab measurements, visits and clinical progress notes.
--
-- PREREQUISITE: Run setup/00_common.sql first. It creates the
-- database (HCLS_LAB), warehouse, git repo connection and CSV
-- file format that this script depends on.
-- ============================================================

-- Switch to the lab database created by 00_common.sql
USE DATABASE HCLS_LAB;

-- ============================================================
-- STEP 1: Create a dedicated schema for the L4 track
-- ============================================================
CREATE SCHEMA IF NOT EXISTS L4_RWE_TREATMENT_PATTERNS;
USE SCHEMA L4_RWE_TREATMENT_PATTERNS;

-- ============================================================
-- STEP 2: Create the tables (simplified OMOP CDM v5.4)
-- ============================================================

-- One row per patient (3,000 rows) — OMOP PERSON
CREATE OR REPLACE TABLE PERSON (
    PERSON_ID INT,                   -- Unique patient identifier
    GENDER_CONCEPT_ID INT,           -- OMOP concept: 8507 = male, 8532 = female
    GENDER VARCHAR(1),               -- M or F (readable copy of the concept)
    YEAR_OF_BIRTH INT,
    AGE_AT_INDEX INT,                -- Age at start of the study period
    STATE VARCHAR(50)                -- Indian state of residence
);

-- Diagnoses (~9,200 rows) — OMOP CONDITION_OCCURRENCE
CREATE OR REPLACE TABLE CONDITION_OCCURRENCE (
    CONDITION_OCCURRENCE_ID INT,     -- Unique row identifier
    PERSON_ID INT,                   -- FK to PERSON
    CONDITION_CONCEPT_ID INT,        -- OMOP standard concept (e.g. 201826 = T2DM)
    CONDITION_SOURCE_VALUE VARCHAR(10), -- Source ICD-10 code (e.g. E11.9)
    CONDITION_NAME VARCHAR(100),     -- Readable condition name
    CONDITION_START_DATE DATE        -- First recorded diagnosis date
);

-- Medication exposures (6,000 rows) — OMOP DRUG_EXPOSURE
-- Line 1 is metformin for everyone; line 2 is the add-on therapy
-- (Glucavia, Sematra, Empaflo or Sitaglen).
CREATE OR REPLACE TABLE DRUG_EXPOSURE (
    DRUG_EXPOSURE_ID INT,            -- Unique row identifier
    PERSON_ID INT,                   -- FK to PERSON
    DRUG_CONCEPT_ID INT,             -- OMOP concept (99000xxx = local concept for fictional brands)
    DRUG_NAME VARCHAR(50),           -- Readable drug name
    DRUG_CLASS VARCHAR(30),          -- Biguanide, GLP-1 RA, SGLT2 inhibitor, DPP-4 inhibitor
    DRUG_EXPOSURE_START_DATE DATE,   -- Therapy start
    DRUG_EXPOSURE_END_DATE DATE,     -- Therapy end (2026-09-30 = still on therapy at data cut)
    DAYS_SUPPLY INT,                 -- Days per fill
    LINE_OF_THERAPY INT,             -- 1 = first line, 2 = add-on
    STOP_REASON_STRUCTURED VARCHAR(50) -- Coded stop reason; mostly empty, as in real EHR data
);

-- Lab results and vitals (15,000 rows) — OMOP MEASUREMENT
CREATE OR REPLACE TABLE MEASUREMENT (
    MEASUREMENT_ID INT,              -- Unique row identifier
    PERSON_ID INT,                   -- FK to PERSON
    MEASUREMENT_CONCEPT_ID INT,      -- OMOP concept (3004410 = HbA1c, 3038553 = BMI, 3049187 = eGFR)
    MEASUREMENT_NAME VARCHAR(20),    -- HbA1c, BMI or eGFR
    MEASUREMENT_DATE DATE,
    VALUE_AS_NUMBER FLOAT,           -- Result value
    UNIT VARCHAR(20)                 -- %, kg/m2, mL/min/1.73m2
);

-- Outpatient visits (6,000 rows) — OMOP VISIT_OCCURRENCE
CREATE OR REPLACE TABLE VISIT_OCCURRENCE (
    VISIT_OCCURRENCE_ID INT,         -- Unique row identifier
    PERSON_ID INT,                   -- FK to PERSON
    VISIT_TYPE VARCHAR(20),          -- Outpatient
    VISIT_START_DATE DATE
);

-- Clinical progress notes (~2,700 rows) — OMOP NOTE
-- This is the unstructured data for the AI step: the real reasons
-- patients stop therapy (and titration details) live only in this text.
CREATE OR REPLACE TABLE NOTE (
    NOTE_ID INT,                     -- Unique note identifier
    PERSON_ID INT,                   -- FK to PERSON
    NOTE_DATE DATE,
    NOTE_TYPE VARCHAR(30),           -- Progress note
    NOTE_TEXT VARCHAR(2000)          -- Free-text clinician note
);

-- ============================================================
-- STEP 3: Copy CSV files from the git repo to an internal stage
-- ============================================================
-- Snowflake cannot COPY INTO a table directly from a git repo
-- stage, so we first copy the files to an internal stage, then
-- load from there.

CREATE OR REPLACE STAGE L4_DATA;

COPY FILES
  INTO @HCLS_LAB.L4_RWE_TREATMENT_PATTERNS.L4_DATA
  FROM @HCLS_LAB.PUBLIC.HCLS_LAB_REPO/branches/main/tracks/l4_rwe_treatment_patterns/data/;

-- ============================================================
-- STEP 4: Load data from the internal stage into tables
-- ============================================================

COPY INTO PERSON FROM @HCLS_LAB.L4_RWE_TREATMENT_PATTERNS.L4_DATA/person.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO CONDITION_OCCURRENCE FROM @HCLS_LAB.L4_RWE_TREATMENT_PATTERNS.L4_DATA/condition_occurrence.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO DRUG_EXPOSURE FROM @HCLS_LAB.L4_RWE_TREATMENT_PATTERNS.L4_DATA/drug_exposure.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO MEASUREMENT FROM @HCLS_LAB.L4_RWE_TREATMENT_PATTERNS.L4_DATA/measurement.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO VISIT_OCCURRENCE FROM @HCLS_LAB.L4_RWE_TREATMENT_PATTERNS.L4_DATA/visit_occurrence.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO NOTE FROM @HCLS_LAB.L4_RWE_TREATMENT_PATTERNS.L4_DATA/note.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

-- ============================================================
-- STEP 5: Verify the load
-- ============================================================
-- Expected counts: PERSON=3000, CONDITION_OCCURRENCE=~9240,
-- DRUG_EXPOSURE=6000, MEASUREMENT=15000, VISIT_OCCURRENCE=6000,
-- NOTE=~2730.
-- If any table shows 0, check that 00_common.sql ran successfully.

SELECT 'PERSON' AS TABLE_NAME, COUNT(*) AS ROW_COUNT FROM PERSON
UNION ALL SELECT 'CONDITION_OCCURRENCE', COUNT(*) FROM CONDITION_OCCURRENCE
UNION ALL SELECT 'DRUG_EXPOSURE', COUNT(*) FROM DRUG_EXPOSURE
UNION ALL SELECT 'MEASUREMENT', COUNT(*) FROM MEASUREMENT
UNION ALL SELECT 'VISIT_OCCURRENCE', COUNT(*) FROM VISIT_OCCURRENCE
UNION ALL SELECT 'NOTE', COUNT(*) FROM NOTE;
