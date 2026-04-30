import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
import threading
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
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


class ManagerDashboard(tk.Frame):
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

    # ══════════════════════════ UI SHELL ════════════════════════════════════
    def _build_layout(self):
        # Sidebar
        self.sidebar = tk.Frame(self, bg=NAVY, width=1)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Brand Area
        brand = tk.Frame(self.sidebar, bg=NAVY, height=80)
        brand.pack(fill="x", pady=(20, 0))
        tk.Label(brand, text="QuickSay Pay", bg=NAVY, fg=GOLD, font=(FONT, 18, "bold")).pack()
        tk.Label(brand, text="Apke Dill Mein Hmara Account", bg=NAVY, fg=T2, font=(FONT, 8, "italic")).pack()

        hdr = tk.Frame(self.sidebar, bg=NAVY, height=80)
        hdr.pack(fill="x", pady=(10, 0))
        hdr.pack_propagate(False)
        av = tk.Canvas(hdr, width=44, height=44, bg=NAVY, highlightthickness=0)
        av.place(x=20, rely=0.5, anchor="w")
        av.create_oval(2, 2, 42, 42, fill=GOLD, outline="")
        av.create_text(22, 22, text=self.user_data.get("USERNAME", "M")[:2].upper(),
                       fill=NAVY, font=(FONT, 14, "bold"))
        tk.Label(hdr, text=self.user_data.get("USERNAME", "Manager"),
                 bg=NAVY, fg=WHITE, font=(FONT, 13, "bold")).place(x=76, y=20)
        tk.Label(hdr, text="Branch Manager",
                 bg=NAVY, fg=GOLD, font=(FONT, 10)).place(x=76, y=42)

        self.nav_cont = tk.Frame(self.sidebar, bg=NAVY)
        self.nav_cont.pack(fill="both", expand=True, pady=20)

        for name, icon in [
            ("Dashboard", "📊"),
            ("Loan Approvals", "💰"),
            ("View Accounts", "🏦"),
            ("Branch Reports", "📈")
        ]:
            self._add_nav_item(name, icon)

        bot = tk.Frame(self.sidebar, bg=NAVY)
        bot.pack(fill="x", side="bottom", pady=20)
        tk.Button(bot, text="⚙ Settings", bg=NAVY, fg=T2, bd=0,
                  font=(FONT, 11), activebackground=NAVY, activeforeground=WHITE,
                  cursor="hand2").pack(anchor="w", padx=24, pady=4)
        tk.Button(bot, text="⎋ Logout", bg=NAVY, fg=RED, bd=0,
                  font=(FONT, 11), activebackground=NAVY, activeforeground=WHITE,
                  cursor="hand2", command=self.logout_cb).pack(anchor="w", padx=24, pady=4)

        # Content
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        bar = tk.Frame(self.content, bg=WHITE, height=64)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Frame(bar, bg=BORDER, height=1).pack(side="bottom", fill="x")
        self._title_lbl = tk.Label(bar, text="Dashboard", bg=WHITE, fg=T1, font=(FONT, 17, "bold"))
        self._title_lbl.pack(side="left", padx=22)

        r = tk.Frame(bar, bg=WHITE)
        r.pack(side="right", padx=14)
        tk.Label(r, text="🔔", bg=WHITE, font=(FONT, 15)).pack(side="right", padx=6)
        av2 = tk.Canvas(r, width=32, height=32, bg=WHITE, highlightthickness=0)
        av2.pack(side="right")
        av2.create_oval(2, 2, 30, 30, fill=GOLD, outline="")
        av2.create_text(16, 16, text=self.user_data.get("USERNAME", "M")[:1].upper(),
                        fill=NAVY, font=(FONT, 11, "bold"))

        self.pg_container = tk.Frame(self.content, bg=BG)
        self.pg_container.pack(fill="both", expand=True)

    def _add_nav_item(self, name, icon):
        row = tk.Frame(self.nav_cont, bg=NAVY, height=44)
        row.pack(fill="x", pady=2)
        row.pack_propagate(False)
        stripe = tk.Frame(row, bg=GOLD, width=4)
        lbl = tk.Label(row, text=f"{icon}   {name}", bg=NAVY, fg=WHITE, font=(FONT, 12))
        lbl.pack(side="left", padx=20)
        row.bind("<Enter>", lambda e: self._hover_on(name))
        row.bind("<Leave>", lambda e: self._hover_off(name))
        lbl.bind("<Enter>", lambda e: self._hover_on(name))
        lbl.bind("<Leave>", lambda e: self._hover_off(name))
        row.bind("<Button-1>", lambda e: self._switch(name))
        lbl.bind("<Button-1>", lambda e: self._switch(name))
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
                    # Schedule refresh on main thread to avoid GUI work in background threads
                    self.after(0, pg.refresh)
            else:
                pg.pack_forget()

    def refresh_all(self):
        """Triggers a refresh on all cached pages that have a refresh() method."""
        for name, pg in self._pages.items():
            if hasattr(pg, "refresh"):
                self.after(0, pg.refresh)

    # ══════════════════════════ PAGES ════════════════════════════════════
    def _build_all_pages(self):
        from gui.views.manager.loan_approval import LoanApprovalPage
        from gui.views.manager.view_accounts import ViewAccountsPage
        from gui.views.manager.branch_reports import BranchReportsPage

        self._pages["Dashboard"]      = self._make_home()
        self._pages["Loan Approvals"] = LoanApprovalPage(self.pg_container, self.branch_code, self.user_data)
        self._pages["View Accounts"]  = ViewAccountsPage(self.pg_container, self.branch_code)
        self._pages["Branch Reports"] = BranchReportsPage(self.pg_container, self.branch_code)

    def _make_home(self):
        pg = tk.Frame(self.pg_container, bg=BG)
        
        # Welcome Header
        tk.Label(pg, text=f"Welcome back, {self.user_data.get('DISPLAY_NAME', 'Manager')}!", 
                 bg=BG, fg=NAVY, font=(FONT, 22, "bold")).pack(anchor="w", padx=30, pady=(30, 5))
        tk.Label(pg, text=f"Branch: {self.branch_code}", 
                 bg=BG, fg=T2, font=(FONT, 14)).pack(anchor="w", padx=30, pady=(0, 30))

        # Stats container
        stats_frame = tk.Frame(pg, bg=BG)
        stats_frame.pack(fill="x", padx=24)

        from gui.db_connection import DatabaseConnection
        db = DatabaseConnection()
        try:
            rows = db.execute_query("SELECT * FROM vw_branch_summary WHERE branch_code = :1", (self.branch_code,))
            b_data = rows[0] if rows else {}
            
            emps = b_data.get("TOTAL_EMPLOYEES", 0)
            accs = b_data.get("TOTAL_ACCOUNTS", 0)
            bal = float(b_data.get("TOTAL_DEPOSITS", 0) or 0)
        except Exception:
            emps = accs = bal = 0

        # Card 1: Employees
        c1 = ctk.CTkFrame(stats_frame, fg_color=WHITE, corner_radius=12, height=120)
        c1.pack(side="left", fill="x", expand=True, padx=6)
        c1.pack_propagate(False)
        tk.Label(c1, text="👥  Branch Employees", bg=WHITE, fg=T2, font=(FONT, 12)).pack(anchor="w", padx=20, pady=(20, 5))
        tk.Label(c1, text=str(emps), bg=WHITE, fg=NAVY, font=(FONT, 28, "bold")).pack(anchor="w", padx=20)

        # Card 2: Accounts
        c2 = ctk.CTkFrame(stats_frame, fg_color=WHITE, corner_radius=12, height=120)
        c2.pack(side="left", fill="x", expand=True, padx=6)
        c2.pack_propagate(False)
        tk.Label(c2, text="🏦  Active Accounts", bg=WHITE, fg=T2, font=(FONT, 12)).pack(anchor="w", padx=20, pady=(20, 5))
        tk.Label(c2, text=str(accs), bg=WHITE, fg=GREEN, font=(FONT, 28, "bold")).pack(anchor="w", padx=20)

        # Card 3: Total Balance
        c3 = ctk.CTkFrame(stats_frame, fg_color=WHITE, corner_radius=12, height=120)
        c3.pack(side="left", fill="x", expand=True, padx=6)
        c3.pack_propagate(False)
        tk.Label(c3, text="💰  Total Balance", bg=WHITE, fg=T2, font=(FONT, 12)).pack(anchor="w", padx=20, pady=(20, 5))
        tk.Label(c3, text=f"PKR {bal:,.0f}", bg=WHITE, fg=GOLD, font=(FONT, 28, "bold")).pack(anchor="w", padx=20)

        # Charts container
        chart_frame = tk.Frame(pg, bg=BG)
        chart_frame.pack(fill="both", expand=True, padx=24, pady=24)
        
        self.pie_host = ctk.CTkFrame(chart_frame, fg_color=WHITE, corner_radius=12)
        self.pie_host.pack(side="left", fill="both", expand=True, padx=6)
        self.pie_host.pack_propagate(False)

        self.bar_host = ctk.CTkFrame(chart_frame, fg_color=WHITE, corner_radius=12)
        self.bar_host.pack(side="left", fill="both", expand=True, padx=6)
        self.bar_host.pack_propagate(False)

        # Draw charts in background
        threading.Thread(target=self._draw_loan_pie, daemon=True).start()
        threading.Thread(target=self._draw_txn_bar, daemon=True).start()

        return pg

    def _draw_loan_pie(self):
        from gui.db_connection import DatabaseConnection
        db = DatabaseConnection()
        q = """SELECT approval_status, COUNT(*) as cnt FROM LOAN 
               WHERE ref_account_id IN (SELECT account_id FROM ACCOUNT WHERE ref_branch_code = :1)
               GROUP BY approval_status"""
        rows = db.execute_query(q, (self.branch_code,)) or []
        
        def _render():
            # Clear old children
            for w in self.pie_host.winfo_children(): w.destroy()
            
            labels = [r.get("APPROVAL_STATUS","") for r in rows]
            vals   = [float(r.get("CNT") or 0) for r in rows]
            if not vals:
                labels = ["No Loans"]; vals = [1]
                
            colors = { "APPROVED": NAVY, "PENDING": GOLD, "REJECTED": "#E74C3C", "No Loans": "#D1D9E6" }
            clr = [colors.get(l, "#888888") for l in labels]
            
            # Create figure in MAIN thread
            fig, ax = plt.subplots(figsize=(3, 3))
            fig.patch.set_facecolor(WHITE)
            
            if labels == ["No Loans"]:
                ax.pie(vals, labels=labels, colors=clr, startangle=90,
                       textprops={"fontsize": 9, "color": T1}, wedgeprops={"linewidth": 1.5, "edgecolor": WHITE})
            else:
                ax.pie(vals, labels=labels, colors=clr, autopct="%1.0f%%", startangle=90,
                       textprops={"fontsize": 9, "color": T1}, wedgeprops={"linewidth": 1.5, "edgecolor": WHITE})
            
            ax.axis('equal')
            tk.Label(self.pie_host, text="Branch Loan Approvals", bg=WHITE, fg=T1, font=(FONT, 12, "bold")).pack(anchor="w", padx=16, pady=(16,0))
            cv = FigureCanvasTkAgg(fig, master=self.pie_host)
            cv.draw()
            cv.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            plt.close(fig) # Cleanup to avoid memory leaks
            
        self.after(0, _render)

    def _draw_txn_bar(self):
        from gui.db_connection import DatabaseConnection
        db = DatabaseConnection()
        q = """SELECT transaction_type, COUNT(*) as cnt FROM TRANSACTION 
               WHERE ref_branch_code = :1
               GROUP BY transaction_type"""
        rows = db.execute_query(q, (self.branch_code,)) or []
        
        def _render():
            # Clear old children
            for w in self.bar_host.winfo_children(): w.destroy()
            
            labels = [r.get("TRANSACTION_TYPE","") for r in rows]
            vals   = [float(r.get("CNT") or 0) for r in rows]
            if not vals:
                labels = ["No Txns"]; vals = [0]

            x = np.arange(len(labels))
            # Create figure in MAIN thread
            fig, ax = plt.subplots(figsize=(4, 3))
            fig.patch.set_facecolor(WHITE); ax.set_facecolor(WHITE)
            ax.bar(x, vals, 0.5, color=GOLD)
            ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9)
            ax.tick_params(colors=T2, labelsize=9)
            ax.spines[["top","right","left"]].set_visible(False)
            ax.set_ylabel("Count", fontsize=9, color=T2)
            
            tk.Label(self.bar_host, text="Branch Transaction Types", bg=WHITE, fg=T1, font=(FONT, 12, "bold")).pack(anchor="w", padx=16, pady=(16,0))
            cv = FigureCanvasTkAgg(fig, master=self.bar_host)
            cv.draw()
            cv.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            plt.close(fig)

        self.after(0, _render)

