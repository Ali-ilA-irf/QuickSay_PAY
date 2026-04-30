from gui.db_connection import DatabaseConnection


class CustomerModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_customers(self) -> list:
        return self.db.execute_query("SELECT * FROM vw_customer_details") or []

    def search_customers(self, keyword: str) -> list:
        kw = f"%{keyword.upper()}%"
        return self.db.execute_query(
            "SELECT * FROM vw_customer_details "
            "WHERE UPPER(customer_name) LIKE :kw OR phone LIKE :kw",
            {"kw": kw},
        ) or []

    def get_total_count(self) -> int:
        result = self.db.execute_query("SELECT customers FROM vw_system_kpi")
        return int(result[0]["CUSTOMERS"]) if result else 0

    def create_customer(self, name: str, address: str, phone: str, password: str, employee_id: int = None) -> bool:
        # pr_add_customer updated in 07_procedures.sql to accept password
        return self.db.call_procedure("pr_add_customer", [name, address, phone, password, employee_id])

    def update_customer(self, customer_id: int, name: str,
                        address: str, phone: str) -> bool:
        # pr_update_customer defined in 07_procedures.sql
        return self.db.call_procedure(
            "pr_update_customer", [customer_id, name, address, phone])
