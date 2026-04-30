-- Add password column to CUSTOMER table
ALTER TABLE CUSTOMER ADD password VARCHAR2(100);

-- Set default password for existing customers (using their phone number as temporary password)
UPDATE CUSTOMER SET password = phone;
COMMIT;

-- Unified login view for both Employees and Customers
-- Username field for customers will be their phone number
CREATE OR REPLACE VIEW vw_system_login AS
SELECT 
    employee_id AS user_id, 
    username, 
    password, 
    role, 
    ref_branch_code AS branch_code,
    username AS display_name,
    'EMPLOYEE' AS user_type
FROM EMPLOYEE
UNION ALL
SELECT 
    customer_id AS user_id, 
    phone AS username, 
    password, 
    'CUSTOMER' AS role, 
    NULL AS branch_code,
    customer_name AS display_name,
    'CUSTOMER' AS user_type
FROM CUSTOMER;
/
