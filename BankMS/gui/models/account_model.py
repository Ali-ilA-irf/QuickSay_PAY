from gui.db_connection import DatabaseConnection


class AccountModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_accounts(self) -> list:
        return self.db.execute_query("SELECT * FROM vw_account_details") or []

    def get_accounts_by_customer(self, customer_id: int) -> list:
        return self.db.execute_query(
            "SELECT * FROM vw_account_details WHERE customer_id = :cid",
            {"cid": customer_id},
        ) or []

    def get_count_per_branch(self) -> list:
        return self.db.execute_query("SELECT * FROM vw_branch_account_counts") or []

    def get_total_balance(self) -> float:
        result = self.db.execute_query("SELECT total_balance FROM vw_system_kpi")
        return float(result[0]["TOTAL_BALANCE"]) if result else 0.0

    def get_total_count(self) -> int:
        result = self.db.execute_query("SELECT accounts FROM vw_system_kpi")
        return int(result[0]["ACCOUNTS"]) if result else 0

    def create_account(self, account_number: str, customer_id: int,
                       branch_code: str, initial_balance: float, employee_id: int = None) -> bool:
        # pr_open_account defined in 07_procedures.sql
        return self.db.call_procedure(
            "pr_open_account",
            [account_number, customer_id, branch_code, initial_balance, employee_id])

    def get_customer_balance(self, customer_id: int) -> float:
        """Return total balance for a customer."""
        result = self.db.execute_query(
            "SELECT NVL(SUM(current_balance), 0) AS total FROM ACCOUNT WHERE ref_customer_id = :cid",
            {"cid": customer_id}
        )
        try:
            return float(result[0]["TOTAL"]) if result else 0.0
        except Exception:
            return 0.0
