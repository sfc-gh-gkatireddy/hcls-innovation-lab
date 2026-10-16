-- ============================================================
-- L2: Pharmacovigilance Signal Detection — Data Loader
-- ============================================================
-- This script loads the synthetic adverse event dataset from
-- the public GitHub repo into your Snowflake account.
--
-- PREREQUISITE: Run setup/00_common.sql first. It creates the
-- database (HCLS_LAB), warehouse, git repo connection and CSV
-- file format that this script depends on.
-- ============================================================

-- Switch to the lab database created by 00_common.sql
USE DATABASE HCLS_LAB;

-- ============================================================
-- STEP 1: Create a dedicated schema for the L2 track
-- ============================================================
CREATE SCHEMA IF NOT EXISTS L2_PHARMACOVIGILANCE;
USE SCHEMA L2_PHARMACOVIGILANCE;

-- ============================================================
-- STEP 2: Create the tables
-- ============================================================

-- Drug products (10 rows)
-- Synthetic products spanning cardiovascular, endocrine, autoimmune,
-- musculoskeletal, neurology, oncology and respiratory areas.
CREATE OR REPLACE TABLE PRODUCTS (
    PRODUCT_ID VARCHAR(20),          -- Unique product identifier (e.g. PROD-01)
    PRODUCT_NAME VARCHAR(100),       -- Brand name (e.g. Cardivex, Osteovance)
    ACTIVE_INGREDIENT VARCHAR(100),  -- Generic name
    THERAPEUTIC_AREA VARCHAR(50),    -- e.g. Cardiovascular, Oncology
    DESCRIPTION VARCHAR(500)         -- Brief description of the drug
);

-- Adverse event case reports (5,000 rows)
-- Modeled on FDA FAERS structure. Each case links a product to a
-- MedDRA-style preferred term (PT) and System Organ Class (SOC),
-- with seriousness, outcome, patient demographics and reporter info.
CREATE OR REPLACE TABLE AE_CASES (
    CASE_ID VARCHAR(20),             -- Unique case identifier (e.g. AE-00001)
    PRODUCT_ID VARCHAR(20),          -- FK to PRODUCTS
    PRODUCT_NAME VARCHAR(100),
    ACTIVE_INGREDIENT VARCHAR(100),
    DRUG_ROLE VARCHAR(5),            -- PS=Primary Suspect, SS=Secondary, C=Concomitant
    ROUTE_OF_ADMIN VARCHAR(20),      -- Oral, Intravenous, Subcutaneous, etc.
    REPORT_DATE DATE,                -- When the case was reported
    EVENT_DATE DATE,                 -- When the adverse event occurred
    PREFERRED_TERM VARCHAR(100),     -- MedDRA-style preferred term (e.g. Hepatotoxicity)
    SOC VARCHAR(50),                 -- System Organ Class (e.g. Hepatobiliary, Cardiac)
    SERIOUSNESS VARCHAR(20),         -- Serious or Non-Serious
    OUTCOME_CODE VARCHAR(5),         -- DE=Death, LT=Life-Threatening, HO=Hospitalization, etc.
    OUTCOME_DESCRIPTION VARCHAR(50),
    PATIENT_AGE INT,
    PATIENT_SEX VARCHAR(1),          -- M or F
    REPORTER_TYPE VARCHAR(30),       -- Physician, Pharmacist, Consumer, etc.
    REPORTER_COUNTRY VARCHAR(5),     -- ISO country code
    REPORT_QUARTER VARCHAR(10)       -- e.g. 2026Q2 — useful for trend analysis
);

-- Free-text case narratives (~460 rows)
-- Clinical narratives describing the adverse event, patient history,
-- lab findings and outcome. Teams will use AI_CLASSIFY to classify
-- seriousness and event type, and Cortex Search to let the agent
-- find and quote similar cases.
CREATE OR REPLACE TABLE CASE_NARRATIVES (
    CASE_ID VARCHAR(20),             -- FK to AE_CASES
    NARRATIVE_TYPE VARCHAR(20),      -- REPORTER or MANUFACTURER narrative
    NARRATIVE_TEXT VARCHAR(16777216)  -- Full case narrative text
);

-- ============================================================
-- STEP 3: Copy CSV files from the git repo to an internal stage
-- ============================================================
-- Snowflake cannot COPY INTO a table directly from a git repo
-- stage, so we first copy the files to an internal stage, then
-- load from there.

CREATE OR REPLACE STAGE L2_DATA;

COPY FILES
  INTO @L2_DATA
  FROM @HCLS_LAB.PUBLIC.HCLS_LAB_REPO/branches/main/tracks/l2_pharmacovigilance/data/;

-- ============================================================
-- STEP 4: Load data from the internal stage into tables
-- ============================================================

COPY INTO PRODUCTS FROM @L2_DATA/products.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO AE_CASES FROM @L2_DATA/ae_cases.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO CASE_NARRATIVES FROM @L2_DATA/case_narratives.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

-- ============================================================
-- STEP 5: Verify the load
-- ============================================================
-- Expected counts: PRODUCTS=10, AE_CASES=5000,
-- CASE_NARRATIVES=~460.
-- If any table shows 0, check that 00_common.sql ran successfully.

SELECT 'PRODUCTS' AS TABLE_NAME, COUNT(*) AS ROW_COUNT FROM PRODUCTS
UNION ALL SELECT 'AE_CASES', COUNT(*) FROM AE_CASES
UNION ALL SELECT 'CASE_NARRATIVES', COUNT(*) FROM CASE_NARRATIVES;
