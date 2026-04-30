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
