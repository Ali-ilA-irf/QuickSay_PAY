import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
import threading

NAVY   = "#0D1B2A"; NAVY2  = "#162534"; HOVER  = "#1A2B3C"
GOLD   = "#E8A020"; GOLD_D = "#C8881A"
BG     = "#F0F4F8"; WHITE  = "#FFFFFF"; BORDER = "#E2E8F0"
T1     = "#1A1A2E"; T2     = "#6B7280"
GREEN  = "#27AE60"; RED    = "#E74C3C"
FONT   = "Segoe UI"


class TellerDashboard(tk.Frame):
    SIDEBAR_W = 220

    def __init__(self, master, user_data, logout_cb, **kw):
        super().__init__(master, bg=BG, **kw)
        self.user_data   = user_data
        self.logout_cb   = logout_cb
        self.branch_code = user_data.get("BRANCH_CODE", "")
        self._active     = "Dashboard"
        self._nav_items  = {}
        self._pages      = {}

        self._build_layout()
        self._build_all_pages()
        self._switch("Dashboard")
        self._animate_sidebar_in()

    def _build_layout(self):
        # Sidebar
        self.sidebar = tk.Frame(self, bg=NAVY, width=1)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        hdr = tk.Frame(self.sidebar, bg=NAVY, height=80)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        av = tk.Canvas(hdr, width=44, height=44, bg=NAVY, highlightthickness=0)
        av.place(x=20, rely=0.5, anchor="w")
        av.create_oval(2, 2, 42, 42, fill=GOLD, outline="")
        av.create_text(22, 22, text=self.user_data.get("USERNAME", "T")[:2].upper(), fill=NAVY, font=(FONT, 14, "bold"))
        tk.Label(hdr, text=self.user_data.get("USERNAME", "Teller"), bg=NAVY, fg=WHITE, font=(FONT, 13, "bold")).place(x=76, y=20)
        tk.Label(hdr, text="Branch Teller", bg=NAVY, fg=GREEN, font=(FONT, 10)).place(x=76, y=42)

        self.nav_cont = tk.Frame(self.sidebar, bg=NAVY)
        self.nav_cont.pack(fill="both", expand=True, pady=20)

        for name, icon in [
            ("Dashboard", "📊"),
            ("New Customer", "👤"),
            ("Open Account", "🏦"),
            ("Txn: Cash", "💵"),
            ("Txn: Transfer", "🔄")
        ]:
            self._add_nav_item(name, icon)

        bot = tk.Frame(self.sidebar, bg=NAVY)
        bot.pack(fill="x", side="bottom", pady=20)
        tk.Button(bot, text="⎋ Logout", bg=NAVY, fg=RED, bd=0, font=(FONT, 11), activebackground=NAVY, activeforeground=WHITE, cursor="hand2", command=self.logout_cb).pack(anchor="w", padx=24, pady=4)

        # Content
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        bar = tk.Frame(self.content, bg=WHITE, height=64)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Frame(bar, bg=BORDER, height=1).pack(side="bottom", fill="x")
        self._title_lbl = tk.Label(bar, text="Dashboard", bg=WHITE, fg=T1, font=(FONT, 17, "bold"))
        self._title_lbl.pack(side="left", padx=22)

        self.pg_container = tk.Frame(self.content, bg=BG)
        self.pg_container.pack(fill="both", expand=True)

    def _add_nav_item(self, name, icon):
        row = tk.Frame(self.nav_cont, bg=NAVY, height=44)
        row.pack(fill="x", pady=2); row.pack_propagate(False)
        stripe = tk.Frame(row, bg=GOLD, width=4)
        lbl = tk.Label(row, text=f"{icon}   {name}", bg=NAVY, fg=WHITE, font=(FONT, 12))
        lbl.pack(side="left", padx=20)
        
        for w in (row, lbl):
            w.bind("<Enter>", lambda e: self._hover_on(name))
            w.bind("<Leave>", lambda e: self._hover_off(name))
            w.bind("<Button-1>", lambda e: self._switch(name))
            
        self._nav_items[name] = (row, stripe, lbl)

    def _hover_on(self, name):
        if self._active != name:
            r, _, l = self._nav_items[name]
            r.config(bg=HOVER); l.config(bg=HOVER)

    def _hover_off(self, name):
        if self._active != name:
            r, _, l = self._nav_items[name]
            r.config(bg=NAVY); l.config(bg=NAVY)

    def _animate_sidebar_in(self, w=1):
        if w < self.SIDEBAR_W:
            nw = min(w + 24, self.SIDEBAR_W)
            self.sidebar.configure(width=nw)
            self.after(8, lambda: self._animate_sidebar_in(nw))

    def _switch(self, name):
        if self._active in self._nav_items:
            row, stripe, lbl = self._nav_items[self._active]
            stripe.pack_forget()
            row.config(bg=NAVY); lbl.config(bg=NAVY, fg=WHITE)
        self._active = name
        if name in self._nav_items:
            row, stripe, lbl = self._nav_items[name]
            stripe.pack(side="left", fill="y")
            row.config(bg=NAVY2); lbl.config(bg=NAVY2, fg=GOLD)
        self._title_lbl.config(text=name)

        for pname, pg in self._pages.items():
            if pname == name:
                pg.pack(fill="both", expand=True)
                if hasattr(pg, "refresh"):
                    # Run refresh on main thread to avoid GUI/Matplotlib calls in background threads
                    self.after(0, pg.refresh)
            else:
                pg.pack_forget()

    def _build_all_pages(self):
        from gui.views.teller.new_customer import NewCustomerPage
        from gui.views.teller.new_account import NewAccountPage
        from gui.views.teller.deposit_withdraw import CashTxnPage
        from gui.views.teller.fund_transfer import TransferPage

        self._pages["Dashboard"] = self._make_home()
        self._pages["New Customer"] = NewCustomerPage(self.pg_container, self.user_data)
        self._pages["Open Account"] = NewAccountPage(self.pg_container, self.branch_code, self.user_data)
        self._pages["Txn: Cash"]    = CashTxnPage(self.pg_container, self.branch_code, self.user_data)
        self._pages["Txn: Transfer"] = TransferPage(self.pg_container, self.branch_code, self.user_data)

    def _make_home(self):
        from gui.models.transaction_model import TransactionModel
        from gui.utils.fast_table import make_treeview, populate_tree

        pg = tk.Frame(self.pg_container, bg=BG)

        # Transaction model for teller KPIs
        self.txn_m = TransactionModel()
        emp_id = int(self.user_data.get("EMPLOYEE_ID") or 0)

        # KPI row
        row = tk.Frame(pg, bg=BG)
        row.pack(fill="x", padx=24, pady=(24, 12))

        c1 = ctk.CTkFrame(row, fg_color=WHITE, corner_radius=12, height=120)
        c1.pack(side="left", fill="x", expand=True, padx=6)
        c1.pack_propagate(False)
        tk.Label(c1, text="Today's Transactions", bg=WHITE, fg=T2, font=(FONT, 12)).pack(anchor="w", padx=20, pady=(16,4))
        self._teller_txn_count = tk.Label(c1, text="0", bg=WHITE, fg=NAVY, font=(FONT, 28, "bold"))
        self._teller_txn_count.pack(anchor="w", padx=20)

        c2 = ctk.CTkFrame(row, fg_color=WHITE, corner_radius=12, height=120)
        c2.pack(side="left", fill="x", expand=True, padx=6)
        c2.pack_propagate(False)
        tk.Label(c2, text="Total Cash Processed", bg=WHITE, fg=T2, font=(FONT, 12)).pack(anchor="w", padx=20, pady=(16,4))
        self._teller_total_cash = tk.Label(c2, text="PKR 0.00", bg=WHITE, fg=GREEN, font=(FONT, 20, "bold"))
        self._teller_total_cash.pack(anchor="w", padx=20)

        # Recent activity
        recent_frame = ctk.CTkFrame(pg, fg_color=WHITE, corner_radius=12)
        recent_frame.pack(fill="both", expand=True, padx=24, pady=(12,24))
        tk.Label(recent_frame, text="Recent Activity (Last 10)", bg=WHITE, fg=T1, font=(FONT, 12, "bold")).pack(anchor="w", padx=16, pady=(12,4))

        self._recent_tv = make_treeview(recent_frame, ["Time", "Action"])

        def refresh_home():
            try:
                stats = self.txn_m.get_teller_daily_stats(emp_id) or {}
                vol = stats.get("volume", 0)
                total_cash = stats.get("total_cash", 0.0)
                self._teller_txn_count.config(text=str(vol))
                self._teller_total_cash.config(text=f"PKR {float(total_cash):,.2f}")

                rows = self.txn_m.get_teller_recent_activity(emp_id, 10) or []
                populate_tree(self._recent_tv, [[r.get("ACTION_TIME", ""), r.get("DESCRIPTION", "")]
                                                for r in rows])
            except Exception as ex:
                print("Teller home refresh error:", ex)

        # attach refresh so _switch can call it
        pg.refresh = refresh_home

        # initial load and periodic updates
        refresh_home()

        def _poll():
            if not pg.winfo_exists():
                return
            try:
                refresh_home()
            finally:
                pg.after(5000, _poll)

        pg.after(5000, _poll)

        return pg
