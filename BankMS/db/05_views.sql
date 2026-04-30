-- ============================================================
-- 05_views.sql
-- ALL database views for the Bank Management System.
-- Run once in SQL*Plus / SQL Developer (@05_views.sql).
-- Python GUI models call: SELECT * FROM <view_name>
-- ============================================================


-- ════════════════════════════════════════════════════════════
-- SECTION 1: ORIGINAL VIEWS (schema-level)
-- ════════════════════════════════════════════════════════════

-- All accounts with customer and branch details
CREATE OR REPLACE VIEW vw_customer_accounts AS
SELECT
    c.customer_id,
    c.customer_name,
    c.phone AS customer_phone,
    a.account_id,
    a.account_number,
    a.current_balance,
    a.date_of_creation,
    b.branch_code,
    b.branch_address
FROM CUSTOMER c
JOIN ACCOUNT a ON c.customer_id = a.ref_customer_id
JOIN BRANCH  b ON a.ref_branch_code = b.branch_code;
/

-- Loans with their remaining balances
CREATE OR REPLACE VIEW vw_loan_details AS
SELECT
    l.loan_id,
    c.customer_id,
    c.customer_name,
    l.loan_amount,
    l.interest_rate,
    l.term_months,
    l.approval_status,
    l.application_date,
    NVL((SELECT MIN(remaining_balance)
         FROM LOAN_PAY lp
         WHERE lp.ref_loan_id = l.loan_id), l.loan_amount) AS current_remaining_balance
FROM LOAN l
JOIN CUSTOMER c ON l.ref_customer_id = c.customer_id;
/

-- Transaction history for account statements
CREATE OR REPLACE VIEW vw_transaction_history AS
SELECT
    t.transaction_id,
    t.transaction_date,
    c.customer_name,
    b.branch_code,
    t.transaction_type,
    t.transaction_amount,
    t.receiving_account
FROM TRANSACTION t
JOIN CUSTOMER c ON t.ref_customer_id = c.customer_id
JOIN BRANCH   b ON t.ref_branch_code  = b.branch_code
ORDER BY t.transaction_date DESC;
/

-- Branch aggregate statistics (for managers/admins)
CREATE OR REPLACE VIEW vw_branch_summary AS
SELECT
    b.branch_code,
    b.branch_address,
    (SELECT COUNT(*) FROM EMPLOYEE e WHERE e.ref_branch_code = b.branch_code) AS total_employees,
    (SELECT COUNT(*) FROM ACCOUNT a WHERE a.ref_branch_code = b.branch_code)  AS total_accounts,
    (SELECT NVL(SUM(a.current_balance), 0) FROM ACCOUNT a WHERE a.ref_branch_code = b.branch_code) AS total_deposits
FROM BRANCH b;
/


-- ════════════════════════════════════════════════════════════
-- SECTION 2: GUI VIEWS (used by Python models)
-- Each Python model does: SELECT * FROM <view_name>
-- No SQL is written inside any Python file.
-- ════════════════════════════════════════════════════════════

-- ── EMPLOYEE ─────────────────────────────────────────────────

-- Used by: employee_model.authenticate_user()
CREATE OR REPLACE VIEW vw_employee_login AS
SELECT
    employee_id,
    username,
    password,
    role,
    ref_branch_code AS branch_code
FROM EMPLOYEE;
/

-- Used by: employee_model.get_all_employees()
CREATE OR REPLACE VIEW vw_employee_details AS
SELECT
    e.employee_id,
    e.username,
    e.role,
    e.ref_branch_code AS branch_code,
    b.branch_address
FROM EMPLOYEE e
LEFT JOIN BRANCH b ON e.ref_branch_code = b.branch_code
ORDER BY e.employee_id ASC;
/

-- Used by: employee_model.get_total_counts()
--          account_model / loan_model KPI helpers
-- One row of system-wide KPI counts
CREATE OR REPLACE VIEW vw_system_kpi AS
SELECT
    (SELECT COUNT(*)                        FROM EMPLOYEE)                        AS employees,
    (SELECT COUNT(*)                        FROM BRANCH)                          AS branches,
    (SELECT COUNT(*)                        FROM CUSTOMER)                        AS customers,
    (SELECT COUNT(*)                        FROM ACCOUNT)                         AS accounts,
    (SELECT NVL(SUM(current_balance), 0)    FROM ACCOUNT)                         AS total_balance,
    (SELECT COUNT(*) FROM LOAN WHERE approval_status = 'PENDING')                 AS pending_loans,
    (SELECT COUNT(*) FROM TRANSACTION
     WHERE TRUNC(transaction_date) = TRUNC(SYSDATE))                             AS today_transactions
FROM DUAL;
/


-- ── ACCOUNT ──────────────────────────────────────────────────

-- Used by: account_model.get_all_accounts()
--          account_model.get_accounts_by_customer()
CREATE OR REPLACE VIEW vw_account_details AS
SELECT
    a.account_id,
    a.account_number,
    a.current_balance,
    TO_CHAR(a.current_balance,  'FM999,999,999.99') AS balance_fmt,
    TO_CHAR(a.date_of_creation, 'Mon DD, YYYY')       AS created_on,
    a.ref_branch_code AS branch_code,
    c.customer_id,
    c.customer_name,
    c.phone
FROM ACCOUNT a
JOIN CUSTOMER c ON a.ref_customer_id = c.customer_id
ORDER BY a.account_id ASC;
/

-- Used by: account_model.get_count_per_branch()
-- Powers the donut chart on the Admin dashboard
CREATE OR REPLACE VIEW vw_branch_account_counts AS
SELECT
    b.branch_code,
    b.branch_address,
    COUNT(a.account_id)            AS account_count,
    NVL(SUM(a.current_balance), 0) AS total_balance
FROM BRANCH b
LEFT JOIN ACCOUNT a ON a.ref_branch_code = b.branch_code
GROUP BY b.branch_code, b.branch_address
ORDER BY b.branch_code ASC;
/

-- ── BRANCH ───────────────────────────────────────────────────

-- Used by: branch_model.get_all_branches()
CREATE OR REPLACE VIEW vw_branch_details AS
SELECT
    branch_code,
    branch_address,
    phone,
    TO_CHAR(created_at, 'Mon DD, YYYY') AS created_on
FROM BRANCH
ORDER BY branch_code ASC;
/

-- ── CUSTOMER ─────────────────────────────────────────────────

-- Used by: customer_model.get_all_customers()
CREATE OR REPLACE VIEW vw_customer_details AS
SELECT
    customer_id,
    customer_name,
    customer_address,
    phone,
    TO_CHAR(created_at, 'Mon DD, YYYY') AS created_on
FROM CUSTOMER
ORDER BY customer_id ASC;
/

-- ── TRANSACTION ──────────────────────────────────────────────

-- Used by: transaction_model.get_all_transactions()
--          transaction_model.get_transactions_by_customer()
CREATE OR REPLACE VIEW vw_transaction_full AS
SELECT
    t.transaction_id,
    t.transaction_type,
    t.transaction_amount,
    TO_CHAR(t.transaction_amount, 'FM999,999,999.99') AS amount_fmt,
    TO_CHAR(t.transaction_date,   'DD-MM-YYYY HH24:MI') AS txn_date,
    t.ref_customer_id AS customer_id,
    c.customer_name,
    t.ref_branch_code AS branch_code,
    t.receiving_account
FROM TRANSACTION t
JOIN CUSTOMER c ON t.ref_customer_id = c.customer_id
ORDER BY t.transaction_id ASC;
/

-- Used by: transaction_model.get_monthly_counts()
-- Powers the bar chart — deposit vs withdrawal count per month (last 9 months)
CREATE OR REPLACE VIEW vw_monthly_txn_counts AS
SELECT
    TO_CHAR(transaction_date, 'Mon-YY')                                   AS month_label,
    MIN(TRUNC(transaction_date, 'MM'))                                    AS sort_date,
    SUM(CASE WHEN transaction_type = 'DEPOSIT'    THEN 1 ELSE 0 END)     AS deposit_count,
    SUM(CASE WHEN transaction_type = 'WITHDRAWAL' THEN 1 ELSE 0 END)     AS withdrawal_count,
    SUM(CASE WHEN transaction_type = 'TRANSFER'   THEN 1 ELSE 0 END)     AS transfer_count
FROM TRANSACTION
WHERE transaction_date >= ADD_MONTHS(SYSDATE, -9)
GROUP BY TO_CHAR(transaction_date, 'Mon-YY')
ORDER BY MIN(TRUNC(transaction_date, 'MM')) ASC;
/

-- Used by: transaction_model.get_daily_totals()
-- Powers the area chart — daily PKR totals for last 30 days
CREATE OR REPLACE VIEW vw_daily_txn_totals AS
SELECT
    TO_CHAR(transaction_date, 'DD-MM')                                              AS txn_day,
    TRUNC(transaction_date)                                                         AS txn_date,
    NVL(SUM(CASE WHEN transaction_type IN ('DEPOSIT','TRANSFER')
                 THEN transaction_amount ELSE 0 END), 0)                            AS deposits,
    NVL(SUM(CASE WHEN transaction_type = 'WITHDRAWAL'
                 THEN transaction_amount ELSE 0 END), 0)                            AS withdrawals
FROM TRANSACTION
WHERE transaction_date >= SYSDATE - 30
GROUP BY TO_CHAR(transaction_date, 'DD-MM'), TRUNC(transaction_date)
ORDER BY TRUNC(transaction_date) ASC;
/

-- ── LOAN ─────────────────────────────────────────────────────

-- Used by: loan_model.get_all_loans()
--          loan_model.get_loans_by_customer()
CREATE OR REPLACE VIEW vw_loan_full AS
SELECT
    l.loan_id,
    l.loan_amount,
    TO_CHAR(l.loan_amount, 'FM999,999,999.99') AS loan_amount_fmt,
    l.interest_rate,
    l.term_months,
    TO_CHAR(l.application_date, 'Mon DD, YYYY')  AS app_date,
    l.approval_status,
    c.customer_id,
    c.customer_name,
    a.ref_branch_code AS branch_code,
    NVL(
        (SELECT lp.remaining_balance
         FROM LOAN_PAY lp
         WHERE lp.ref_loan_id = l.loan_id
           AND lp.payment_id = (SELECT MAX(p2.payment_id)
                                FROM LOAN_PAY p2
                                WHERE p2.ref_loan_id = l.loan_id)),
        l.loan_amount
    ) AS current_remaining_balance
FROM LOAN l
JOIN CUSTOMER c ON l.ref_customer_id = c.customer_id
LEFT JOIN ACCOUNT a ON l.ref_account_id = a.account_id
ORDER BY l.loan_id ASC;
/


-- Used by: loan_model.get_pending_loans()
CREATE OR REPLACE VIEW vw_pending_loans AS
SELECT
    l.loan_id,
    l.loan_amount,
    TO_CHAR(l.loan_amount, 'FM999,999,999.99') AS loan_amount_fmt,
    l.interest_rate,
    l.term_months,
    TO_CHAR(l.application_date, 'Mon DD, YYYY')  AS app_date,
    l.approval_status,
    c.customer_id,
    c.customer_name,
    a.ref_branch_code AS branch_code
FROM LOAN l
JOIN CUSTOMER c ON l.ref_customer_id = c.customer_id
LEFT JOIN ACCOUNT a ON l.ref_account_id = a.account_id
WHERE l.approval_status = 'PENDING'
ORDER BY l.application_date ASC;
/

-- ── LOAN PAYMENTS ────────────────────────────────────────────

-- Used by: loan_payment_model.get_payments_by_loan()
--          loan_payment_model.get_payments_by_customer()
CREATE OR REPLACE VIEW vw_loan_payments AS
SELECT
    lp.payment_id,
    lp.ref_loan_id,
    lp.ref_customer_id,
    lp.payment_amount,
    TO_CHAR(lp.payment_amount,    'FM999,999,999.99') AS payment_amount_fmt,
    lp.remaining_balance,
    TO_CHAR(lp.remaining_balance, 'FM999,999,999.99') AS remaining_fmt,
    TO_CHAR(lp.payment_date, 'Mon DD, YYYY')            AS pay_date,
    lp.payment_status,
    NVL(lp.late_fee, 0)                               AS late_fee
FROM LOAN_PAY lp
ORDER BY lp.payment_date ASC;
/

-- ── CARD ─────────────────────────────────────────────────────

-- Used by: card_model.get_all_cards()
--          card_model.get_cards_by_account()
CREATE OR REPLACE VIEW vw_card_details AS
SELECT
    cd.card_id,
    cd.card_number,
    cd.card_type,
    TO_CHAR(cd.date_of_issuance, 'Mon DD, YYYY') AS issued_on,
    TO_CHAR(cd.date_of_expiry,   'Mon DD, YYYY') AS expires_on,
    cd.card_status,
    a.account_id,
    a.account_number,
    c.customer_id,
    c.customer_name
FROM CARD cd
JOIN ACCOUNT  a ON cd.ref_account_id = a.account_id
JOIN CUSTOMER c ON a.ref_customer_id = c.customer_id
ORDER BY cd.card_id ASC;
/

-- ── BENEFICIARY ──────────────────────────────────────────────

-- Used by: beneficiary_model.get_all_beneficiaries()
--          beneficiary_model.get_beneficiaries_by_customer()
CREATE OR REPLACE VIEW vw_beneficiary_details AS
SELECT
    b.beneficiary_id,
    b.beneficiary_name,
    b.phone,
    b.iban,
    b.ref_customer_id AS customer_id,
    c.customer_name
FROM BENEFICIARY b
JOIN CUSTOMER c ON b.ref_customer_id = c.customer_id
ORDER BY b.beneficiary_id ASC;
/

-- ── AUDIT LOGS ───────────────────────────────────────────────

-- Used by: audit_model.get_all_logs()
CREATE OR REPLACE VIEW vw_audit_log_details AS
SELECT
    a.log_id,
    a.description,
    TO_CHAR(a.timestamp, 'Mon DD, YYYY HH24:MI:SS') AS log_timestamp,
    e.employee_id,
    e.username AS employee_name,
    e.role,
    e.ref_branch_code AS branch_code
FROM AUDIT_LOG a
JOIN EMPLOYEE e ON a.ref_employee_id = e.employee_id
ORDER BY a.log_id DESC;
/

-- Used by: employee_model.get_total_counts() and account_model.get_total_balance()
CREATE OR REPLACE VIEW vw_system_kpi AS
SELECT
    (SELECT COUNT(*) FROM EMPLOYEE) AS employees,
    (SELECT COUNT(*) FROM BRANCH) AS branches,
    (SELECT COUNT(*) FROM CUSTOMER) AS customers,
    (SELECT COUNT(*) FROM ACCOUNT) AS accounts,
    (SELECT NVL(SUM(current_balance), 0) FROM ACCOUNT) AS total_balance,
    (SELECT COUNT(*) FROM LOAN WHERE approval_status = 'PENDING') AS pending_loans,
    (SELECT COUNT(*) FROM TRANSACTION WHERE TRUNC(transaction_date) = TRUNC(SYSDATE)) AS today_transactions
FROM DUAL;
/
