-- 10_packages.sql

-- Package Specification
CREATE OR REPLACE PACKAGE pkg_bank_reports AS
    PROCEDURE generate_branch_summary(p_branch_code IN VARCHAR2);
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

END pkg_bank_reports;
/
