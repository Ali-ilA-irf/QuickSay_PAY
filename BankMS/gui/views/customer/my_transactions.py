import tkinter as tk
import customtkinter as ctk
from gui.models.transaction_model import TransactionModel
from gui.utils.fast_table import make_treeview, populate_tree

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY   = "#0D1B2A"; GOLD = "#E8A020"; BG = "#F0F4F8"; WHITE = "#FFFFFF"
T1     = "#1A1A2E"; T2 = "#6B7280"; GREEN = "#27AE60"; RED = "#E74C3C"
FONT   = "Playfair Display"


class MyTransactionsPage(tk.Frame):
    COLS = ["Date", "Type", "Amount (PKR)", "Account", "Recipient/Sender", "Branch"]

    def __init__(self, master, customer_id, **kw):
        super().__init__(master, bg=BG, **kw)
        self.customer_id = customer_id
        self.txn_m = TransactionModel()
        
        self._build_ui()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=30, pady=(30, 10))
        
        tk.Label(hdr, text="Transaction History", bg=BG, fg=NAVY, 
                 font=(FONT, 18, "bold")).pack(side="left")
        
        btn_f = tk.Frame(hdr, bg=BG)
        btn_f.pack(side="right")
        
        tk.Button(btn_f, text="📥 Export PDF/Statement", command=self._export_statement,
                  bg=GOLD, fg=NAVY, font=(FONT, 10, "bold"),
                  bd=0, padx=12, pady=6, cursor="hand2").pack(side="left", padx=(0, 10))
                  
        tk.Button(btn_f, text="↺ Refresh", command=self.refresh,
                  bg=WHITE, fg=T1, font=(FONT, 10, "bold"),
                  bd=0, padx=12, pady=6, cursor="hand2").pack(side="left")

        # Filters row
        filters = tk.Frame(self, bg=BG)
        filters.pack(fill="x", padx=30, pady=5)
        
        self.search_var = tk.StringVar()
        e = ctk.CTkEntry(filters, placeholder_text="🔍  Search by type or recipient…",
                         textvariable=self.search_var, fg_color=WHITE,
                         border_color=GOLD, border_width=1,
                         text_color=T1, placeholder_text_color="#6B7280",
                         height=36, corner_radius=8)
        e.pack(side="left", fill="x", expand=True)
        e.bind("<KeyRelease>", lambda _: self._do_search())

        # Table Card
        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12)
        card.pack(fill="both", expand=True, padx=30, pady=(10, 20))
        
        self._tv = make_treeview(card, self.COLS)
        self._all_rows = []

    def refresh(self):
        self._all_rows = self.txn_m.get_transactions_by_customer(self.customer_id) or []
        self._do_search()

    def _do_search(self):
        kw = self.search_var.get().strip().lower()
        filtered = [r for r in self._all_rows 
                    if not kw 
                    or kw in str(r.get("TRANSACTION_TYPE", "")).lower()
                    or kw in str(r.get("RECEIVING_ACCOUNT", "")).lower()]
        
        data = []
        for r in filtered:
            ttype = r.get("TRANSACTION_TYPE", "—")
            amt = float(r.get("TRANSACTION_AMOUNT") or 0)
            data.append([
                r.get("TXN_DATE", "—"),
                ttype,
                f"PKR {amt:,.2f}",
                r.get("ACCOUNT_NUMBER", "—"),
                r.get("CUSTOMER_NAME", r.get("RECEIVING_ACCOUNT", "Self")),
                r.get("BRANCH_CODE", "Main")
            ])
            
        self.after(0, lambda: populate_tree(self._tv, data))

    def _export_statement(self):
        from gui.utils.export import export_transactions_html
        if not self._all_rows:
            from tkinter import messagebox
            messagebox.showinfo("No Data", "There are no transactions to export.")
            return
            
        # Get customer info from the first row or assume generic
        acc_num = "All Accounts"
        cust_name = self._all_rows[0].get("CUSTOMER_NAME", "Customer")
        
        # Generate the statement
        export_transactions_html(cust_name, acc_num, self._all_rows)