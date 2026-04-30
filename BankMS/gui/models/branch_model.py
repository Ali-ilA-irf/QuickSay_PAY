from gui.db_connection import DatabaseConnection


class BranchModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_branches(self) -> list:
        return self.db.execute_query("SELECT * FROM vw_branch_details") or []

    def get_branch_codes(self) -> list:
        result = self.db.execute_query("SELECT branch_code FROM vw_branch_details")
        return [r["BRANCH_CODE"] for r in result] if result else []

    def get_total_count(self) -> int:
        result = self.db.execute_query("SELECT branches FROM vw_system_kpi")
        return int(result[0]["BRANCHES"]) if result else 0

    def create_branch(self, branch_code: str, address: str, phone: str) -> bool:
        # pr_add_branch defined in 07_procedures.sql
        return self.db.call_procedure("pr_add_branch", [branch_code, address, phone])

    def delete_branch(self, branch_code: str) -> bool:
        # pr_delete_branch defined in 07_procedures.sql
        return self.db.call_procedure("pr_delete_branch", [branch_code])
