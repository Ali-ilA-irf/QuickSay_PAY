from gui.db_connection import DatabaseConnection


class AuditModel:
    def __init__(self):
        self.db = DatabaseConnection()

    def get_all_logs(self) -> list:
        """All audit log entries — vw_audit_log_details (ordered ASC by timestamp)."""
        return self.db.execute_query("SELECT * FROM vw_audit_log_details") or []
