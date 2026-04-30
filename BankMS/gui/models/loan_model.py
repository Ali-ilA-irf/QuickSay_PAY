from gui.db_connection import DatabaseConnection


class LoanModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_loans(self) -> list:
        return self.db.execute_query("SELECT * FROM vw_loan_full") or []

    def get_pending_loans(self) -> list:
        return self.db.execute_query("SELECT * FROM vw_pending_loans") or []

    def get_loans_by_customer(self, customer_id: int) -> list:
        return self.db.execute_query(
            "SELECT * FROM vw_loan_full WHERE customer_id = :cid",
            {"cid": customer_id},
        ) or []

    def get_pending_count(self) -> int:
        result = self.db.execute_query("SELECT pending_loans FROM vw_system_kpi")
        return int(result[0]["PENDING_LOANS"]) if result else 0

    def approve_loan(self, loan_id: int, employee_id: int = 0) -> bool:
        # pr_approve_loan defined in 07_procedures.sql
        return self.db.call_procedure("pr_approve_loan", [loan_id, employee_id])

    def reject_loan(self, loan_id: int, employee_id: int = 0) -> bool:
        # pr_reject_loan defined in 07_procedures.sql
        return self.db.call_procedure("pr_reject_loan", [loan_id, employee_id])

    def calc_monthly_interest(self, loan_id: int) -> float:
        """Call fn_calc_monthly_loan_interest and return monthly interest PKR as float."""
        import cx_Oracle
        result = self.db.call_function('fn_calc_monthly_loan_interest', cx_Oracle.NUMBER, [loan_id])
        try:
            return float(result) if result is not None else 0.0
        except Exception:
            return 0.0

    def request_loan(self, ref_account_id: int, customer_id: int, loan_amount: float, interest_rate: float = 10.0, term_months: int = 12) -> bool:
        """Insert a loan application into LOAN table (approval pending)."""
        sql = (
            "INSERT INTO LOAN (loan_amount, interest_rate, term_months, application_date, approval_status, ref_account_id, ref_customer_id) "
            "VALUES (:loan_amount, :interest_rate, :term_months, SYSDATE, 'PENDING', :ref_account_id, :ref_customer_id)"
        )
        params = {
            'loan_amount': loan_amount,
            'interest_rate': interest_rate,
            'term_months': term_months,
            'ref_account_id': ref_account_id,
            'ref_customer_id': customer_id,
        }
        return self.db.execute_update(sql, params)
