-- ============================================================
-- L3: Commercial HCP 360 & Next Best Action — Data Loader
-- ============================================================
-- This script loads the synthetic pharma commercial dataset
-- (HCP master, monthly prescriptions, rep calls, call notes and
-- approved messaging) from the public GitHub repo.
--
-- PREREQUISITE: Run setup/00_common.sql first. It creates the
-- database (HCLS_LAB), warehouse, git repo connection and CSV
-- file format that this script depends on.
-- ============================================================

-- Switch to the lab database created by 00_common.sql
USE DATABASE HCLS_LAB;

-- ============================================================
-- STEP 1: Create a dedicated schema for the L3 track
-- ============================================================
CREATE SCHEMA IF NOT EXISTS L3_COMMERCIAL_HCP360;
USE SCHEMA L3_COMMERCIAL_HCP360;

-- ============================================================
-- STEP 2: Create the tables
-- ============================================================

-- Brands in the type 2 diabetes market (4 rows)
-- Glucavia is "our" brand; the others are competitors.
CREATE OR REPLACE TABLE BRANDS (
    BRAND_ID VARCHAR(10),            -- Unique brand identifier (e.g. BR-01)
    BRAND_NAME VARCHAR(50),          -- Glucavia, Sematra, Empaflo, Sitaglen
    MOLECULE_CLASS VARCHAR(50),      -- Molecule description
    DRUG_CLASS VARCHAR(20),          -- GLP-1 RA, SGLT2i, DPP-4i
    INDICATION VARCHAR(50),          -- Type 2 diabetes
    IS_OUR_BRAND VARCHAR(1)          -- Y = our brand, N = competitor
);

-- Sales territories and assigned reps (12 rows)
CREATE OR REPLACE TABLE TERRITORIES (
    TERRITORY_ID VARCHAR(10),        -- Unique territory identifier (e.g. T07)
    TERRITORY_NAME VARCHAR(50),      -- e.g. Pune West
    REGION VARCHAR(10),              -- North, South, East, West
    REP_NAME VARCHAR(50),            -- Assigned field representative
    REP_ID VARCHAR(10)               -- Unique rep identifier
);

-- Healthcare professional (HCP) master (2,000 rows)
CREATE OR REPLACE TABLE HCPS (
    HCP_ID VARCHAR(20),              -- Unique HCP identifier (e.g. HCP-00001)
    HCP_NAME VARCHAR(100),           -- Synthetic doctor name
    SPECIALTY VARCHAR(50),           -- Endocrinology, Internal Medicine, etc.
    TERRITORY_ID VARCHAR(10),        -- FK to TERRITORIES
    CITY VARCHAR(50),
    PRACTICE_SETTING VARCHAR(50),    -- Private clinic, Corporate hospital, etc.
    DECILE INT,                      -- 1-10 prescribing potential (10 = highest)
    TARGET_TIER VARCHAR(1),          -- A (deciles 8-10), B (5-7), C (1-4)
    YEARS_IN_PRACTICE INT
);

-- Monthly prescriptions per HCP per brand (96,000 rows)
-- Modeled on IQVIA-style prescriber-level data. 12 months:
-- Oct 2025 to Sep 2026.
CREATE OR REPLACE TABLE RX_MONTHLY (
    HCP_ID VARCHAR(20),              -- FK to HCPS
    BRAND_ID VARCHAR(10),            -- FK to BRANDS
    MONTH DATE,                      -- First day of the month
    TRX INT,                         -- Total prescriptions (new + refills)
    NRX INT,                         -- New prescriptions
    MARKET_TRX INT                   -- HCP's total T2D market TRx that month (all brands)
);

-- Field rep call activity from CRM (~10,450 rows)
CREATE OR REPLACE TABLE CALLS (
    CALL_ID VARCHAR(20),             -- Unique call identifier
    HCP_ID VARCHAR(20),              -- FK to HCPS
    REP_ID VARCHAR(10),              -- FK to TERRITORIES.REP_ID
    TERRITORY_ID VARCHAR(10),        -- FK to TERRITORIES
    CALL_DATE DATE,
    CHANNEL VARCHAR(20),             -- In-person, Remote video, Phone, Email
    BRAND_DETAILED VARCHAR(50),      -- Brand discussed on the call
    SAMPLES_DROPPED INT,             -- Number of sample packs left
    DURATION_MIN INT                 -- Call length in minutes
);

-- Free-text call notes written by reps (~1,460 rows)
-- This is the unstructured data for the AI step: objections,
-- competitor mentions and sentiment live only in this text.
CREATE OR REPLACE TABLE CALL_NOTES (
    NOTE_ID VARCHAR(20),             -- Unique note identifier
    CALL_ID VARCHAR(20),             -- FK to CALLS
    HCP_ID VARCHAR(20),              -- FK to HCPS
    TERRITORY_ID VARCHAR(10),        -- FK to TERRITORIES
    NOTE_DATE DATE,
    NOTE_TEXT VARCHAR(2000)          -- Rep's free-text summary of the call
);

-- Approved messaging and objection-handling documents (8 rows)
-- Use with Cortex Search so the agent can recommend what to say.
CREATE OR REPLACE TABLE MESSAGING_DOCS (
    DOC_ID VARCHAR(10),              -- Unique document identifier
    TITLE VARCHAR(200),              -- Document title
    CONTENT VARCHAR(5000)            -- Full document text
);

-- ============================================================
-- STEP 3: Copy CSV files from the git repo to an internal stage
-- ============================================================
-- Snowflake cannot COPY INTO a table directly from a git repo
-- stage, so we first copy the files to an internal stage, then
-- load from there.

CREATE OR REPLACE STAGE L3_DATA;

COPY FILES
  INTO @HCLS_LAB.L3_COMMERCIAL_HCP360.L3_DATA
  FROM @HCLS_LAB.PUBLIC.HCLS_LAB_REPO/branches/main/tracks/l3_commercial_hcp360/data/;

-- ============================================================
-- STEP 4: Load data from the internal stage into tables
-- ============================================================

COPY INTO BRANDS FROM @HCLS_LAB.L3_COMMERCIAL_HCP360.L3_DATA/brands.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO TERRITORIES FROM @HCLS_LAB.L3_COMMERCIAL_HCP360.L3_DATA/territories.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO HCPS FROM @HCLS_LAB.L3_COMMERCIAL_HCP360.L3_DATA/hcps.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO RX_MONTHLY FROM @HCLS_LAB.L3_COMMERCIAL_HCP360.L3_DATA/rx_monthly.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO CALLS FROM @HCLS_LAB.L3_COMMERCIAL_HCP360.L3_DATA/calls.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO CALL_NOTES FROM @HCLS_LAB.L3_COMMERCIAL_HCP360.L3_DATA/call_notes.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

COPY INTO MESSAGING_DOCS FROM @HCLS_LAB.L3_COMMERCIAL_HCP360.L3_DATA/messaging_docs.csv
  FILE_FORMAT = HCLS_LAB.PUBLIC.CSV_FORMAT;

-- ============================================================
-- STEP 5: Verify the load
-- ============================================================
-- Expected counts: BRANDS=4, TERRITORIES=12, HCPS=2000,
-- RX_MONTHLY=96000, CALLS=~10450, CALL_NOTES=~1460, MESSAGING_DOCS=8.
-- If any table shows 0, check that 00_common.sql ran successfully.

SELECT 'BRANDS' AS TABLE_NAME, COUNT(*) AS ROW_COUNT FROM BRANDS
UNION ALL SELECT 'TERRITORIES', COUNT(*) FROM TERRITORIES
UNION ALL SELECT 'HCPS', COUNT(*) FROM HCPS
UNION ALL SELECT 'RX_MONTHLY', COUNT(*) FROM RX_MONTHLY
UNION ALL SELECT 'CALLS', COUNT(*) FROM CALLS
UNION ALL SELECT 'CALL_NOTES', COUNT(*) FROM CALL_NOTES
UNION ALL SELECT 'MESSAGING_DOCS', COUNT(*) FROM MESSAGING_DOCS;
