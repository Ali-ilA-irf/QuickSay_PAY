from gui.db_connection import DatabaseConnection


class TransactionModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_transactions(self) -> list:
        return self.db.execute_query("SELECT * FROM vw_transaction_full") or []

    def get_transactions_by_customer(self, customer_id: int) -> list:
        sql = (
            "SELECT t.transaction_id, TO_CHAR(t.transaction_date, 'Mon DD, YYYY') as TXN_DATE, "
            "t.transaction_type, t.transaction_amount, t.ref_branch_code as BRANCH_CODE, "
            "t.receiving_account "
            "FROM TRANSACTION t "
            "WHERE t.ref_customer_id = :cid "
            "ORDER BY t.transaction_date DESC"
        )
        return self.db.execute_query(sql, {"cid": customer_id}) or []

    def get_daily_totals(self, days: int = 30) -> list:
        """Return daily transaction totals. 'days' parameter currently unused —
        view vw_daily_txn_totals should supply the necessary rows.
        """
        # vw_daily_txn_totals defined in 05_views.sql
        sql = (
            "SELECT TO_CHAR(transaction_date, 'DD-MM') AS txn_day, "
            "TRUNC(transaction_date) AS txn_date, "
            "NVL(SUM(CASE WHEN transaction_type IN ('DEPOSIT','TRANSFER') THEN transaction_amount ELSE 0 END),0) AS deposits, "
            "NVL(SUM(CASE WHEN transaction_type = 'WITHDRAWAL' THEN transaction_amount ELSE 0 END),0) AS withdrawals "
            "FROM TRANSACTION "
            "WHERE transaction_date >= SYSDATE - :days "
            "GROUP BY TO_CHAR(transaction_date, 'DD-MM'), TRUNC(transaction_date) "
            "ORDER BY TRUNC(transaction_date) ASC"
        )
        return self.db.execute_query(sql, {"days": days}) or []

    def get_monthly_counts(self) -> list:
        """Return deposit/withdrawal/transfer counts per month for the last 9 months.
        Queries vw_monthly_txn_counts defined in 05_views.sql.
        Used by: system_reports.py _draw_bar()
        """
        return self.db.execute_query("SELECT * FROM vw_monthly_txn_counts") or []


    def get_today_count(self) -> int:
        # today_transactions column in vw_system_kpi (05_views.sql)
        result = self.db.execute_query("SELECT today_transactions FROM vw_system_kpi")
        return int(result[0]["TODAY_TRANSACTIONS"]) if result else 0

    def deposit(self, account_id: int, branch_code: str, amount: float, employee_id: int = None) -> bool:
        # pr_deposit defined in 07_procedures.sql
        return self.db.call_procedure("pr_deposit", [account_id, branch_code, amount, employee_id])

    def withdraw(self, account_id: int, branch_code: str, amount: float, employee_id: int = None) -> bool:
        # pr_withdraw defined in 07_procedures.sql
        return self.db.call_procedure("pr_withdraw", [account_id, branch_code, amount, employee_id])

    def transfer(self, from_account_id: int, branch_code: str,
                 amount: float, to_account: str, employee_id: int = None) -> bool:
        # pr_transfer_funds defined in 07_procedures.sql
        return self.db.call_procedure(
            "pr_transfer_funds", [from_account_id, branch_code, to_account, amount, employee_id])

    def get_teller_daily_stats(self, employee_id: int) -> dict:
        """Return daily transaction count and total cash processed for a teller using AUDIT_LOG entries.
        Uses REGEXP_SUBSTR to extract numeric amounts from audit descriptions.
        """
        sql = (
            "SELECT COUNT(*) AS VOLUME, NVL(SUM(TO_NUMBER(REGEXP_SUBSTR(description, '[0-9]+(\\.[0-9]+)?'))),0) AS TOTAL_CASH "
            "FROM AUDIT_LOG "
            "WHERE ref_employee_id = :eid "
            "AND TRUNC(timestamp) = TRUNC(SYSDATE) "
            "AND (description LIKE 'Cash deposit%' OR description LIKE 'Cash withdrawal%' OR description LIKE 'Transferred%')"
        )
        res = self.db.execute_query(sql, {"eid": employee_id}) or []
        if not res:
            return {"volume": 0, "total_cash": 0.0}
        row = res[0]
        return {"volume": int(row.get("VOLUME") or 0), "total_cash": float(row.get("TOTAL_CASH") or 0.0)}

    def get_teller_recent_activity(self, employee_id: int, limit: int = 10) -> list:
        """Return recent audit log entries for the given teller (most recent first)."""
        sql = (
            "SELECT log_id, description, TO_CHAR(timestamp, 'DD-Mon-YYYY HH24:MI:SS') AS ACTION_TIME "
            "FROM (SELECT log_id, description, timestamp FROM AUDIT_LOG WHERE ref_employee_id = :eid ORDER BY timestamp DESC) "
            "WHERE ROWNUM <= :lim"
        )
        return self.db.execute_query(sql, {"eid": employee_id, "lim": limit}) or []
