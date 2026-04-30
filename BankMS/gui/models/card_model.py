from gui.db_connection import DatabaseConnection


class CardModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_cards(self) -> list:
        return self.db.execute_query("SELECT * FROM vw_card_details") or []

    def get_cards_by_account(self, account_id: int) -> list:
        return self.db.execute_query(
            "SELECT * FROM vw_card_details WHERE account_id = :aid",
            {"aid": account_id},
        ) or []

    def get_cards_by_customer(self, customer_id: int) -> list:
        return self.db.execute_query(
            "SELECT * FROM vw_card_details WHERE customer_id = :cid",
            {"cid": customer_id},
        ) or []

    def issue_card(self, card_number: str, card_type: str,
                   cvv: str, account_id: int, expiry_years: int = 3) -> bool:
        # pr_issue_card defined in 07_procedures.sql
        return self.db.call_procedure(
            "pr_issue_card",
            [card_number, card_type, cvv, account_id, expiry_years * 12])

    def deactivate_card(self, card_id: int) -> bool:
        # pr_deactivate_card defined in 07_procedures.sql
        return self.db.call_procedure("pr_deactivate_card", [card_id])
