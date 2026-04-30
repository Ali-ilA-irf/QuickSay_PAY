import tkinter as tk
import customtkinter as ctk
from gui.models.account_model import AccountModel
from gui.utils.fast_table import make_treeview, populate_tree

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY   = "#0D1B2A"; GOLD = "#E8A020"; BG = "#F0F4F8"; WHITE = "#FFFFFF"
T1     = "#1A1A2E"; T2 = "#6B7280"; GREEN = "#27AE60"; FONT = "Segoe UI"


class MyAccountsPage(tk.Frame):
    COLS = ["Account Number", "Type", "Created On", "Balance (PKR)", "Branch"]

    def __init__(self, master, customer_id, **kw):
        super().__init__(master, bg=BG, **kw)
        self.customer_id = customer_id
        self.acc_m = AccountModel()
        
        self._build_ui()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=30, pady=(30, 10))
        
        tk.Label(hdr, text="My Bank Accounts", bg=BG, fg=NAVY, 
                 font=(FONT, 18, "bold")).pack(side="left")
        
        tk.Button(hdr, text="↺ Refresh", command=self.refresh,
                  bg=WHITE, fg=T1, font=(FONT, 10, "bold"),
                  bd=0, padx=12, pady=6, cursor="hand2").pack(side="right")

        # Table Card
        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12)
        card.pack(fill="both", expand=True, padx=30, pady=20)
        
        self._tv = make_treeview(card, self.COLS)
        
        # Summary footer inside card
        footer = tk.Frame(card, bg=WHITE, height=50)
        footer.pack(fill="x", side="bottom")
        tk.Frame(footer, bg=BG, height=1).pack(fill="x", side="top")
        
        self._l_total = tk.Label(footer, text="Total Balance: PKR 0.00", 
                                 bg=WHITE, fg=NAVY, font=(FONT, 12, "bold"))
        self._l_total.pack(side="right", padx=20, pady=10)

    def refresh(self):
        rows = self.acc_m.get_accounts_by_customer(self.customer_id) or []
        
        data = []
        total = 0
        for r in rows:
            bal = float(r.get("CURRENT_BALANCE") or 0)
            total += bal
            data.append([
                r.get("ACCOUNT_NUMBER", "—"),
                "Savings" if bal > 0 else "Checking", # Mock type for now
                r.get("CREATED_ON", "—"),
                f"PKR {bal:,.2f}",
                r.get("BRANCH_CODE", "Main")
            ])
            
        self.after(0, lambda: populate_tree(self._tv, data))
        self.after(0, lambda: self._l_total.config(text=f"Total Balance: PKR {total:,.2f}"))