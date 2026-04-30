import tkinter as tk
import customtkinter as ctk
from gui.models.account_model import AccountModel
from gui.utils.fast_table import make_treeview, populate_tree

NAVY = "#0D1B2A"; GOLD = "#E8A020"
BG = "#F0F4F8"; WHITE = "#FFFFFF"
T1 = "#1A1A2E"; T2 = "#6B7280"; FONT = "Segoe UI"


class ManageAccountsPage(tk.Frame):
    """Read-only account viewer for Admin. Teller creates accounts."""
    COLS = ["ID", "Account No.", "Customer", "Phone", "Branch",
            "Balance (PKR)", "Opened On"]

    def __init__(self, master, **kw):
        super().__init__(master, bg=BG, **kw)
        self.acc_m = AccountModel()
        self._all_rows = []
        self._build_toolbar()
        self._build_table()
        self.refresh()

    def _build_toolbar(self):
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=20, pady=(16, 8))
        self._sv = tk.StringVar()
        e = ctk.CTkEntry(bar, placeholder_text="🔍  Search account number, customer or branch…",
                         textvariable=self._sv, fg_color=WHITE,
                         border_color=GOLD, border_width=1,
                         text_color=T1, placeholder_text_color="#9CA3AF", height=36, corner_radius=8)
        e.pack(side="left", fill="x", expand=True)
        e.bind("<KeyRelease>", lambda _: self._do_search())
        tk.Button(bar, text="↺ Refresh", command=self.refresh,
                  bg=WHITE, fg=T1, font=(FONT, 11, "bold"),
                  bd=0, padx=14, pady=8, cursor="hand2").pack(side="left", padx=(8, 0))

        # Total balance badge
        self._bal_lbl = tk.Label(bar, text="Total: PKR —",
                                 bg=NAVY, fg=GOLD,
                                 font=(FONT, 11, "bold"), padx=14, pady=8)
        self._bal_lbl.pack(side="right")

    def _build_table(self):
        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12)
        card.pack(fill="both", expand=True, padx=20, pady=(4, 20))
        self._tv = make_treeview(card, self.COLS)

    def refresh(self):
        self._all_rows = self.acc_m.get_all_accounts()
        self._sv.set("")
        self._render(self._all_rows)
        # Update total
        total = sum(float(r.get("CURRENT_BALANCE", 0) or 0)
                    for r in self._all_rows)
        self._bal_lbl.config(text=f"Total: PKR {total:,.2f}")

    def _do_search(self):
        kw = self._sv.get().strip().lower()
        data = [r for r in self._all_rows
                if not kw
                or kw in str(r.get("ACCOUNT_NUMBER","")).lower()
                or kw in str(r.get("CUSTOMER_NAME","")).lower()
                or kw in str(r.get("BRANCH_CODE","")).lower()]
        self._render(data)

    def _render(self, rows):
        populate_tree(self._tv, [
            [r.get("ACCOUNT_ID",""),
             r.get("ACCOUNT_NUMBER",""),
             r.get("CUSTOMER_NAME",""),
             r.get("PHONE",""),
             r.get("BRANCH_CODE",""),
             f"PKR {float(r.get('CURRENT_BALANCE', 0) or 0):,.2f}",
             r.get("CREATED_ON","")]
            for r in rows])