-- ============================================================
-- 07_procedures.sql
-- ALL stored procedures for the Bank Management System.
-- Run once: @07_procedures.sql
-- Python models call via: db.call_procedure('pr_name', [...])
-- ============================================================


-- ════════════════════════════════════════════════════════════
-- SECTION 1: ORIGINAL PROCEDURES
-- ════════════════════════════════════════════════════════════

-- Transfer funds between accounts
CREATE OR REPLACE PROCEDURE pr_transfer_funds (
    p_from_account_id   IN NUMBER,
    p_from_branch_code  IN VARCHAR2,
    p_to_account_number IN VARCHAR2,   -- accepts account_number OR beneficiary IBAN
    p_amount            IN NUMBER,
    p_employee_id       IN NUMBER DEFAULT NULL
) AS
    v_cust_id     NUMBER;
    v_balance     NUMBER;
    v_resolved    VARCHAR2(20);        -- resolved internal account_number
BEGIN
    -- Fetch sender details
    SELECT ref_customer_id, current_balance INTO v_cust_id, v_balance
    FROM ACCOUNT WHERE account_id = p_from_account_id;

    IF v_balance < p_amount THEN
        RAISE_APPLICATION_ERROR(-20002, 'Insufficient balance for transfer.');
    END IF;

    -- Resolve receiving account: try direct account_number match first
    BEGIN
        SELECT account_number INTO v_resolved
        FROM ACCOUNT
        WHERE account_number = p_to_account_number
        AND ROWNUM = 1;
    EXCEPTION
        WHEN NO_DATA_FOUND THEN
            -- Treat as external transfer to IBAN
            v_resolved := p_to_account_number;
    END;

    -- Debit sender
    UPDATE ACCOUNT SET current_balance = current_balance - p_amount
    WHERE account_id = p_from_account_id;

    -- Credit receiver (only if it's an internal account)
    IF v_resolved != p_to_account_number OR p_to_account_number LIKE 'ACC-%' THEN
        UPDATE ACCOUNT SET current_balance = current_balance + p_amount
        WHERE account_number = v_resolved;
    END IF;

    INSERT INTO TRANSACTION (
        ref_customer_id, ref_branch_code,
        transaction_type, transaction_amount, receiving_account
    ) VALUES (
        v_cust_id, p_from_branch_code,
        'TRANSFER', p_amount, v_resolved
    );


    IF p_employee_id IS NOT NULL THEN
        INSERT INTO AUDIT_LOG (description, ref_employee_id)
        VALUES ('Transferred PKR ' || p_amount || ' to ' || v_resolved, p_employee_id);
    END IF;

    COMMIT;
EXCEPTION
    WHEN OTHERS THEN ROLLBACK; RAISE;
END pr_transfer_funds;
/

-- Approve a pending loan and deposit funds into account
CREATE OR REPLACE PROCEDURE pr_approve_loan (
    p_loan_id     IN NUMBER,
    p_employee_id IN NUMBER
) AS
    v_account_id  NUMBER;
    v_loan_amount NUMBER;
BEGIN
    SELECT ref_account_id, loan_amount
    INTO v_account_id, v_loan_amount
    FROM LOAN
    WHERE loan_id = p_loan_id AND approval_status = 'PENDING';

    UPDATE LOAN SET approval_status = 'APPROVED' WHERE loan_id = p_loan_id;

    UPDATE ACCOUNT
    SET current_balance = current_balance + v_loan_amount
    WHERE account_id = v_account_id;

    INSERT INTO AUDIT_LOG (description, ref_employee_id)
    VALUES ('Loan ' || p_loan_id || ' approved and funds deposited.', p_employee_id);

    COMMIT;
EXCEPTION
    WHEN NO_DATA_FOUND THEN
        RAISE_APPLICATION_ERROR(-20010, 'Loan not found or already processed.');
    WHEN OTHERS THEN ROLLBACK; RAISE;
END pr_approve_loan;
/

-- Create a new customer and their first account in one transaction
CREATE OR REPLACE PROCEDURE pr_create_account (
    p_customer_name   IN  VARCHAR2,
    p_phone           IN  VARCHAR2,
    p_password        IN  VARCHAR2,
    p_branch_code     IN  VARCHAR2,
    p_initial_deposit IN  NUMBER,
    p_account_number  OUT VARCHAR2
) AS
    v_customer_id NUMBER;
BEGIN
    INSERT INTO CUSTOMER (customer_name, phone, password)
    VALUES (p_customer_name, p_phone, p_password)
    RETURNING customer_id INTO v_customer_id;

    p_account_number := 'ACC-' || TO_CHAR(SYSDATE, 'YYYYMMDD') || seq_account_id.NEXTVAL;

    INSERT INTO ACCOUNT (account_number, ref_customer_id, ref_branch_code,
                         date_of_creation, current_balance)
    VALUES (p_account_number, v_customer_id, p_branch_code, SYSDATE, p_initial_deposit);

    COMMIT;
EXCEPTION
    WHEN OTHERS THEN ROLLBACK; RAISE;
END pr_create_account;
/

-- Procedure demonstrating NESTED CALLS (calls pr_open_account inside)
CREATE OR REPLACE PROCEDURE pr_customer_onboarding (
    p_name        IN VARCHAR2,
    p_address     IN VARCHAR2,
    p_phone       IN VARCHAR2,
    p_password    IN VARCHAR2,
    p_branch_code IN VARCHAR2,
    p_deposit     IN NUMBER,
    p_employee_id IN NUMBER
) AS
    v_customer_id NUMBER;
    v_account_num VARCHAR2(20);
BEGIN
    -- 1. Insert customer directly
    INSERT INTO CUSTOMER (customer_name, customer_address, phone, password)
    VALUES (p_name, p_address, p_phone, p_password)
    RETURNING customer_id INTO v_customer_id;
    
    v_account_num := 'ACC-OB-' || seq_account_id.NEXTVAL;
    
    -- 2. Nested procedure call
    pr_open_account(v_account_num, v_customer_id, p_branch_code, p_deposit, p_employee_id);
    
    DBMS_OUTPUT.PUT_LINE('Successfully onboarded: ' || p_name);
EXCEPTION
    WHEN OTHERS THEN 
        ROLLBACK; 
        DBMS_OUTPUT.PUT_LINE('Error during onboarding: ' || SQLERRM);
        RAISE;
END pr_customer_onboarding;
/


-- ════════════════════════════════════════════════════════════
-- SECTION 2: GUI PROCEDURES (called by Python models)
-- ════════════════════════════════════════════════════════════

-- ── EMPLOYEE ─────────────────────────────────────────────────

CREATE OR REPLACE PROCEDURE pr_add_employee (
    p_username    IN VARCHAR2,
    p_password    IN VARCHAR2,
    p_role        IN VARCHAR2,
    p_branch_code IN VARCHAR2
) AS
BEGIN
    INSERT INTO EMPLOYEE (username, password, role, ref_branch_code)
    VALUES (p_username, p_password, p_role, p_branch_code);
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN ROLLBACK; RAISE;
END pr_add_employee;
/

CREATE OR REPLACE PROCEDURE pr_update_employee (
    p_employee_id IN NUMBER,
    p_role        IN VARCHAR2,
    p_branch_code IN VARCHAR2
) AS
BEGIN
    UPDATE EMPLOYEE
    SET role = p_role, ref_branch_code = p_branch_code
    WHERE employee_id = p_employee_id;
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN ROLLBACK; RAISE;
END pr_update_employee;
/

CREATE OR REPLACE PROCEDURE pr_delete_employee (
    p_employee_id IN NUMBER
) AS
BEGIN
    DELETE FROM EMPLOYEE WHERE employee_id = p_employee_id;
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN ROLLBACK; RAISE;
END pr_delete_employee;
/

-- ── BRANCH ───────────────────────────────────────────────────

CREATE OR REPLACE PROCEDURE pr_add_branch (
    p_branch_code    IN VARCHAR2,
    p_branch_address IN VARCHAR2,
    p_phone          IN VARCHAR2
) AS
BEGIN
    INSERT INTO BRANCH (branch_code, branch_address, phone)
    VALUES (p_branch_code, p_branch_address, p_phone);
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN ROLLBACK; RAISE;
END pr_add_branch;
/

CREATE OR REPLACE PROCEDURE pr_delete_branch (
    p_branch_code IN VARCHAR2
) AS
BEGIN
    DELETE FROM BRANCH WHERE branch_code = p_branch_code;
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN ROLLBACK; RAISE;
END pr_delete_branch;
/

-- ── CUSTOMER ─────────────────────────────────────────────────

CREATE OR REPLACE PROCEDURE pr_add_customer (
    p_name        IN VARCHAR2,
    p_address     IN VARCHAR2,
    p_phone       IN VARCHAR2,
    p_password    IN VARCHAR2,
    p_employee_id IN NUMBER DEFAULT NULL
) AS
    v_cid NUMBER;
BEGIN
    INSERT INTO CUSTOMER (customer_name, customer_address, phone, password)
    VALUES (p_name, p_address, p_phone, p_password)
    RETURNING customer_id INTO v_cid;
    IF p_employee_id IS NOT NULL THEN
        INSERT INTO AUDIT_LOG (description, ref_employee_id)
        VALUES ('Created new customer: ' || p_name || ' (ID: ' || v_cid || ')', p_employee_id);
    END IF;
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN ROLLBACK; RAISE;
END pr_add_customer;
/

CREATE OR REPLACE PROCEDURE pr_update_customer (
    p_customer_id IN NUMBER,
    p_name        IN VARCHAR2,
    p_address     IN VARCHAR2,
    p_phone       IN VARCHAR2
) AS
BEGIN
    UPDATE CUSTOMER
    SET customer_name = p_name,
        customer_address = p_address,
        phone = p_phone
    WHERE customer_id = p_customer_id;
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN ROLLBACK; RAISE;
END pr_update_customer;
/

-- ── ACCOUNT ──────────────────────────────────────────────────

CREATE OR REPLACE PROCEDURE pr_open_account (
    p_account_number  IN VARCHAR2,
    p_customer_id     IN NUMBER,
    p_branch_code     IN VARCHAR2,
    p_initial_balance IN NUMBER,
    p_employee_id     IN NUMBER DEFAULT NULL
) AS
BEGIN
    INSERT INTO ACCOUNT (account_number, ref_customer_id,
                         ref_branch_code, date_of_creation, current_balance)
    VALUES (p_account_number, p_customer_id, p_branch_code, SYSDATE, p_initial_balance);
    IF p_employee_id IS NOT NULL THEN
        INSERT INTO AUDIT_LOG (description, ref_employee_id)
        VALUES ('Opened account ' || p_account_number || ' for customer ' || p_customer_id, p_employee_id);
    END IF;
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN ROLLBACK; RAISE;
END pr_open_account;
/

-- ── TRANSACTION ──────────────────────────────────────────────

-- Balance trigger fires automatically on INSERT into TRANSACTION

CREATE OR REPLACE PROCEDURE pr_deposit (
    p_account_id  IN NUMBER,
    p_branch_code IN VARCHAR2,
    p_amount      IN NUMBER,
    p_employee_id IN NUMBER DEFAULT NULL
) AS
    v_cust_id NUMBER;
BEGIN
    SELECT ref_customer_id INTO v_cust_id FROM ACCOUNT WHERE account_id = p_account_id;
    UPDATE ACCOUNT SET current_balance = current_balance + p_amount WHERE account_id = p_account_id;
    INSERT INTO TRANSACTION (ref_customer_id, ref_branch_code,
                             transaction_type, transaction_amount)
    VALUES (v_cust_id, p_branch_code, 'DEPOSIT', p_amount);
    IF p_employee_id IS NOT NULL THEN
        INSERT INTO AUDIT_LOG (description, ref_employee_id)
        VALUES ('Cash deposit of PKR ' || p_amount || ' for Account ' || p_account_id, p_employee_id);
    END IF;
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN ROLLBACK; RAISE;
END pr_deposit;
/

CREATE OR REPLACE PROCEDURE pr_withdraw (
    p_account_id  IN NUMBER,
    p_branch_code IN VARCHAR2,
    p_amount      IN NUMBER,
    p_employee_id IN NUMBER DEFAULT NULL
) AS
    v_cust_id NUMBER;
    v_balance NUMBER;
BEGIN
    SELECT ref_customer_id, current_balance INTO v_cust_id, v_balance FROM ACCOUNT WHERE account_id = p_account_id;
    IF v_balance < p_amount THEN
        RAISE_APPLICATION_ERROR(-20001, 'Insufficient balance for withdrawal.');
    END IF;
    UPDATE ACCOUNT SET current_balance = current_balance - p_amount WHERE account_id = p_account_id;
    INSERT INTO TRANSACTION (ref_customer_id, ref_branch_code,
                             transaction_type, transaction_amount)
    VALUES (v_cust_id, p_branch_code, 'WITHDRAWAL', p_amount);
    IF p_employee_id IS NOT NULL THEN
        INSERT INTO AUDIT_LOG (description, ref_employee_id)
        VALUES ('Cash withdrawal of PKR ' || p_amount || ' from Account ' || p_account_id, p_employee_id);
    END IF;
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN ROLLBACK; RAISE;
END pr_withdraw;
/

-- ── LOAN ─────────────────────────────────────────────────────

CREATE OR REPLACE PROCEDURE pr_reject_loan (
    p_loan_id     IN NUMBER,
    p_employee_id IN NUMBER
) AS
BEGIN
    UPDATE LOAN SET approval_status = 'REJECTED' WHERE loan_id = p_loan_id;

    INSERT INTO AUDIT_LOG (description, ref_employee_id)
    VALUES ('Loan ' || p_loan_id || ' rejected.', p_employee_id);

    COMMIT;
EXCEPTION
    WHEN OTHERS THEN ROLLBACK; RAISE;
END pr_reject_loan;
/

-- ── LOAN PAYMENT ─────────────────────────────────────────────

-- NOTE: TRANSACTION.ref_account_id column is added by 15_fix_transaction_account.sql
-- Run that script once before this procedure will compile cleanly.
CREATE OR REPLACE PROCEDURE pr_record_payment (
    p_loan_id         IN NUMBER,
    p_customer_id     IN NUMBER,
    p_account_id      IN NUMBER,
    p_amount          IN NUMBER,
    p_remaining       IN NUMBER
) AS
    v_branch VARCHAR2(10);
BEGIN
    -- Deduct from account
    UPDATE ACCOUNT
    SET current_balance = current_balance - p_amount
    WHERE account_id = p_account_id AND current_balance >= p_amount;

    IF SQL%ROWCOUNT = 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 'Insufficient funds for loan payment.');
    END IF;

    -- Get branch
    SELECT ref_branch_code INTO v_branch FROM ACCOUNT WHERE account_id = p_account_id;

    -- Insert Transaction (ref_account_id requires 15_fix_transaction_account.sql)
    INSERT INTO TRANSACTION (ref_customer_id, ref_branch_code, transaction_type, transaction_amount, ref_account_id)
    VALUES (p_customer_id, v_branch, 'LOAN PAYMENT', p_amount, p_account_id);

    -- Insert Loan Payment Record
    INSERT INTO LOAN_PAY (ref_loan_id, ref_customer_id, payment_date,
                          payment_amount, remaining_balance, payment_status)
    VALUES (p_loan_id, p_customer_id, SYSDATE, p_amount, p_remaining, 'COMPLETED');

    -- Auto-close the loan when fully paid off (remaining balance reaches zero)
    IF p_remaining <= 0 THEN
        UPDATE LOAN SET approval_status = 'PAID' WHERE loan_id = p_loan_id;
    END IF;

    COMMIT;
EXCEPTION
    WHEN OTHERS THEN ROLLBACK; RAISE;
END pr_record_payment;
/


-- ── CARD ─────────────────────────────────────────────────────

CREATE OR REPLACE PROCEDURE pr_issue_card (
    p_card_number   IN VARCHAR2,
    p_card_type     IN VARCHAR2,
    p_cvv           IN VARCHAR2,
    p_account_id    IN NUMBER,
    p_expiry_months IN NUMBER
) AS
BEGIN
    INSERT INTO CARD (card_number, card_type, date_of_issuance,
                      date_of_expiry, cvv_code, ref_account_id)
    VALUES (p_card_number, p_card_type, SYSDATE,
            ADD_MONTHS(SYSDATE, p_expiry_months), p_cvv, p_account_id);
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN ROLLBACK; RAISE;
END pr_issue_card;
/

CREATE OR REPLACE PROCEDURE pr_deactivate_card (
    p_card_id IN NUMBER
) AS
BEGIN
    UPDATE CARD SET card_status = 'INACTIVE' WHERE card_id = p_card_id;
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN ROLLBACK; RAISE;
END pr_deactivate_card;
/

-- ── BENEFICIARY ──────────────────────────────────────────────

CREATE OR REPLACE PROCEDURE pr_add_beneficiary (
    p_name        IN VARCHAR2,
    p_phone       IN VARCHAR2,
    p_iban        IN VARCHAR2,
    p_customer_id IN NUMBER
) AS
BEGIN
    INSERT INTO BENEFICIARY (beneficiary_name, phone, iban, ref_customer_id)
    VALUES (p_name, p_phone, p_iban, p_customer_id);
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN ROLLBACK; RAISE;
END pr_add_beneficiary;
/

CREATE OR REPLACE PROCEDURE pr_delete_beneficiary (
    p_beneficiary_id IN NUMBER
) AS
BEGIN
    DELETE FROM BENEFICIARY WHERE beneficiary_id = p_beneficiary_id;
    COMMIT;
EXCEPTION
    WHEN OTHERS THEN ROLLBACK; RAISE;
END pr_delete_beneficiary;
/
