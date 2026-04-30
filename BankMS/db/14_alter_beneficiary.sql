-- Run this script to drop the unnecessary internal account requirement for beneficiaries.

ALTER TABLE BENEFICIARY DROP CONSTRAINT fk_beneficiary_ref_account;
ALTER TABLE BENEFICIARY DROP COLUMN ref_account_id;
COMMIT;
/
