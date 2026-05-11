-- 09_cursors.sql

-- Anonymous block demonstrating a cursor to iterate over all accounts
-- and print those that have a balance over 10,000 to standard output
SET SERVEROUTPUT ON;

DECLARE
    CURSOR c_high_value_accounts IS
        SELECT a.account_number, c.customer_name, a.current_balance
        FROM ACCOUNT a
        JOIN CUSTOMER c ON a.ref_customer_id = c.customer_id
        WHERE a.current_balance >= 10000;
        
    v_acc_num ACCOUNT.account_number%TYPE;
    v_cust_name CUSTOMER.customer_name%TYPE;
    v_balance ACCOUNT.current_balance%TYPE;
BEGIN
    DBMS_OUTPUT.PUT_LINE('--- HIGH VALUE ACCOUNTS REPORT ---');
    
    OPEN c_high_value_accounts;
    LOOP
        FETCH c_high_value_accounts INTO v_acc_num, v_cust_name, v_balance;
        EXIT WHEN c_high_value_accounts%NOTFOUND;
        
        DBMS_OUTPUT.PUT_LINE('Account: ' || v_acc_num || ' | Customer: ' || v_cust_name || ' | Balance: $' || v_balance);
    END LOOP;
    CLOSE c_high_value_accounts;
    
    DBMS_OUTPUT.PUT_LINE('----------------------------------');
END;
/

-- Second anonymous block: Parameterized cursor, IF, EXCEPTION
DECLARE
    -- Parameterized cursor
    CURSOR c_branch_accounts(p_branch_code VARCHAR2) IS
        SELECT account_number, current_balance
        FROM ACCOUNT
        WHERE ref_branch_code = p_branch_code;
        
    v_acc ACCOUNT.account_number%TYPE;
    v_bal ACCOUNT.current_balance%TYPE;
    v_total_found NUMBER := 0;
    
    -- Custom exception
    e_no_accounts EXCEPTION;
BEGIN
    DBMS_OUTPUT.PUT_LINE('--- BRANCH ACCOUNTS REPORT ---');
    
    OPEN c_branch_accounts('LHR-001');
    LOOP
        FETCH c_branch_accounts INTO v_acc, v_bal;
        EXIT WHEN c_branch_accounts%NOTFOUND;
        
        v_total_found := v_total_found + 1;
        
        -- IF condition
        IF v_bal > 50000 THEN
            DBMS_OUTPUT.PUT_LINE('Account: ' || v_acc || ' (Premium) | Balance: $' || v_bal);
        ELSE
            DBMS_OUTPUT.PUT_LINE('Account: ' || v_acc || ' (Standard) | Balance: $' || v_bal);
        END IF;
    END LOOP;
    CLOSE c_branch_accounts;
    
    IF v_total_found = 0 THEN
        RAISE e_no_accounts;
    END IF;
    
EXCEPTION
    WHEN e_no_accounts THEN
        DBMS_OUTPUT.PUT_LINE('No accounts found for the specified branch.');
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('An unexpected error occurred: ' || SQLERRM);
END;
/
