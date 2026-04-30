-- 06_indexes.sql

-- Foreign Key Indexes (Crucial for performance and avoiding full table locks on deletes)
CREATE INDEX idx_employee_branch ON EMPLOYEE(ref_branch_code);
CREATE INDEX idx_account_customer ON ACCOUNT(ref_customer_id);
CREATE INDEX idx_account_branch ON ACCOUNT(ref_branch_code);
CREATE INDEX idx_card_account ON CARD(ref_account_id);
CREATE INDEX idx_benef_account ON BENEFICIARY(ref_account_id);
CREATE INDEX idx_benef_customer ON BENEFICIARY(ref_customer_id);
CREATE INDEX idx_trans_customer ON TRANSACTION(ref_customer_id);
CREATE INDEX idx_trans_branch ON TRANSACTION(ref_branch_code);
CREATE INDEX idx_loan_account ON LOAN(ref_account_id);
CREATE INDEX idx_loan_customer ON LOAN(ref_customer_id);
CREATE INDEX idx_loanpay_loan ON LOAN_PAY(ref_loan_id);
CREATE INDEX idx_loanpay_customer ON LOAN_PAY(ref_customer_id);

-- Search/Filter Indexes
CREATE INDEX idx_customer_name ON CUSTOMER(customer_name);
CREATE INDEX idx_trans_date ON TRANSACTION(transaction_date);
CREATE INDEX idx_account_number ON ACCOUNT(account_number);
CREATE INDEX idx_employee_username ON EMPLOYEE(username);
