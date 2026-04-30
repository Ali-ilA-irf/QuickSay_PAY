from gui.db_connection import DatabaseConnection


class EmployeeModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def authenticate_user(self, username: str, password: str) -> dict | None:
        result = self.db.execute_query(
            "SELECT * FROM vw_system_login WHERE username = :u AND password = :p",
            {"u": username, "p": password},
        )
        return result[0] if result else None

    def get_all_employees(self) -> list:
        return self.db.execute_query("SELECT * FROM vw_employee_details") or []

    def get_total_counts(self) -> dict:
        result = self.db.execute_query("SELECT * FROM vw_system_kpi")
        return result[0] if result else {}

    def create_employee(self, username: str, password: str,
                        role: str, branch_code: str) -> bool:
        # pr_add_employee defined in 07_procedures.sql
        return self.db.call_procedure(
            "pr_add_employee", [username, password, role, branch_code])

    def update_employee(self, employee_id: int, role: str,
                        branch_code: str) -> bool:
        # pr_update_employee defined in 07_procedures.sql
        return self.db.call_procedure(
            "pr_update_employee", [employee_id, role, branch_code])

    def delete_employee(self, employee_id: int) -> bool:
        # pr_delete_employee defined in 07_procedures.sql
        return self.db.call_procedure("pr_delete_employee", [employee_id])
