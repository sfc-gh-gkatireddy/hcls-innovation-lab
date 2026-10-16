-- ============================================================
-- HCLS Innovation Lab: Common Setup
-- Run this ONCE before any track loader script.
-- ============================================================

-- 1. Warehouse (XS is plenty for synthetic data)
CREATE WAREHOUSE IF NOT EXISTS HCLS_LAB_WH
  WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 120
  AUTO_RESUME = TRUE;

USE WAREHOUSE HCLS_LAB_WH;

-- 2. Database
CREATE DATABASE IF NOT EXISTS HCLS_LAB;
USE DATABASE HCLS_LAB;

-- 3. Connect to the public GitHub repo
-- Update the URL below if the repo moves.
CREATE OR REPLACE API INTEGRATION HCLS_LAB_GIT_API
  API_PROVIDER = git_https_api
  API_ALLOWED_PREFIXES = ('https://github.com/gkatireddy')
  ENABLED = TRUE;

CREATE OR REPLACE GIT REPOSITORY HCLS_LAB.PUBLIC.HCLS_LAB_REPO
  API_INTEGRATION = HCLS_LAB_GIT_API
  ORIGIN = 'https://github.com/gkatireddy/hcls-innovation-lab.git';

-- Fetch latest
ALTER GIT REPOSITORY HCLS_LAB.PUBLIC.HCLS_LAB_REPO FETCH;

-- 4. File format for CSVs
CREATE OR REPLACE FILE FORMAT HCLS_LAB.PUBLIC.CSV_FORMAT
  TYPE = 'CSV'
  FIELD_OPTIONALLY_ENCLOSED_BY = '"'
  SKIP_HEADER = 1
  NULL_IF = ('')
  EMPTY_FIELD_AS_NULL = TRUE;

-- 5. Cross-region AI (needed if the trial account is in a region
--    without full Cortex model availability)
-- Uncomment the line below if AI functions return a region error:
-- ALTER ACCOUNT SET CORTEX_ENABLED_CROSS_REGION = 'ANY_REGION';

-- ============================================================
-- You are ready. Now run ONE of the track loader scripts:
--   setup/load_p1_claims_denials.sql
--   setup/load_p2_hedis_gaps.sql
--   setup/load_l1_trial_matching.sql
--   setup/load_l2_pharmacovigilance.sql
-- ============================================================
