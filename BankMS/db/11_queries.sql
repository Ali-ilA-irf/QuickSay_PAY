-- 11_queries.sql

-- 1. Get Top 5 Customers by Total Balance
SELECT * FROM (
    SELECT c.customer_name, SUM(a.current_balance) as total_wealth
    FROM CUSTOMER c
    JOIN ACCOUNT a ON c.customer_id = a.ref_customer_id
    GROUP BY c.customer_id, c.customer_name
    ORDER BY SUM(a.current_balance) DESC
) WHERE ROWNUM <= 5;

-- 2. See all pending loans that need approval
SELECT loan_id, loan_amount, term_months, application_date
FROM LOAN
WHERE approval_status = 'PENDING'
ORDER BY application_date ASC;

-- 3. Monthly Transaction Volume (Number of transactions and total amount per type)
SELECT transaction_type, COUNT(*) as num_transactions, SUM(transaction_amount) as total_volume
FROM TRANSACTION
WHERE EXTRACT(MONTH FROM transaction_date) = EXTRACT(MONTH FROM SYSDATE)
  AND EXTRACT(YEAR FROM transaction_date) = EXTRACT(YEAR FROM SYSDATE)
GROUP BY transaction_type;

-- 4. Find accounts with cards expiring in the next 30 days
SELECT a.account_number, c.customer_name, cd.card_number, cd.date_of_expiry
FROM CARD cd
JOIN ACCOUNT a ON cd.ref_account_id = a.account_id
JOIN CUSTOMER c ON a.ref_customer_id = c.customer_id
WHERE cd.date_of_expiry BETWEEN SYSDATE AND SYSDATE + 30;

-- 5. Find customers whose total balance is above average (Using Function in SELECT and Correlated Subquery)
SELECT c.customer_name, 
       fn_get_customer_balance(c.customer_id) as total_balance
FROM CUSTOMER c
WHERE fn_get_customer_balance(c.customer_id) > (
    SELECT AVG(current_balance) FROM ACCOUNT
);

-- 6. Branches and the number of active loans they originated (JOIN + GROUP BY)
SELECT b.branch_code, b.branch_address, COUNT(l.loan_id) as active_loans
FROM BRANCH b
JOIN ACCOUNT a ON b.branch_code = a.ref_branch_code
JOIN LOAN l ON a.account_id = l.ref_account_id
WHERE l.approval_status = 'APPROVED'
GROUP BY b.branch_code, b.branch_address;

-- 7. Correlated Subquery: Find the accounts with the highest balance in their respective branch
SELECT a1.account_number, a1.current_balance, a1.ref_branch_code
FROM ACCOUNT a1
WHERE a1.current_balance = (
    SELECT MAX(a2.current_balance)
    FROM ACCOUNT a2
    WHERE a2.ref_branch_code = a1.ref_branch_code
);

-- 8. Customer Details with their Beneficiaries (JOIN)
SELECT c.customer_name, b.beneficiary_name, b.iban
FROM CUSTOMER c
LEFT JOIN BENEFICIARY b ON c.customer_id = b.ref_customer_id
WHERE b.beneficiary_id IS NOT NULL;

-- 5. Left Outer Join: All Customers and their Loans (if any)
SELECT c.customer_name, l.loan_amount, l.approval_status
FROM CUSTOMER c
LEFT OUTER JOIN LOAN l ON c.customer_id = l.ref_customer_id
WHERE c.customer_name LIKE '%' OR c.customer_name IS NOT NULL;

-- 6. Self Join: Find Employees working in the same branch as 'admin_user'
SELECT e1.username as Employee, e2.username as Colleague, e1.ref_branch_code
FROM EMPLOYEE e1
JOIN EMPLOYEE e2 ON e1.ref_branch_code = e2.ref_branch_code
WHERE e1.username = 'admin_user' AND e2.username != 'admin_user';

-- 7. Subquery + Group By: Branches with more than average number of accounts
SELECT b.branch_code, COUNT(a.account_id) as total_accounts
FROM BRANCH b
JOIN ACCOUNT a ON b.branch_code = a.ref_branch_code
GROUP BY b.branch_code
HAVING COUNT(a.account_id) > (
    SELECT COUNT(account_id) / COUNT(DISTINCT ref_branch_code)
    FROM ACCOUNT
);
