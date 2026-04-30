import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
import threading
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from datetime import datetime
import calendar

from gui.models.employee_model import EmployeeModel
from gui.models.audit_model import AuditModel
from gui.models.account_model import AccountModel
from gui.models.loan_model import LoanModel
from gui.models.branch_model import BranchModel
from gui.models.transaction_model import TransactionModel
from gui.utils.fast_table import make_treeview, populate_tree

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY   = "#0D1B2A"
NAVY2  = "#162534"
HOVER  = "#1A2B3C"
GOLD   = "#E8A020"
GOLD_D = "#C8881A"
BG     = "#F0F4F8"
WHITE  = "#FFFFFF"
BORDER = "#E2E8F0"
T1     = "#1A1A2E"
T2     = "#6B7280"
GREEN  = "#27AE60"
RED    = "#E74C3C"
FONT   = "Playfair Display"


def _card(parent, pad_x=16, pad_y=12, radius=12, height=None):
    """White rounded card."""
    f = ctk.CTkFrame(parent, fg_color=WHITE, corner_radius=radius)
    if height:
        f.configure(height=height)
    return f


class AdminDashboard(tk.Frame):
    SIDEBAR_W = 220

    def __init__(self, master, user_data, logout_cb, **kw):
        super().__init__(master, bg=BG, **kw)
        self.user_data  = user_data
        self.logout_cb  = logout_cb
        self._active    = "Dashboard"
        self._nav_items = {}   # name → (row_frame, stripe, lbl)
        self._pages     = {}   # name → frame
        self._kpi_vals  = {}   # key → label widget
        self._all_emps  = []

        self.emp_m    = EmployeeModel()
        self.audit_m  = AuditModel()
        self.account_m = AccountModel()
        self.loan_m   = LoanModel()
        self.branch_m = BranchModel()
        self.txn_m    = TransactionModel()

        self._build_sidebar()
        self._build_content()
        self._build_all_pages()
        self._switch("Dashboard")
        self.after(60, self._animate_sidebar)

    # ══════════════════════════ SIDEBAR ═══════════════════════════════════════
    def _build_sidebar(self):
        self.sidebar = tk.Frame(self, bg=NAVY, width=1)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Brand Area
        brand = tk.Frame(self.sidebar, bg=NAVY, height=80)
        brand.pack(fill="x", pady=(20, 0))
        tk.Label(brand, text="QuickSay Pay", bg=NAVY, fg=GOLD, font=(FONT, 18, "bold")).pack()
        tk.Label(brand, text="Apke Dill Mein Hmara Account", bg=NAVY, fg=T2, font=(FONT, 8, "italic")).pack()

        # ── Profile
        pf = tk.Frame(self.sidebar, bg=NAVY)
        pf.pack(fill="x", pady=(10, 8))
        av = tk.Canvas(pf, width=64, height=64, bg=NAVY, highlightthickness=0)
        av.pack()
        av.create_oval(4, 4, 60, 60, fill=GOLD, outline="")
        init = self.user_data.get("USERNAME", "A")[:2].upper()
        av.create_text(32, 32, text=init, fill=NAVY,
                       font=(FONT, 18, "bold"))
        tk.Label(pf, text=self.user_data.get("USERNAME", "Admin").title(),
                 bg=NAVY, fg=WHITE, font=(FONT, 13, "bold")).pack(pady=(6, 2))
        tk.Label(pf, text="Administrator",
                 bg=NAVY, fg=GOLD, font=(FONT, 10)).pack()

        tk.Frame(self.sidebar, bg=HOVER, height=1).pack(fill="x", pady=8)

        # ── Nav
        nav_items = [
            ("Dashboard",  "⊞"),
            ("Employees",  "👥"),
            ("Branches",   "🏢"),
            ("Customers",  "👤"),
            ("Accounts",   "🏦"),
            ("Audit Logs", "📋"),
            ("Reports",    "📊"),
            ("Settings",   "⚙"),
        ]
        for name, icon in nav_items:
            self._make_nav_item(name, icon)

        # ── Logout
        tk.Frame(self.sidebar, bg=HOVER, height=1).pack(fill="x", pady=8, side="bottom")
        lo = tk.Label(self.sidebar, text="⎋  Logout", bg=NAVY, fg=RED,
                      font=(FONT, 12), cursor="hand2", pady=12, anchor="w", padx=18)
        lo.pack(fill="x", side="bottom")
        lo.bind("<Button-1>", lambda _: self.logout_cb())
        lo.bind("<Enter>", lambda _: lo.config(bg="#1A0808"))
        lo.bind("<Leave>", lambda _: lo.config(bg=NAVY))

    def _make_nav_item(self, name, icon):
        row = tk.Frame(self.sidebar, bg=NAVY)
        row.pack(fill="x")
        stripe = tk.Frame(row, width=3, bg=GOLD)   # hidden by default
        lbl = tk.Label(row, text=f"  {icon}  {name}", bg=NAVY, fg=WHITE,
                       font=(FONT, 12), anchor="w", pady=11, padx=8,
                       cursor="hand2")
        lbl.pack(side="left", fill="x", expand=True)

        def enter(_):
            if name != self._active:
                row.config(bg=HOVER); lbl.config(bg=HOVER)
        def leave(_):
            if name != self._active:
                row.config(bg=NAVY); lbl.config(bg=NAVY)
        def click(_): self._switch(name)

        lbl.bind("<Enter>", enter)
        lbl.bind("<Leave>", leave)
        lbl.bind("<Button-1>", click)
        row.bind("<Button-1>", click)
        self._nav_items[name] = (row, stripe, lbl)

    def _animate_sidebar(self, w=1):
        target = self.SIDEBAR_W
        if w < target:
            nw = min(w + 22, target)
            self.sidebar.configure(width=nw)
            self.after(8, lambda: self._animate_sidebar(nw))

    # ══════════════════════════ CONTENT ═══════════════════════════════════════
    def _build_content(self):
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        # Top bar
        bar = tk.Frame(self.content, bg=WHITE, height=54)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        self._title_lbl = tk.Label(bar, text="Dashboard", bg=WHITE, fg=T1,
                                   font=(FONT, 17, "bold"))
        self._title_lbl.pack(side="left", padx=22)
        # Notification + user chip
        r = tk.Frame(bar, bg=WHITE)
        r.pack(side="right", padx=14)
        tk.Label(r, text="🔔", bg=WHITE, font=(FONT, 15)).pack(side="right", padx=6)
        av2 = tk.Canvas(r, width=32, height=32, bg=WHITE, highlightthickness=0)
        av2.pack(side="right")
        av2.create_oval(2, 2, 30, 30, fill=GOLD, outline="")
        av2.create_text(16, 16, text=self.user_data.get("DISPLAY_NAME","A")[:1].upper(),
                        fill=NAVY, font=(FONT, 11, "bold"))

        # Pages container
        self.pg_container = tk.Frame(self.content, bg=BG)
        self.pg_container.pack(fill="both", expand=True)

    # ══════════════════════════ PAGE SWITCHING ════════════════════════════════
    def _switch(self, name):
        # Deactivate old
        if self._active in self._nav_items:
            row, stripe, lbl = self._nav_items[self._active]
            stripe.pack_forget()
            row.config(bg=NAVY); lbl.config(bg=NAVY, fg=WHITE)
        # Activate new
        self._active = name
        if name in self._nav_items:
            row, stripe, lbl = self._nav_items[name]
            stripe.pack(side="left", fill="y")
            row.config(bg=NAVY2); lbl.config(bg=NAVY2, fg=GOLD)
        self._title_lbl.config(text=name)

        # Show/hide pages
        for pname, pg in self._pages.items():
            if pname == name:
                pg.pack(fill="both", expand=True)
                if hasattr(pg, "refresh"):
                    self.after(0, pg.refresh)
                if pname == "Dashboard":
                    self.after(0, self._refresh_dashboard)
            else:
                pg.pack_forget()

    def refresh_all(self):
        """Triggers a refresh on all cached pages that have a refresh() method."""
        for name, pg in self._pages.items():
            if hasattr(pg, "refresh"):
                self.after(0, pg.refresh)
        # Always refresh the admin dashboard stats/charts
        self.after(0, self._refresh_dashboard)

    # ══════════════════════════ ALL PAGES ════════════════════════════════════
    def _build_all_pages(self):
        from gui.views.admin.manage_employees import ManageEmployeesPage
        from gui.views.admin.manage_branches  import ManageBranchesPage
        from gui.views.admin.manage_customers import ManageCustomersPage
        from gui.views.admin.manage_accounts  import ManageAccountsPage
        from gui.views.admin.system_reports   import SystemReportsPage
        from gui.views.admin.audit_logs       import AuditLogsView

        self._pages["Dashboard"]  = self._make_dashboard_page()
        self._pages["Employees"]  = ManageEmployeesPage(self.pg_container)
        self._pages["Branches"]   = ManageBranchesPage(self.pg_container)
        self._pages["Customers"]  = ManageCustomersPage(self.pg_container)
        self._pages["Accounts"]   = ManageAccountsPage(self.pg_container)
        self._pages["Audit Logs"] = AuditLogsView(self.pg_container)
        self._pages["Reports"]    = SystemReportsPage(self.pg_container)
        self._pages["Settings"]   = self._make_placeholder("Settings")

    # ─────────────────────────── DASHBOARD PAGE ───────────────────────────────
    def _make_dashboard_page(self):
        pg = tk.Frame(self.pg_container, bg=BG)
        # Scrollable
        cv = tk.Canvas(pg, bg=BG, highlightthickness=0)
        sb = ttk.Scrollbar(pg, orient="vertical", command=cv.yview)
        cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        cv.pack(side="left", fill="both", expand=True)
        inner = tk.Frame(cv, bg=BG)
        win = cv.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: (
            cv.configure(scrollregion=cv.bbox("all")),
            cv.itemconfig(win, width=cv.winfo_width()),
        ))
        cv.bind("<Configure>", lambda e: cv.itemconfig(win, width=e.width))

        # ── KPI Row
        kpi_row = tk.Frame(inner, bg=BG)
        kpi_row.pack(fill="x", padx=20, pady=(20, 12))
        kpi_defs = [
            ("employees", "Total Employees", "👥", True),
            ("branches",  "Total Branches",  "🏢", False),
            ("balance",   "Total Balance",   "💰", False),
            ("loans",     "Pending Loans",   "📋", False),
        ]
        for i, (key, label, icon, navy) in enumerate(kpi_defs):
            c = self._make_kpi_card(kpi_row, key, label, icon, navy)
            c.grid(row=0, column=i, padx=8, sticky="nsew")
            kpi_row.columnconfigure(i, weight=1)

        # ── Charts row 1
        r1 = tk.Frame(inner, bg=BG)
        r1.pack(fill="x", padx=20, pady=(0, 12))
        r1.columnconfigure(0, weight=65)
        r1.columnconfigure(1, weight=35)
        bar_card  = _card(r1, height=290); bar_card.grid(row=0, column=0, padx=(0,8), sticky="nsew")
        donut_card = _card(r1, height=290); donut_card.grid(row=0, column=1, padx=(8,0), sticky="nsew")
        self._bar_host   = bar_card
        self._donut_host = donut_card

        # ── Charts row 2
        r2 = tk.Frame(inner, bg=BG)
        r2.pack(fill="x", padx=20, pady=(0, 20))
        r2.columnconfigure(0, weight=65)
        r2.columnconfigure(1, weight=35)
        area_card    = _card(r2, height=240); area_card.grid(row=0, column=0, padx=(0,8), sticky="nsew")
        summary_card = _card(r2, height=240); summary_card.grid(row=0, column=1, padx=(8,0), sticky="nsew")
        self._area_host    = area_card
        self._summary_host = summary_card

        return pg

    def _make_kpi_card(self, parent, key, label, icon, navy=False):
        bg_c = NAVY if navy else WHITE
        fg_c = WHITE if navy else T1
        ic_c = WHITE if navy else GOLD
        card = ctk.CTkFrame(parent, fg_color=bg_c, corner_radius=12, height=110)
        card.pack_propagate(False)
        top = tk.Frame(card, bg=bg_c)
        top.pack(fill="x", padx=14, pady=(14, 0))
        tk.Label(top, text=label, bg=bg_c, fg=fg_c if navy else T2,
                 font=(FONT, 11)).pack(side="left")
        tk.Label(top, text=icon, bg=bg_c, fg=ic_c,
                 font=(FONT, 14)).pack(side="right")
        val = tk.Label(card, text="—", bg=bg_c, fg=GOLD if navy else T1,
                       font=(FONT, 28, "bold"))
        val.pack(anchor="w", padx=14, pady=(4, 10))
        self._kpi_vals[key] = val
        return card

    # ─────────────────────────── REFRESH DASHBOARD ────────────────────────────
    def _refresh_dashboard(self):
        stats = self.emp_m.get_total_counts()
        bal   = self.account_m.get_total_balance()
        loans = self.loan_m.get_pending_count()
        self.after(0, lambda: self._set_kpi("employees", stats.get("EMPLOYEES", 0)))
        self.after(0, lambda: self._set_kpi("branches",  stats.get("BRANCHES",  0)))
        self.after(0, lambda: self._set_kpi("balance",   f"PKR {bal:,.0f}"))
        self.after(0, lambda: self._set_kpi("loans",     loans))
        self.after(0, self._draw_bar_chart)
        self.after(0, self._draw_donut_chart)
        self.after(0, self._draw_area_chart)
        self.after(0, self._draw_summary)

    def _set_kpi(self, key, val):
        if key in self._kpi_vals and self._kpi_vals[key].winfo_exists():
            self._kpi_vals[key].config(text=str(val))

    def _draw_bar_chart(self):
        """Real data: transaction counts per month from Oracle TRANSACTION table."""
        for w in self._bar_host.winfo_children(): w.destroy()
        rows = self.txn_m.get_monthly_counts()

        if rows:
            months  = [r.get("MONTH_LABEL", "")  for r in rows]
            deps    = [float(r.get("DEPOSIT_COUNT") or 0)    for r in rows]
            wds     = [float(r.get("WITHDRAWAL_COUNT") or 0) for r in rows]
        else:
            # No transactions yet — show empty months with 0
            months = ["No Data"]; deps = [0]; wds = [0]

        x = np.arange(len(months))
        fig, ax = plt.subplots(figsize=(5.5, 2.6))
        fig.patch.set_facecolor(WHITE); ax.set_facecolor(WHITE)
        ax.bar(x - 0.18, deps, 0.32, color=NAVY,  label="Deposits")
        ax.bar(x + 0.18, wds,  0.32, color=GOLD,  label="Withdrawals")
        ax.set_xticks(x); ax.set_xticklabels(months, fontsize=8, rotation=15)
        ax.tick_params(colors=T2, labelsize=8)
        ax.spines[["top","right","left"]].set_visible(False)
        ax.set_ylabel("Count", fontsize=8, color=T2)
        ax.legend(fontsize=8, framealpha=0)
        tk.Label(self._bar_host, text="Monthly Transactions (Real Data)",
                 bg=WHITE, fg=T1, font=(FONT, 11, "bold")).pack(anchor="w", padx=4)
        cv = FigureCanvasTkAgg(fig, master=self._bar_host)
        cv.draw(); cv.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def _draw_donut_chart(self):
        """Real data: account count per branch from Oracle ACCOUNT table."""
        for w in self._donut_host.winfo_children(): w.destroy()
        rows = self.account_m.get_count_per_branch()

        if rows:
            labels = [r.get("BRANCH_CODE", "") for r in rows]
            vals   = [max(float(r.get("ACCOUNT_COUNT") or 0), 0.001) for r in rows]
            total  = int(sum(r.get("ACCOUNT_COUNT", 0) for r in rows))
        else:
            labels = ["No Accounts"]; vals = [1]; total = 0

        fig, ax = plt.subplots(figsize=(2.5, 2.5))
        fig.patch.set_facecolor(WHITE)
        palette = [NAVY, GOLD, "#1E3A5F", "#C8881A", "#2D4A6E", "#5B8DB8"]
        ax.pie(vals,
               labels=labels,
               colors=palette[:len(vals)],
               wedgeprops=dict(width=0.52),
               startangle=90,
               textprops={"fontsize": 7, "color": T2})
        ax.text(0, 0, f"{total}\nAccounts", ha="center", va="center",
                fontsize=9, fontweight="bold", color=T1)
        tk.Label(self._donut_host, text="Accounts per Branch (Real Data)",
                 bg=WHITE, fg=T1, font=(FONT, 11, "bold")).pack(anchor="w", padx=4)
        cv = FigureCanvasTkAgg(fig, master=self._donut_host)
        cv.draw(); cv.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def _draw_area_chart(self):
        """Real data: daily deposit vs withdrawal totals from Oracle TRANSACTION table."""
        for w in self._area_host.winfo_children(): w.destroy()
        rows = self.txn_m.get_daily_totals(days=30)

        if rows:
            labels = [r.get("TXN_DAY", "")          for r in rows]
            deps   = [float(r.get("DEPOSITS") or 0)    for r in rows]
            wds    = [float(r.get("WITHDRAWALS") or 0) for r in rows]
        else:
            labels = ["No Data"]; deps = [0]; wds = [0]

        x = np.arange(len(labels))
        fig, ax = plt.subplots(figsize=(5.2, 2.2))
        fig.patch.set_facecolor(WHITE); ax.set_facecolor(WHITE)
        ax.fill_between(x, deps, alpha=0.30, color=GOLD)
        ax.fill_between(x, wds,  alpha=0.30, color=NAVY)
        ax.plot(x, deps, color=GOLD, linewidth=1.8, label="Deposits (PKR)")
        ax.plot(x, wds,  color=NAVY, linewidth=1.8, label="Withdrawals (PKR)")
        if labels:
            step = max(1, len(labels) // 6)
            ax.set_xticks(x[::step])
            ax.set_xticklabels(labels[::step], fontsize=7, rotation=15)
        ax.spines[["top","right","left","bottom"]].set_visible(False)
        ax.tick_params(colors=T2, labelsize=7)
        ax.legend(fontsize=8, framealpha=0, loc="upper left")
        tk.Label(self._area_host, text="Daily Transaction Trend — Last 30 Days (Real Data)",
                 bg=WHITE, fg=T1, font=(FONT, 11, "bold")).pack(anchor="w", padx=4)
        cv = FigureCanvasTkAgg(fig, master=self._area_host)
        cv.draw(); cv.get_tk_widget().pack(fill="both", expand=True)
        plt.close(fig)

    def _draw_summary(self):
        for w in self._summary_host.winfo_children(): w.destroy()
        tk.Label(self._summary_host, text="Quick Summary",
                 bg=WHITE, fg=T1, font=(FONT, 11, "bold")).pack(anchor="w", padx=4, pady=(4,8))
        items = [
            ("Active Accounts", "🏦"),
            ("Cards Issued",    "💳"),
            ("Loans Approved",  "✅"),
            ("Loans Pending",   "⏳"),
        ]
        for label, icon in items:
            row = tk.Frame(self._summary_host, bg=WHITE)
            row.pack(fill="x", padx=4, pady=4)
            tk.Label(row, text=icon, bg=WHITE, font=(FONT, 13)).pack(side="left", padx=(0,8))
            tk.Label(row, text=label, bg=WHITE, fg=T1, font=(FONT, 11)).pack(side="left")
            tk.Label(row, text="—", bg=WHITE, fg=GOLD,
                     font=(FONT, 11, "bold")).pack(side="right")
        tk.Button(self._summary_host, text="View Reports →",
                  bg=GOLD, fg=WHITE, font=(FONT, 11, "bold"),
                  bd=0, padx=12, pady=6, cursor="hand2",
                  activebackground=GOLD_D,
                  command=lambda: self._switch("Reports")).pack(
            fill="x", padx=4, pady=(12, 4))




    # ─────────────────────────── PLACEHOLDER ──────────────────────────────────
    def _make_placeholder(self, name):
        pg = tk.Frame(self.pg_container, bg=BG)
        tk.Label(pg, text=f"{name}\n\nComing in the next phase.",
                 bg=BG, fg=T2, font=(FONT, 18)).pack(expand=True)
        return pg
