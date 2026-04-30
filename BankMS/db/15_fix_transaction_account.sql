-- ============================================================
-- 15_fix_transaction_account.sql
-- FIX: Add optional ref_account_id to TRANSACTION table.
-- pr_record_payment (07_procedures.sql) needs this column.
-- Run ONCE after 01_tables.sql if column does not exist.
-- ============================================================

ALTER TABLE TRANSACTION
    ADD ref_account_id NUMBER(10);

ALTER TABLE TRANSACTION
    ADD CONSTRAINT fk_transaction_ref_account
        FOREIGN KEY (ref_account_id) REFERENCES ACCOUNT(account_id);

COMMIT;
/
