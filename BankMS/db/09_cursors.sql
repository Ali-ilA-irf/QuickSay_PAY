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
