from gui.db_connection import DatabaseConnection


class LoanPaymentModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_payments_by_loan(self, loan_id: int) -> list:
        return self.db.execute_query(
            "SELECT * FROM vw_loan_payments WHERE ref_loan_id = :lid",
            {"lid": loan_id},
        ) or []

    def get_payments_by_customer(self, customer_id: int) -> list:
        return self.db.execute_query(
            "SELECT * FROM vw_loan_payments WHERE ref_customer_id = :cid",
            {"cid": customer_id},
        ) or []

    def record_payment(self, loan_id: int, customer_id: int, account_id: int,
                       amount: float, remaining: float) -> bool:
        # pr_record_payment defined in 07_procedures.sql
        return self.db.call_procedure(
            "pr_record_payment", [loan_id, customer_id, account_id, amount, remaining])
