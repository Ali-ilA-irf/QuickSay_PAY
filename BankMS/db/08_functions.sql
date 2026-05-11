-- 08_functions.sql

-- Function to get the total balance of a specific customer
CREATE OR REPLACE FUNCTION fn_get_customer_balance(p_customer_id NUMBER) 
RETURN NUMBER IS
    v_total NUMBER(15,2);
BEGIN
    SELECT NVL(SUM(current_balance), 0) INTO v_total
    FROM ACCOUNT
    WHERE ref_customer_id = p_customer_id;
    
    RETURN v_total;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN 0;
END fn_get_customer_balance;
/

-- Function to calculate expected monthly interest for a given loan
CREATE OR REPLACE FUNCTION fn_calc_monthly_loan_interest(p_loan_id NUMBER) 
RETURN NUMBER IS
    v_amount NUMBER(15,2);
    v_rate NUMBER(5,2);
    v_interest NUMBER(15,2);
BEGIN
    SELECT loan_amount, interest_rate INTO v_amount, v_rate
    FROM LOAN
    WHERE loan_id = p_loan_id;
    
    -- Simple interest calculation for one month (rate is annual percentage)
    v_interest := (v_amount * (v_rate / 100)) / 12;
    
    RETURN ROUND(v_interest, 2);
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RETURN 0;
END fn_calc_monthly_loan_interest;
/

-- Function to get the number of active cards for a customer
CREATE OR REPLACE FUNCTION fn_get_active_cards(p_customer_id NUMBER) 
RETURN NUMBER IS
    v_count NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM CARD cd
    JOIN ACCOUNT a ON cd.ref_account_id = a.account_id
    WHERE a.ref_customer_id = p_customer_id AND cd.card_status = 'ACTIVE' 
      AND cd.date_of_expiry >= SYSDATE;
    
    RETURN v_count;
EXCEPTION
    WHEN OTHERS THEN
        RETURN 0;
END fn_get_active_cards;
/
