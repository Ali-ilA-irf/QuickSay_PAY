from gui.db_connection import DatabaseConnection


class BeneficiaryModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_beneficiaries(self) -> list:
        return self.db.execute_query("SELECT * FROM vw_beneficiary_details") or []

    def get_beneficiaries_by_customer(self, customer_id: int) -> list:
        return self.db.execute_query(
            "SELECT * FROM vw_beneficiary_details WHERE customer_id = :cid",
            {"cid": customer_id},
        ) or []

    def get_ibans_for_transfer(self, customer_id: int) -> list:
        result = self.get_beneficiaries_by_customer(customer_id)
        return [r["IBAN"] for r in result]

    def add_beneficiary(self, name: str, phone: str, iban: str,
                        customer_id: int) -> bool:
        # pr_add_beneficiary defined in 07_procedures.sql
        return self.db.call_procedure(
            "pr_add_beneficiary",
            [name, phone, iban, customer_id])

    def delete_beneficiary(self, beneficiary_id: int) -> bool:
        # pr_delete_beneficiary defined in 07_procedures.sql
        return self.db.call_procedure("pr_delete_beneficiary", [beneficiary_id])
