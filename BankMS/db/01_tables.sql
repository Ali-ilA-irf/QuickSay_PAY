
CREATE TABLE BRANCH (
    branch_code     VARCHAR2(10)    CONSTRAINT pk_branch PRIMARY KEY
                                    CONSTRAINT ck_branch_code CHECK (branch_code LIKE 'QSB%' AND LENGTH(branch_code) = 10),
    branch_address  VARCHAR2(255)   CONSTRAINT nn_branch_address NOT NULL,
    phone           VARCHAR2(15)    CONSTRAINT uq_branch_phone UNIQUE,
    created_at      DATE            DEFAULT SYSDATE
);


CREATE TABLE EMPLOYEE (
    employee_id     NUMBER(10)      CONSTRAINT pk_employee PRIMARY KEY,
    username        VARCHAR2(50)    CONSTRAINT nn_employee_username NOT NULL,
    password        VARCHAR2(255)   CONSTRAINT nn_employee_password NOT NULL,
    role            VARCHAR2(30)    CONSTRAINT nn_employee_role NOT NULL,
    ref_branch_code VARCHAR2(10)    CONSTRAINT nn_employee_branch NOT NULL,
    created_at      DATE            DEFAULT SYSDATE,
    CONSTRAINT uq_employee_username UNIQUE (username),
    CONSTRAINT fk_employee_ref_branch FOREIGN KEY (ref_branch_code) REFERENCES BRANCH(branch_code)
);


CREATE TABLE CUSTOMER (
    customer_id     NUMBER(10)      CONSTRAINT pk_customer PRIMARY KEY,
    customer_name   VARCHAR2(100)   CONSTRAINT nn_customer_name NOT NULL,
    customer_address VARCHAR2(255),
    phone           VARCHAR2(15)    CONSTRAINT uq_customer_phone UNIQUE,
    created_at      DATE            DEFAULT SYSDATE
);


CREATE TABLE ACCOUNT (
    account_id      NUMBER(10)      CONSTRAINT pk_account PRIMARY KEY,
    account_number  VARCHAR2(20)    CONSTRAINT nn_account_number NOT NULL,
    ref_customer_id NUMBER(10)      CONSTRAINT nn_account_customer NOT NULL,
    ref_branch_code VARCHAR2(10)    CONSTRAINT nn_account_branch NOT NULL,
    date_of_creation DATE           CONSTRAINT nn_account_creation NOT NULL,
    current_balance NUMBER(15,2)    DEFAULT 0,
    created_at      DATE            DEFAULT SYSDATE,
    CONSTRAINT uq_account_number UNIQUE (account_number),
    CONSTRAINT ck_account_balance CHECK (current_balance >= 0),
    CONSTRAINT fk_account_ref_customer FOREIGN KEY (ref_customer_id) REFERENCES CUSTOMER(customer_id),
    CONSTRAINT fk_account_ref_branch FOREIGN KEY (ref_branch_code) REFERENCES BRANCH(branch_code)
);


CREATE TABLE CARD (
    card_id         NUMBER(10)      CONSTRAINT pk_card PRIMARY KEY,
    card_number     VARCHAR2(20)    CONSTRAINT nn_card_number NOT NULL,
    card_type       VARCHAR2(20)    CONSTRAINT nn_card_type NOT NULL,
    date_of_issuance DATE           CONSTRAINT nn_card_issue NOT NULL,
    date_of_expiry  DATE            CONSTRAINT nn_card_expiry NOT NULL,
    cvv_code        VARCHAR2(5)     CONSTRAINT nn_card_cvv NOT NULL,
    card_status     VARCHAR2(20)    DEFAULT 'ACTIVE',
    ref_account_id  NUMBER(10)      CONSTRAINT nn_card_account NOT NULL,
    created_at      DATE            DEFAULT SYSDATE,
    CONSTRAINT uq_card_number UNIQUE (card_number),
    CONSTRAINT fk_card_ref_account FOREIGN KEY (ref_account_id) REFERENCES ACCOUNT(account_id)
);


CREATE TABLE BENEFICIARY (
    beneficiary_id  NUMBER(10)      CONSTRAINT pk_beneficiary PRIMARY KEY,
    beneficiary_name VARCHAR2(100)  CONSTRAINT nn_beneficiary_name NOT NULL,
    phone           VARCHAR2(15),
    iban            VARCHAR2(50)    CONSTRAINT nn_beneficiary_iban NOT NULL,
    ref_customer_id NUMBER(10)      CONSTRAINT nn_beneficiary_customer NOT NULL,
    created_at      DATE            DEFAULT SYSDATE,
    CONSTRAINT uq_beneficiary_iban UNIQUE (iban),
    CONSTRAINT fk_beneficiary_ref_customer FOREIGN KEY (ref_customer_id) REFERENCES CUSTOMER(customer_id)
);

CREATE TABLE TRANSACTION (
    transaction_id  NUMBER(10)      CONSTRAINT pk_transaction PRIMARY KEY,
    ref_customer_id NUMBER(10)      CONSTRAINT nn_transaction_customer NOT NULL,
    ref_branch_code VARCHAR2(10)    CONSTRAINT nn_transaction_branch NOT NULL,
    transaction_type VARCHAR2(30)   CONSTRAINT nn_transaction_type NOT NULL,
    transaction_amount NUMBER(15,2) CONSTRAINT nn_transaction_amount NOT NULL,
    transaction_date DATE           DEFAULT SYSDATE,
    receiving_account VARCHAR2(20),
    ref_account_id  NUMBER(10),                                -- nullable: set for LOAN PAYMENT, NULL for others
    created_at      DATE            DEFAULT SYSDATE,
    CONSTRAINT ck_transaction_amount CHECK (transaction_amount > 0),
    CONSTRAINT fk_transaction_ref_customer FOREIGN KEY (ref_customer_id) REFERENCES CUSTOMER(customer_id),
    CONSTRAINT fk_transaction_ref_branch FOREIGN KEY (ref_branch_code) REFERENCES BRANCH(branch_code),
    CONSTRAINT fk_transaction_ref_account FOREIGN KEY (ref_account_id) REFERENCES ACCOUNT(account_id)
);



CREATE TABLE LOAN (
    loan_id         NUMBER(10)      CONSTRAINT pk_loan PRIMARY KEY,
    loan_amount     NUMBER(15,2)    CONSTRAINT nn_loan_amount NOT NULL,
    interest_rate   NUMBER(5,2)     CONSTRAINT nn_loan_rate NOT NULL,
    term_months     NUMBER(10)      CONSTRAINT nn_loan_term NOT NULL,
    application_date DATE           CONSTRAINT nn_loan_appdate NOT NULL,
    approval_status VARCHAR2(20)    DEFAULT 'PENDING',
    ref_account_id  NUMBER(10)      CONSTRAINT nn_loan_account NOT NULL,
    ref_customer_id NUMBER(10)      CONSTRAINT nn_loan_customer NOT NULL,
    created_at      DATE            DEFAULT SYSDATE,
    CONSTRAINT ck_loan_amount CHECK (loan_amount > 0),
    CONSTRAINT ck_loan_interest_rate CHECK (interest_rate > 0),
    CONSTRAINT fk_loan_ref_account FOREIGN KEY (ref_account_id) REFERENCES ACCOUNT(account_id),
    CONSTRAINT fk_loan_ref_customer FOREIGN KEY (ref_customer_id) REFERENCES CUSTOMER(customer_id)
);

CREATE TABLE LOAN_PAY (
    payment_id      NUMBER(10)      CONSTRAINT pk_loan_pay PRIMARY KEY,
    ref_loan_id     NUMBER(10)      CONSTRAINT nn_loan_pay_loan NOT NULL,
    ref_customer_id NUMBER(10)      CONSTRAINT nn_loan_pay_customer NOT NULL,
    payment_date    DATE            CONSTRAINT nn_loan_pay_date NOT NULL,
    payment_amount  NUMBER(15,2)    CONSTRAINT nn_loan_pay_amount NOT NULL,
    remaining_balance NUMBER(15,2) CONSTRAINT nn_loan_pay_balance NOT NULL,
    payment_status  VARCHAR2(20)    DEFAULT 'PENDING',
    account_cutoff_date DATE,
    late_fee        NUMBER(15,2)    DEFAULT 0,
    created_at      DATE            DEFAULT SYSDATE,
    CONSTRAINT ck_loan_pay_amount CHECK (payment_amount > 0),
    CONSTRAINT ck_loan_pay_late_fee CHECK (late_fee >= 0),
    CONSTRAINT fk_loan_pay_ref_loan FOREIGN KEY (ref_loan_id) REFERENCES LOAN(loan_id),
    CONSTRAINT fk_loan_pay_ref_customer FOREIGN KEY (ref_customer_id) REFERENCES CUSTOMER(customer_id)
);


CREATE TABLE AUDIT_LOG (
    log_id          NUMBER(10)      CONSTRAINT pk_audit_log PRIMARY KEY,
    description     VARCHAR2(500)   CONSTRAINT nn_audit_desc NOT NULL,
    timestamp       DATE            DEFAULT SYSDATE,
    ref_employee_id NUMBER(10)      CONSTRAINT nn_audit_employee NOT NULL,
    created_at      DATE            DEFAULT SYSDATE,
    CONSTRAINT fk_audit_log_ref_employee FOREIGN KEY (ref_employee_id) REFERENCES EMPLOYEE(employee_id)
);

-- ============================================
-- TABLE RELATIONSHIPS & CONSTRAINTS SUMMARY
-- ============================================
-- BRANCH (1) ──→ (N) EMPLOYEE
-- BRANCH (1) ──→ (N) ACCOUNT
-- CUSTOMER (1) ──→ (N) ACCOUNT
-- ACCOUNT (1) ──→ (N) CARD
-- ACCOUNT (1) ──→ (N) BENEFICIARY
-- CUSTOMER (1) ──→ (N) BENEFICIARY
-- CUSTOMER (1) ──→ (N) TRANSACTION
-- BRANCH (1) ──→ (N) TRANSACTION
-- ACCOUNT (1) ──→ (N) LOAN
-- CUSTOMER (1) ──→ (N) LOAN
-- LOAN (1) ──→ (N) LOAN_PAYMENT
-- CUSTOMER (1) ──→ (N) LOAN_PAYMENT
-- EMPLOYEE (1) ──→ (N) AUDIT_LOG
-- ============================================