-- 04_inserts.sql
SET DEFINE OFF;

-- Branches
INSERT INTO BRANCH (branch_code, branch_address, phone) VALUES ('QSB0000001', '123 Main St, City Center', '555-0101');
INSERT INTO BRANCH (branch_code, branch_address, phone) VALUES ('QSB0000002', '456 West End Ave, Uptown', '555-0102');
INSERT INTO BRANCH (branch_code, branch_address, phone) VALUES ('QSB0000003', '789 East Side Dr, Downtown', '555-0103');
INSERT INTO BRANCH (branch_code, branch_address, phone) VALUES ('QSB0000004', '321 North Blvd, North Hills', '555-0104');
INSERT INTO BRANCH (branch_code, branch_address, phone) VALUES ('QSB0000005', '654 South Pkwy, South Side', '555-0105');

-- Employees
INSERT INTO EMPLOYEE (username, password, role, ref_branch_code) VALUES ('admin_user', 'admin123', 'ADMIN', 'QSB0000001');
INSERT INTO EMPLOYEE (username, password, role, ref_branch_code) VALUES ('mgr_john', 'mgr123', 'MANAGER', 'QSB0000001');
INSERT INTO EMPLOYEE (username, password, role, ref_branch_code) VALUES ('mgr_sarah', 'mgr123', 'MANAGER', 'QSB0000002');
INSERT INTO EMPLOYEE (username, password, role, ref_branch_code) VALUES ('mgr_mike', 'mgr123', 'MANAGER', 'QSB0000003');
INSERT INTO EMPLOYEE (username, password, role, ref_branch_code) VALUES ('mgr_lucy', 'mgr123', 'MANAGER', 'QSB0000004');
INSERT INTO EMPLOYEE (username, password, role, ref_branch_code) VALUES ('mgr_david', 'mgr123', 'MANAGER', 'QSB0000005');
INSERT INTO EMPLOYEE (username, password, role, ref_branch_code) VALUES ('teller_alice', 'teller123', 'TELLER', 'QSB0000001');
INSERT INTO EMPLOYEE (username, password, role, ref_branch_code) VALUES ('teller_bob', 'teller123', 'TELLER', 'QSB0000001');
INSERT INTO EMPLOYEE (username, password, role, ref_branch_code) VALUES ('teller_charlie', 'teller123', 'TELLER', 'QSB0000002');
INSERT INTO EMPLOYEE (username, password, role, ref_branch_code) VALUES ('teller_diana', 'teller123', 'TELLER', 'QSB0000003');
INSERT INTO EMPLOYEE (username, password, role, ref_branch_code) VALUES ('teller_eve', 'teller123', 'TELLER', 'QSB0000004');
INSERT INTO EMPLOYEE (username, password, role, ref_branch_code) VALUES ('teller_frank', 'teller123', 'TELLER', 'QSB0000005');

-- Customers
INSERT INTO CUSTOMER (customer_name, customer_address, phone) VALUES ('John Doe', '12 Maple St', '555-1001');
INSERT INTO CUSTOMER (customer_name, customer_address, phone) VALUES ('Jane Smith', '34 Oak Ave', '555-1002');
INSERT INTO CUSTOMER (customer_name, customer_address, phone) VALUES ('Michael Johnson', '56 Pine Rd', '555-1003');
INSERT INTO CUSTOMER (customer_name, customer_address, phone) VALUES ('Emily Davis', '78 Cedar Ln', '555-1004');
INSERT INTO CUSTOMER (customer_name, customer_address, phone) VALUES ('William Brown', '90 Birch Dr', '555-1005');
INSERT INTO CUSTOMER (customer_name, customer_address, phone) VALUES ('Olivia Wilson', '11 Elm Ct', '555-1006');
INSERT INTO CUSTOMER (customer_name, customer_address, phone) VALUES ('James Taylor', '22 Willow Way', '555-1007');
INSERT INTO CUSTOMER (customer_name, customer_address, phone) VALUES ('Sophia Martinez', '33 Spruce Pl', '555-1008');
INSERT INTO CUSTOMER (customer_name, customer_address, phone) VALUES ('Benjamin Anderson', '44 Ash Cir', '555-1009');
INSERT INTO CUSTOMER (customer_name, customer_address, phone) VALUES ('Isabella Thomas', '55 Chestnut Blvd', '555-1010');

-- Accounts
-- Assuming customer_id matches the insertion order (1 to 10) due to seq_customer_id starting at 1
INSERT INTO ACCOUNT (account_number, ref_customer_id, ref_branch_code, date_of_creation, current_balance) VALUES ('ACC-00001001', 1, 'QSB0000001', SYSDATE - 300, 5000.00);
INSERT INTO ACCOUNT (account_number, ref_customer_id, ref_branch_code, date_of_creation, current_balance) VALUES ('ACC-00001002', 1, 'QSB0000001', SYSDATE - 150, 15000.00);
INSERT INTO ACCOUNT (account_number, ref_customer_id, ref_branch_code, date_of_creation, current_balance) VALUES ('ACC-00002001', 2, 'QSB0000002', SYSDATE - 400, 3200.50);
INSERT INTO ACCOUNT (account_number, ref_customer_id, ref_branch_code, date_of_creation, current_balance) VALUES ('ACC-00003001', 3, 'QSB0000003', SYSDATE - 50, 10500.00);
INSERT INTO ACCOUNT (account_number, ref_customer_id, ref_branch_code, date_of_creation, current_balance) VALUES ('ACC-00004001', 4, 'QSB0000001', SYSDATE - 800, 250.00);
INSERT INTO ACCOUNT (account_number, ref_customer_id, ref_branch_code, date_of_creation, current_balance) VALUES ('ACC-00005001', 5, 'QSB0000004', SYSDATE - 120, 8900.00);
INSERT INTO ACCOUNT (account_number, ref_customer_id, ref_branch_code, date_of_creation, current_balance) VALUES ('ACC-00006001', 6, 'QSB0000005', SYSDATE - 60, 45000.00);
INSERT INTO ACCOUNT (account_number, ref_customer_id, ref_branch_code, date_of_creation, current_balance) VALUES ('ACC-00007001', 7, 'QSB0000002', SYSDATE - 200, 1200.00);
INSERT INTO ACCOUNT (account_number, ref_customer_id, ref_branch_code, date_of_creation, current_balance) VALUES ('ACC-00008001', 8, 'QSB0000003', SYSDATE - 900, 75000.00);
INSERT INTO ACCOUNT (account_number, ref_customer_id, ref_branch_code, date_of_creation, current_balance) VALUES ('ACC-00009001', 9, 'QSB0000004', SYSDATE - 30, 800.00);
INSERT INTO ACCOUNT (account_number, ref_customer_id, ref_branch_code, date_of_creation, current_balance) VALUES ('ACC-00010001', 10, 'QSB0000005', SYSDATE - 5, 2000.00);

-- Cards (Assumes account_id matches insert order 1-11)
INSERT INTO CARD (card_number, card_type, date_of_issuance, date_of_expiry, cvv_code, ref_account_id) VALUES ('4111222233334444', 'DEBIT', SYSDATE - 300, SYSDATE + 795, '123', 1);
INSERT INTO CARD (card_number, card_type, date_of_issuance, date_of_expiry, cvv_code, ref_account_id) VALUES ('5111222233334444', 'CREDIT', SYSDATE - 150, SYSDATE + 945, '456', 2);
INSERT INTO CARD (card_number, card_type, date_of_issuance, date_of_expiry, cvv_code, ref_account_id) VALUES ('4222333344445555', 'DEBIT', SYSDATE - 400, SYSDATE + 695, '789', 3);
INSERT INTO CARD (card_number, card_type, date_of_issuance, date_of_expiry, cvv_code, ref_account_id) VALUES ('5222333344445555', 'CREDIT', SYSDATE - 50, SYSDATE + 1045, '321', 4);
INSERT INTO CARD (card_number, card_type, date_of_issuance, date_of_expiry, cvv_code, ref_account_id) VALUES ('4333444455556666', 'DEBIT', SYSDATE - 800, SYSDATE + 295, '654', 5);

-- Beneficiaries
INSERT INTO BENEFICIARY (beneficiary_name, phone, iban, ref_account_id, ref_customer_id) VALUES ('Alice Mother', '555-9001', 'IBAN12345678901', 1, 1);
INSERT INTO BENEFICIARY (beneficiary_name, phone, iban, ref_account_id, ref_customer_id) VALUES ('Bob Brother', '555-9002', 'IBAN12345678902', 3, 2);
INSERT INTO BENEFICIARY (beneficiary_name, phone, iban, ref_account_id, ref_customer_id) VALUES ('Charlie Son', '555-9003', 'IBAN12345678903', 4, 3);

-- Transactions
-- These inserts will trigger the trg_before_transaction_balance and update the accounts accordingly
INSERT INTO TRANSACTION (ref_customer_id, ref_branch_code, transaction_type, transaction_amount, transaction_date) VALUES (1, 'QSB0000001', 'DEPOSIT', 1000.00, SYSDATE - 10);
INSERT INTO TRANSACTION (ref_customer_id, ref_branch_code, transaction_type, transaction_amount, transaction_date) VALUES (2, 'QSB0000002', 'WITHDRAWAL', 500.00, SYSDATE - 5);
INSERT INTO TRANSACTION (ref_customer_id, ref_branch_code, transaction_type, transaction_amount, transaction_date, receiving_account) VALUES (3, 'QSB0000003', 'TRANSFER', 200.00, SYSDATE - 2, 'ACC-00001001');

-- Loans
INSERT INTO LOAN (loan_amount, interest_rate, term_months, application_date, approval_status, ref_account_id, ref_customer_id) VALUES (50000, 5.5, 60, SYSDATE - 60, 'APPROVED', 1, 1);
INSERT INTO LOAN (loan_amount, interest_rate, term_months, application_date, approval_status, ref_account_id, ref_customer_id) VALUES (15000, 7.0, 36, SYSDATE - 10, 'PENDING', 3, 2);
INSERT INTO LOAN (loan_amount, interest_rate, term_months, application_date, approval_status, ref_account_id, ref_customer_id) VALUES (100000, 4.5, 120, SYSDATE - 300, 'APPROVED', 8, 8);

-- Loan Payments
INSERT INTO LOAN_PAY (ref_loan_id, ref_customer_id, payment_date, payment_amount, remaining_balance, payment_status) VALUES (1, 1, SYSDATE - 30, 966.67, 49033.33, 'COMPLETED');
INSERT INTO LOAN_PAY (ref_loan_id, ref_customer_id, payment_date, payment_amount, remaining_balance, payment_status) VALUES (3, 8, SYSDATE - 270, 1200.00, 98800.00, 'COMPLETED');

COMMIT;
