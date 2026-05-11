-- ============================================================
-- Project : Bank Account Management System
-- Script  : 03_triggers.sql
-- Purpose : All triggers - Auto ID, Business Logic, Audit Logs
-- ============================================================
SET SERVEROUTPUT ON;

CREATE OR REPLACE TRIGGER trg_before_employee_ins
BEFORE INSERT ON EMPLOYEE
FOR EACH ROW
BEGIN
    :NEW.employee_id := seq_employee_id.NEXTVAL;
END;
/

CREATE OR REPLACE TRIGGER trg_before_customer_ins
BEFORE INSERT ON CUSTOMER
FOR EACH ROW
BEGIN
    :NEW.customer_id := seq_customer_id.NEXTVAL;
END;
/

CREATE OR REPLACE TRIGGER trg_before_account_ins
BEFORE INSERT ON ACCOUNT
FOR EACH ROW
BEGIN
    :NEW.account_id := seq_account_id.NEXTVAL;
END;
/

CREATE OR REPLACE TRIGGER trg_before_card_ins
BEFORE INSERT ON CARD
FOR EACH ROW
BEGIN
    :NEW.card_id := seq_card_id.NEXTVAL;
END;
/

CREATE OR REPLACE TRIGGER trg_before_beneficiary_ins
BEFORE INSERT ON BENEFICIARY
FOR EACH ROW
BEGIN
    :NEW.beneficiary_id := seq_beneficiary_id.NEXTVAL;
END;
/

CREATE OR REPLACE TRIGGER trg_before_transaction_ins
BEFORE INSERT ON TRANSACTION
FOR EACH ROW
BEGIN
    :NEW.transaction_id := seq_transaction_id.NEXTVAL;
END;
/

CREATE OR REPLACE TRIGGER trg_before_loan_ins
BEFORE INSERT ON LOAN
FOR EACH ROW
BEGIN
    :NEW.loan_id := seq_loan_id.NEXTVAL;
END;
/

CREATE OR REPLACE TRIGGER trg_before_loan_pay_ins
BEFORE INSERT ON LOAN_PAY
FOR EACH ROW
BEGIN
    :NEW.payment_id := seq_loan_pay_id.NEXTVAL;
END;
/

CREATE OR REPLACE TRIGGER trg_before_audit_log_ins
BEFORE INSERT ON AUDIT_LOG
FOR EACH ROW
BEGIN
    :NEW.log_id := seq_audit_log_id.NEXTVAL;
END;
/


-- ============================================================
-- SECTION 2: BUSINESS LOGIC TRIGGERS
-- ============================================================

-- Trigger: Update account balance on every transaction
-- When a DEPOSIT/WITHDRAWAL/TRANSFER is inserted,
-- automatically update the current_balance in ACCOUNT

CREATE OR REPLACE TRIGGER trg_before_transaction_balance
BEFORE INSERT ON TRANSACTION
FOR EACH ROW
BEGIN
    NULL; -- Balance logic moved to procedures to support specific account targeting
END;
/


-- Trigger: Set card expiry date automatically (3 years from issuance)
-- If user does not provide expiry, auto-set it

CREATE OR REPLACE TRIGGER trg_before_card_expiry
BEFORE INSERT ON CARD
FOR EACH ROW
BEGIN
    IF :NEW.date_of_expiry IS NULL THEN
        :NEW.date_of_expiry := ADD_MONTHS(:NEW.date_of_issuance, 36);
    END IF;
END;
/


-- Trigger: Set loan application_date to SYSDATE if not provided

CREATE OR REPLACE TRIGGER trg_before_loan_appdate
BEFORE INSERT ON LOAN
FOR EACH ROW
BEGIN
    IF :NEW.application_date IS NULL THEN
        :NEW.application_date := SYSDATE;
    END IF;
END;
/


-- Trigger: Prevent negative remaining_balance in LOAN_PAY

CREATE OR REPLACE TRIGGER trg_before_loan_pay_balance
BEFORE INSERT ON LOAN_PAY
FOR EACH ROW
BEGIN
    IF :NEW.remaining_balance < 0 THEN
        RAISE_APPLICATION_ERROR(-20003, 'Remaining balance cannot be negative.');
    END IF;
END;
/


-- ============================================================
-- SECTION 3: AFTER UPDATE TRIGGERS (Audit Logging)
-- ============================================================

-- Trigger: Log when loan approval_status changes (PENDING → APPROVED/REJECTED)

CREATE OR REPLACE TRIGGER trg_after_loan_status_upd
AFTER UPDATE OF approval_status ON LOAN
FOR EACH ROW
DECLARE
    v_emp_id NUMBER(10);
BEGIN
    -- Use employee_id 1 as system/default if no session user
    -- In real GUI this would come from application session
    SELECT NVL(MIN(employee_id), 1) INTO v_emp_id FROM EMPLOYEE;

    INSERT INTO AUDIT_LOG (description, timestamp, ref_employee_id)
    VALUES (
        'LOAN ID ' || :NEW.loan_id ||
        ' status changed from ' || :OLD.approval_status ||
        ' to ' || :NEW.approval_status,
        SYSDATE,
        v_emp_id
    );
END;
/


-- Trigger: Log when account balance is updated

CREATE OR REPLACE TRIGGER trg_after_account_balance_upd
AFTER UPDATE OF current_balance ON ACCOUNT
FOR EACH ROW
DECLARE
    v_emp_id NUMBER(10);
BEGIN
    SELECT NVL(MIN(employee_id), 1) INTO v_emp_id FROM EMPLOYEE;

    INSERT INTO AUDIT_LOG (description, timestamp, ref_employee_id)
    VALUES (
        'ACCOUNT ID ' || :NEW.account_id ||
        ' balance changed from ' || :OLD.current_balance ||
        ' to ' || :NEW.current_balance,
        SYSDATE,
        v_emp_id
    );
END;
/


-- Trigger: Log when card status changes (ACTIVE → BLOCKED/EXPIRED)

CREATE OR REPLACE TRIGGER trg_after_card_status_upd
AFTER UPDATE OF card_status ON CARD
FOR EACH ROW
DECLARE
    v_emp_id NUMBER(10);
BEGIN
    SELECT NVL(MIN(employee_id), 1) INTO v_emp_id FROM EMPLOYEE;

    INSERT INTO AUDIT_LOG (description, timestamp, ref_employee_id)
    VALUES (
        'CARD ID ' || :NEW.card_id ||
        ' status changed from ' || :OLD.card_status ||
        ' to ' || :NEW.card_status,
        SYSDATE,
        v_emp_id
    );
END;
/


-- ============================================================
-- SECTION 4: AFTER DELETE TRIGGERS (Audit Logging)
-- ============================================================

-- Trigger: Log when a customer is deleted

CREATE OR REPLACE TRIGGER trg_after_customer_del
AFTER DELETE ON CUSTOMER
FOR EACH ROW
DECLARE
    v_emp_id NUMBER(10);
BEGIN
    SELECT NVL(MIN(employee_id), 1) INTO v_emp_id FROM EMPLOYEE;

    INSERT INTO AUDIT_LOG (description, timestamp, ref_employee_id)
    VALUES (
        'CUSTOMER ID ' || :OLD.customer_id ||
        ' (' || :OLD.customer_name || ') was deleted from system.',
        SYSDATE,
        v_emp_id
    );
END;
/


-- Trigger: Log when a beneficiary is deleted

CREATE OR REPLACE TRIGGER trg_after_beneficiary_del
AFTER DELETE ON BENEFICIARY
FOR EACH ROW
DECLARE
    v_emp_id NUMBER(10);
BEGIN
    SELECT NVL(MIN(employee_id), 1) INTO v_emp_id FROM EMPLOYEE;

    INSERT INTO AUDIT_LOG (description, timestamp, ref_employee_id)
    VALUES (
        'BENEFICIARY ID ' || :OLD.beneficiary_id ||
        ' (' || :OLD.beneficiary_name || ') removed by customer ID ' || :OLD.ref_customer_id,
        SYSDATE,
        v_emp_id
    );
END;
/


-- ============================================================
-- SECTION 5: AFTER INSERT TRIGGERS (Audit Logging)
-- ============================================================

-- Trigger: Log when a new account is created

CREATE OR REPLACE TRIGGER trg_after_account_ins
AFTER INSERT ON ACCOUNT
FOR EACH ROW
DECLARE
    v_emp_id NUMBER(10);
BEGIN
    SELECT NVL(MIN(employee_id), 1) INTO v_emp_id FROM EMPLOYEE;

    INSERT INTO AUDIT_LOG (description, timestamp, ref_employee_id)
    VALUES (
        'New ACCOUNT created. Account Number: ' || :NEW.account_number ||
        ' for Customer ID: ' || :NEW.ref_customer_id,
        SYSDATE,
        v_emp_id
    );
END;
/


-- Trigger: Log when a new loan is applied

CREATE OR REPLACE TRIGGER trg_after_loan_ins
AFTER INSERT ON LOAN
FOR EACH ROW
DECLARE
    v_emp_id NUMBER(10);
BEGIN
    SELECT NVL(MIN(employee_id), 1) INTO v_emp_id FROM EMPLOYEE;

    INSERT INTO AUDIT_LOG (description, timestamp, ref_employee_id)
    VALUES (
        'New LOAN applied. Loan ID: ' || :NEW.loan_id ||
        ' Amount: ' || :NEW.loan_amount ||
        ' by Customer ID: ' || :NEW.ref_customer_id,
        SYSDATE,
        v_emp_id
    );
END;
/

-- ============================================================
-- END OF 03_triggers.sql
-- ============================================================