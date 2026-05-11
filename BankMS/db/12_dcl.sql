-- 12_dcl.sql

-- In Oracle 11g, creating users requires DBA privileges
-- Run this script as SYSTEM or SYSDBA

-- Create standard roles
CREATE ROLE bank_admin_role;
CREATE ROLE bank_manager_role;
CREATE ROLE bank_teller_role;

-- Grant system privileges to roles
GRANT CREATE SESSION TO bank_admin_role, bank_manager_role, bank_teller_role;

-- Admin has full access to all tables
GRANT ALL PRIVILEGES ON BRANCH TO bank_admin_role;
GRANT ALL PRIVILEGES ON EMPLOYEE TO bank_admin_role;
GRANT ALL PRIVILEGES ON CUSTOMER TO bank_admin_role;
GRANT ALL PRIVILEGES ON ACCOUNT TO bank_admin_role;
GRANT ALL PRIVILEGES ON CARD TO bank_admin_role;
GRANT ALL PRIVILEGES ON BENEFICIARY TO bank_admin_role;
GRANT ALL PRIVILEGES ON TRANSACTION TO bank_admin_role;
GRANT ALL PRIVILEGES ON LOAN TO bank_admin_role;
GRANT ALL PRIVILEGES ON LOAN_PAY TO bank_admin_role;
GRANT ALL PRIVILEGES ON AUDIT_LOG TO bank_admin_role;

-- Teller has limited access (can select, insert, update specific tables, no deletes)
GRANT SELECT, INSERT, UPDATE ON CUSTOMER TO bank_teller_role;
GRANT SELECT, INSERT, UPDATE ON ACCOUNT TO bank_teller_role;
GRANT SELECT, INSERT ON TRANSACTION TO bank_teller_role;
GRANT SELECT ON BRANCH TO bank_teller_role;

-- Create actual database users (Schema names)
-- Oracle 11g does not require c## prefix for local users unless using container DBs (which is 12c+)
CREATE USER admin_user IDENTIFIED BY admin123;
CREATE USER teller_user IDENTIFIED BY teller123;

-- Assign roles to users
GRANT bank_admin_role TO admin_user;
GRANT bank_teller_role TO teller_user;

-- Demonstrate REVOKE
REVOKE bank_admin_role FROM admin_user;
GRANT bank_admin_role TO admin_user; -- grant it back so system keeps working

-- Demonstration of REVOKE
REVOKE SELECT ON BRANCH FROM bank_teller_role;
GRANT SELECT ON BRANCH TO bank_teller_role; -- Re-granting to keep application functional
