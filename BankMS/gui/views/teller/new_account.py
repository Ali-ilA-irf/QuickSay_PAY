import tkinter as tk
import customtkinter as ctk
from gui.models.account_model import AccountModel
from gui.models.customer_model import CustomerModel

NAVY = "#0D1B2A"; GOLD = "#E8A020"; BG = "#F0F4F8"; WHITE = "#FFFFFF"
T1 = "#1A1A2E"; T2 = "#6B7280"; GREEN = "#27AE60"; RED = "#E74C3C"
FONT = "Segoe UI"


class NewAccountPage(tk.Frame):
    def __init__(self, master, branch_code: str, user_data: dict, **kw):
        super().__init__(master, bg=BG, **kw)
        self.branch_code = branch_code
        self.user_data = user_data
        self.acc_m = AccountModel()
        self.cust_m = CustomerModel()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12)
        card.pack(fill="both", expand=True, padx=80, pady=80)
        
        tk.Label(card, text="🏦 Open New Account", bg=WHITE, fg=NAVY,
                 font=(FONT, 16, "bold")).pack(pady=(24, 16))

        tk.Label(card, text="Search Customer (ID or Name)", bg=WHITE, fg=T2, font=(FONT, 11)).pack(anchor="w", padx=30, pady=(10, 2))
        self.search_var = ctk.StringVar()
        s_entry = ctk.CTkEntry(card, textvariable=self.search_var, placeholder_text="🔍  Type customer ID or name…",
                               fg_color=WHITE, border_color=GOLD, border_width=1,
                               height=36, corner_radius=8, text_color=T1, placeholder_text_color="#9CA3AF")
        s_entry.pack(fill="x", padx=30)
        s_entry.bind("<KeyRelease>", lambda _: self._filter_customers())

        tk.Label(card, text="Select Customer", bg=WHITE, fg=T2, font=(FONT, 11)).pack(anchor="w", padx=30, pady=(10, 2))
        self.cust_var = ctk.StringVar()
        self.cust_menu = ctk.CTkOptionMenu(card, variable=self.cust_var, values=["Loading..."],
                                           fg_color=WHITE, text_color=T1, button_color=GOLD,
                                           height=40, corner_radius=8, anchor="w")
        self.cust_menu.pack(fill="x", padx=30)

        self._f_bal = self._field(card, "Initial Deposit (PKR)")

        self._ferr = tk.Label(card, text="", bg=WHITE, font=(FONT, 11))
        self._ferr.pack(pady=(8, 0))

        tk.Button(card, text="Open Account", bg=GOLD, fg=NAVY,
                  font=(FONT, 12, "bold"), bd=0, padx=14, pady=12,
                  cursor="hand2", command=self._save).pack(fill="x", padx=30, pady=(12, 24))

    def _field(self, parent, label):
        tk.Label(parent, text=label, bg=WHITE, fg=T2, font=(FONT, 11)).pack(anchor="w", padx=30, pady=(10, 2))
        var = tk.StringVar()
        ctk.CTkEntry(parent, textvariable=var, fg_color=WHITE,
                     border_color=GOLD, border_width=1,
                     height=40, corner_radius=8, text_color=T1).pack(fill="x", padx=30)
        return var

    def refresh(self):
        self.all_custs = self.cust_m.get_all_customers() or []
        self._filter_customers()

    def _filter_customers(self):
        kw = self.search_var.get().strip().lower()
        filtered = [c for c in self.all_custs if kw in str(c.get("CUSTOMER_ID", "")).lower() or kw in str(c.get("CUSTOMER_NAME", "")).lower()]
        self.cust_map = {f"{c.get('CUSTOMER_ID')} - {c.get('CUSTOMER_NAME')}": c.get("CUSTOMER_ID") for c in filtered}
        vals = list(self.cust_map.keys())
        if vals:
            self.cust_menu.configure(values=vals)
            self.cust_var.set(vals[0])
        else:
            self.cust_menu.configure(values=["No Customers found"])
            self.cust_var.set("No Customers found")

    def _save(self):
        if not self.cust_map: return
        try:
            import random
            cid = self.cust_map[self.cust_var.get()]
            bal = float(self._f_bal.get().strip() or 0)
            if bal < 0: raise ValueError
            
            acc_num = f"AC{random.randint(10000000, 99999999)}"
            
            if self.acc_m.create_account(acc_num, cid, self.branch_code, bal, self.user_data.get("EMPLOYEE_ID")):
                self._ferr.config(text=f"✓ Account {acc_num} opened successfully!", fg=GREEN)
                self._f_bal.set("")
            else:
                self._ferr.config(text="❌ Failed to open. Check console.", fg=RED)
        except ValueError:
            self._ferr.config(text="Invalid Initial Deposit amount.", fg=RED)