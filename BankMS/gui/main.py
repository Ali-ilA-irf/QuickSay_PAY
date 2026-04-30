import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from gui.db_connection import DatabaseConnection
from gui.views.login import LoginWindow

# ── Global Theme ─────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Load Custom Fonts (Windows only logic for Playfair Display)
def load_custom_fonts():
    if sys.platform == "win32":
        import ctypes
        from ctypes import wintypes
        FR_PRIVATE = 0x10
        gdi32 = ctypes.WinDLL('gdi32', use_last_error=True)
        add_font_resource_ex = gdi32.AddFontResourceExW
        
        font_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "fonts")
        if os.path.exists(font_dir):
            for font_file in os.listdir(font_dir):
                if font_file.endswith(".ttf"):
                    font_path = os.path.join(font_dir, font_file)
                    add_font_resource_ex(font_path, FR_PRIVATE, 0)
load_custom_fonts()

COLORS = {
    "bg_primary":   "#0A1628",
    "bg_secondary": "#1E3A5F",
    "accent":       "#C9A84C",
    "accent_hover": "#E8C060",
    "text_primary": "#FFFFFF",
    "text_muted":   "#E0E0E0",
    "success":      "#2ECC71",
    "error":        "#E74C3C",
    "warning":      "#F39C12",
    "sidebar":      "#061020",
    "card":         "#132338",
}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("QuickSay Pay")
        self.geometry("1280x800")
        self.minsize(1100, 700)
        self.configure(fg_color=COLORS["bg_primary"])

        # Centre window on screen
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = (sw - 1280) // 2
        y  = (sh - 800)  // 2
        self.geometry(f"1280x800+{x}+{y}")

        # Initialise DB connection (singleton)
        self.db = DatabaseConnection()
        self.db.connect()

        # Current dashboard widget reference
        self._current_view = None

        # Show login
        self.show_login()

    # ── Navigation ────────────────────────────────────────────────────────────
    def show_login(self):
        self._clear_view()
        login = LoginWindow(self, on_success=self.on_login_success)
        login.pack(fill="both", expand=True)
        self._current_view = login

    def on_login_success(self, user_data: dict):
        """Called by LoginWindow after successful authentication."""
        import traceback
        # Normalize login result keys so GUI components can read EMPLOYEE_ID and USER_ID consistently
        if user_data:
            uid = user_data.get('USER_ID') or user_data.get('EMPLOYEE_ID')
            if uid is not None:
                user_data['USER_ID'] = uid
                user_data['EMPLOYEE_ID'] = uid
            # copy lowercase view keys if present (defensive)
            if 'branch_code' in user_data and 'BRANCH_CODE' not in user_data:
                user_data['BRANCH_CODE'] = user_data['branch_code']
            if 'display_name' in user_data and 'DISPLAY_NAME' not in user_data:
                user_data['DISPLAY_NAME'] = user_data['display_name']
        role = user_data.get("ROLE", "") if user_data else ""
        print(f"[DEBUG] Login success — role={role}, user={user_data.get('USERNAME')}")
        self._clear_view()

        try:
            if role == "ADMIN":
                from gui.views.admin.admin_main import AdminDashboard
                view = AdminDashboard(self, user_data, logout_cb=self.logout)
            elif role == "MANAGER":
                from gui.views.manager.manager_main import ManagerDashboard
                view = ManagerDashboard(self, user_data, logout_cb=self.logout)
            elif role == "TELLER":
                from gui.views.teller.teller_main import TellerDashboard
                view = TellerDashboard(self, user_data, logout_cb=self.logout)
            elif role == "CUSTOMER":
                from gui.views.customer.customer_main import CustomerDashboard
                view = CustomerDashboard(self, user_data, logout_cb=self.logout)
            else:
                print(f"[WARN] Unknown role '{role}' — returning to login.")
                self.show_login()
                return

            view.pack(fill="both", expand=True)
            self._current_view = view
            print("[DEBUG] Dashboard packed successfully.")
        except Exception as e:
            with open("error.txt", "w") as f:
                traceback.print_exc(file=f)
            traceback.print_exc()
            self.show_login()  # fall back so app doesn't hang blank

    def logout(self):
        self._clear_view()
        self.show_login()

    def _clear_view(self):
        if self._current_view:
            self._current_view.destroy()
            self._current_view = None

    def on_closing(self):
        self.db.close()
        self.destroy()


if __name__ == "__main__":
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
