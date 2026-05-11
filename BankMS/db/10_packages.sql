-- 10_packages.sql

-- Package Specification
CREATE OR REPLACE PACKAGE pkg_bank_reports AS
    -- Package level constant
    c_bank_name CONSTANT VARCHAR2(50) := 'QuickSay PAY Bank';
    
    PROCEDURE generate_branch_summary(p_branch_code IN VARCHAR2);
    PROCEDURE print_customer_info(p_customer_id IN NUMBER);
    FUNCTION get_total_loans_given RETURN NUMBER;
END pkg_bank_reports;
/

-- Package Body
CREATE OR REPLACE PACKAGE BODY pkg_bank_reports AS

    PROCEDURE generate_branch_summary(p_branch_code IN VARCHAR2) IS
        v_total_deposits NUMBER;
        v_total_accounts NUMBER;
    BEGIN
        SELECT total_deposits, total_accounts 
        INTO v_total_deposits, v_total_accounts
        FROM vw_branch_summary
        WHERE branch_code = p_branch_code;
        
        DBMS_OUTPUT.PUT_LINE('Branch: ' || p_branch_code);
        DBMS_OUTPUT.PUT_LINE('Total Accounts: ' || v_total_accounts);
        DBMS_OUTPUT.PUT_LINE('Total Deposits: $' || v_total_deposits);
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            DBMS_OUTPUT.PUT_LINE('Branch ' || p_branch_code || ' not found.');
    END generate_branch_summary;

    FUNCTION get_total_loans_given RETURN NUMBER IS
        v_total NUMBER;
    BEGIN
        SELECT NVL(SUM(loan_amount), 0) INTO v_total
        FROM LOAN
        WHERE approval_status = 'APPROVED';
        RETURN v_total;
    END get_total_loans_given;

    PROCEDURE print_customer_info(p_customer_id IN NUMBER) IS
        v_name VARCHAR2(100);
        v_phone VARCHAR2(20);
    BEGIN
        SELECT customer_name, phone INTO v_name, v_phone
        FROM CUSTOMER
        WHERE customer_id = p_customer_id;
        
        DBMS_OUTPUT.PUT_LINE('Bank Name: ' || c_bank_name);
        DBMS_OUTPUT.PUT_LINE('Customer Name: ' || v_name);
        DBMS_OUTPUT.PUT_LINE('Phone: ' || v_phone);
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            DBMS_OUTPUT.PUT_LINE('Customer ' || p_customer_id || ' not found.');
    END print_customer_info;

END pkg_bank_reports;
/

-- Demonstration of Package execution
SET SERVEROUTPUT ON;
BEGIN
    DBMS_OUTPUT.PUT_LINE('--- PACKAGE DEMONSTRATION ---');
    pkg_bank_reports.generate_branch_summary('LHR-001');
    pkg_bank_reports.print_customer_info(1);
    DBMS_OUTPUT.PUT_LINE('Total Loans Given: $' || pkg_bank_reports.get_total_loans_given());
    DBMS_OUTPUT.PUT_LINE('-----------------------------');
END;
/
