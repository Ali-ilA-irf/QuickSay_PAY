import cx_Oracle  # type: ignore
import threading


class DatabaseConnection:
    _instance   = None
    _connection = None
    _lock       = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def connect(self):
        with self._lock:
            if self._connection is None:
                try:
                    self._connection = cx_Oracle.connect("system/123@localhost/XE")
                    print("Database connected successfully.")
                except cx_Oracle.Error as e:
                    print(f"Error connecting to Oracle DB: {e}")
                    return False
        return True

    def get_connection(self):
        if self._connection is None:
            self.connect()
        return self._connection

    def close(self):
        with self._lock:
            if self._connection:
                self._connection.close()
                self._connection = None
                print("Database connection closed.")

    def execute_query(self, query: str, parameters: dict | None = None) -> list | None:
        """SELECT queries — returns list of dicts, or None on error."""
        if not self.connect():
            return None
        with self._lock:
            cursor = self._connection.cursor()
            try:
                cursor.execute(query, parameters or {})
                columns = [col[0] for col in cursor.description]
                cursor.rowfactory = lambda *args: dict(zip(columns, args))
                return cursor.fetchall()
            except cx_Oracle.Error as e:
                print(f"Query Error: {e}")
                return None
            finally:
                cursor.close()

    def execute_update(self, query: str, parameters: dict | None = None) -> bool:
        """
        Fallback for simple INSERTs/UPDATEs/DELETEs that do NOT have
        a matching stored procedure yet.
        Prefer call_procedure() for all DML.
        """
        if not self.connect():
            return False
        with self._lock:
            cursor = self._connection.cursor()
            try:
                cursor.execute(query, parameters or {})
                self._connection.commit()
                return True
            except cx_Oracle.Error as e:
                print(f"Update Error: {e}")
                self._connection.rollback()
                return False
            finally:
                cursor.close()

    def call_procedure(self, proc_name: str, params: list | None = None) -> bool:
        """
        Call a stored procedure defined in 07_procedures.sql.
        params is a plain list of IN arguments in positional order.
        Returns True on success, False on error.

        Example:
            db.call_procedure('pr_add_employee',
                              ['john', 'pass123', 'TELLER', 'BR01'])
        """
        if not self.connect():
            return False
        with self._lock:
            cursor = self._connection.cursor()
            try:
                cursor.callproc(proc_name, params or [])
                self._connection.commit()
                return True
            except cx_Oracle.Error as e:
                print(f"Procedure Error [{proc_name}]: {e}")
                self._connection.rollback()
                return False
            finally:
                cursor.close()

    def call_function(self, func_name: str, return_type,
                      params: list | None = None):
        """
        Call a stored function defined in 08_functions.sql.
        return_type is a cx_Oracle type (e.g. cx_Oracle.NUMBER).

        Example:
            bal = db.call_function('fn_get_customer_balance',
                                   cx_Oracle.NUMBER, [customer_id])
        """
        if not self.connect():
            return None
        with self._lock:
            cursor = self._connection.cursor()
            try:
                result = cursor.callfunc(func_name, return_type, params or [])
                return result
            except cx_Oracle.Error as e:
                print(f"Function Error [{func_name}]: {e}")
                return None
            finally:
                cursor.close()
