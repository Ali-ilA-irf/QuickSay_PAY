import tkinter as tk
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from gui.models.employee_model import EmployeeModel
from gui.models.account_model import AccountModel
from gui.models.loan_model import LoanModel
from gui.models.transaction_model import TransactionModel
from gui.db_connection import DatabaseConnection

NAVY = "#0D1B2A"; GOLD = "#E8A020"
BG = "#F0F4F8"; WHITE = "#FFFFFF"
T1 = "#1A1A2E"; T2 = "#6B7280"; FONT = "Segoe UI"
GREEN = "#27AE60"; RED = "#E74C3C"; BORDER = "#E2E8F0"


class SystemReportsPage(tk.Frame):
    def __init__(self, master, **kw):
        super().__init__(master, bg=BG, **kw)
        self.emp_m = EmployeeModel()
        self.acc_m = AccountModel()
        self.loan_m = LoanModel()
        self.txn_m  = TransactionModel()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # Toolbar
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=20, pady=(16, 8))
        tk.Label(bar, text="System Reports", bg=BG, fg=T1,
                 font=(FONT, 16, "bold")).pack(side="left")
        tk.Button(bar, text="↺ Refresh", command=self.refresh,
                  bg=WHITE, fg=T1, font=(FONT, 11, "bold"),
                  bd=0, padx=14, pady=8, cursor="hand2").pack(side="right")
        try:
            from reportlab.lib.pagesizes import A4
            tk.Button(bar, text="⬇ Export PDF", command=self._export_pdf,
                      bg=NAVY, fg=GOLD, font=(FONT, 11, "bold"),
                      bd=0, padx=14, pady=8, cursor="hand2").pack(side="right", padx=(0, 8))
        except ImportError:
            pass

        # Scrollable canvas
        cv = tk.Canvas(self, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(self, orient="vertical", command=cv.yview)
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
        self._inner = inner

    def refresh(self):
        for w in self._inner.winfo_children():
            w.destroy()
        self._build_stat_cards()
        self._build_charts()
        self._build_branch_table()

    # ── KPI stat cards ────────────────────────────────────────
    def _build_stat_cards(self):
        kpi = self.emp_m.get_total_counts()
        row = tk.Frame(self._inner, bg=BG)
        row.pack(fill="x", padx=20, pady=(12, 8))

        stats = [
            ("Total Employees",  kpi.get("EMPLOYEES", "—"),   "👥"),
            ("Total Branches",   kpi.get("BRANCHES", "—"),    "🏢"),
            ("Total Customers",  kpi.get("CUSTOMERS", "—"),   "👤"),
            ("Total Accounts",   kpi.get("ACCOUNTS", "—"),    "🏦"),
            ("Total Balance",    f"PKR {float(kpi.get('TOTAL_BALANCE') or 0):,.0f}", "💰"),
            ("Pending Loans",    kpi.get("PENDING_LOANS","—"),"📋"),
        ]
        for i, (label, val, icon) in enumerate(stats):
            c = ctk.CTkFrame(row, fg_color=WHITE, corner_radius=10, height=80)
            c.grid(row=0, column=i, padx=6, sticky="nsew")
            c.pack_propagate(False)
            row.columnconfigure(i, weight=1)
            tk.Label(c, text=f"{icon}  {label}", bg=WHITE, fg=T2,
                     font=(FONT, 10)).pack(anchor="w", padx=12, pady=(10, 0))
            tk.Label(c, text=str(val), bg=WHITE, fg=NAVY,
                     font=(FONT, 18, "bold")).pack(anchor="w", padx=12)

    # ── Charts ────────────────────────────────────────────────
    def _build_charts(self):
        r = tk.Frame(self._inner, bg=BG)
        r.pack(fill="x", padx=20, pady=8)
        r.columnconfigure(0, weight=6)
        r.columnconfigure(1, weight=4)

        bar_card = ctk.CTkFrame(r, fg_color=WHITE, corner_radius=12, height=260)
        bar_card.grid(row=0, column=0, padx=(0, 8), sticky="nsew")
        bar_card.pack_propagate(False)
        self._draw_bar(bar_card)

        loan_card = ctk.CTkFrame(r, fg_color=WHITE, corner_radius=12, height=260)
        loan_card.grid(row=0, column=1, padx=(8, 0), sticky="nsew")
        loan_card.pack_propagate(False)
        self._draw_loan_pie(loan_card)

    def _draw_bar(self, parent):
        tk.Label(parent, text="Monthly Transactions", bg=WHITE, fg=T1,
                 font=(FONT, 11, "bold")).pack(anchor="w", padx=12, pady=(10, 0))
        rows = self.txn_m.get_monthly_counts()
        if rows:
            months = [r.get("MONTH_LABEL","") for r in rows]
            deps   = [float(r.get("DEPOSIT_COUNT") or 0) for r in rows]
            wds    = [float(r.get("WITHDRAWAL_COUNT") or 0) for r in rows]
        else:
            months = ["No Data"]; deps = [0]; wds = [0]
        x = np.arange(len(months))
        fig, ax = plt.subplots(figsize=(5, 2.2))
        fig.patch.set_facecolor(WHITE); ax.set_facecolor(WHITE)
        ax.bar(x - 0.18, deps, 0.32, color=NAVY, label="Deposits")
        ax.bar(x + 0.18, wds,  0.32, color=GOLD, label="Withdrawals")
        ax.set_xticks(x); ax.set_xticklabels(months, fontsize=7, rotation=20)
        ax.tick_params(colors=T2, labelsize=7)
        ax.spines[["top","right","left"]].set_visible(False)
        ax.legend(fontsize=7, framealpha=0)
        cv = FigureCanvasTkAgg(fig, master=parent)
        cv.draw(); cv.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
        plt.close(fig)

    def _draw_loan_pie(self, parent):
        tk.Label(parent, text="Loan Status Breakdown", bg=WHITE, fg=T1,
                 font=(FONT, 11, "bold")).pack(anchor="w", padx=12, pady=(10, 0))
        db = DatabaseConnection()
        rows = db.execute_query(
            "SELECT approval_status, COUNT(*) AS cnt "
            "FROM LOAN GROUP BY approval_status") or []
        labels = [r.get("APPROVAL_STATUS","") for r in rows]
        vals   = [float(r.get("CNT") or 0) for r in rows]
        
        has_loans = len(vals) > 0
        if not has_loans:
            labels = ["No Loans"]; vals = [1]
            
        colors = {
            "APPROVED": NAVY, "PENDING": GOLD,
            "REJECTED": "#E74C3C", "PAID": GREEN, "No Loans": "#D1D9E6",
        }
        clr = [colors.get(l, "#888888") for l in labels]
        fig, ax = plt.subplots(figsize=(3, 2.2))
        fig.patch.set_facecolor(WHITE)
        ax.pie(vals, labels=labels, colors=clr,
               autopct="%1.0f%%" if has_loans else None, startangle=90,
               textprops={"fontsize": 7, "color": T1},
               wedgeprops={"linewidth": 1.5, "edgecolor": WHITE})
        cv = FigureCanvasTkAgg(fig, master=parent)
        cv.draw(); cv.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
        plt.close(fig)

    # ── Branch table ──────────────────────────────────────────
    def _build_branch_table(self):
        from gui.utils.fast_table import make_treeview, populate_tree
        card = ctk.CTkFrame(self._inner, fg_color=WHITE, corner_radius=12)
        card.pack(fill="x", padx=20, pady=(0, 20))
        tk.Label(card, text="Branch Summary", bg=WHITE, fg=T1,
                 font=(FONT, 12, "bold")).pack(anchor="w", padx=14, pady=(12, 4))
        tv = make_treeview(card, ["Branch", "Address", "Employees",
                                   "Accounts", "Total Balance (PKR)"])
        db = DatabaseConnection()
        rows = db.execute_query("SELECT * FROM vw_branch_summary") or []
        populate_tree(tv, [
            [r.get("BRANCH_CODE",""), r.get("BRANCH_ADDRESS",""),
             r.get("TOTAL_EMPLOYEES",""), r.get("TOTAL_ACCOUNTS",""),
             f"PKR {float(r.get('TOTAL_DEPOSITS') or 0):,.2f}"]
            for r in rows])

    # ── PDF Export ────────────────────────────────────────────
    def _export_pdf(self):
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
            from reportlab.lib import colors
            from reportlab.lib.styles import getSampleStyleSheet
            import tkinter.filedialog as fd
            path = fd.asksaveasfilename(defaultextension=".pdf",
                                        filetypes=[("PDF", "*.pdf")],
                                        initialfile="bank_report.pdf")
            if not path:
                return
            doc = SimpleDocTemplate(path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = [Paragraph("Bank Management System — System Report", styles["Title"]),
                     Spacer(1, 12)]
            kpi = self.emp_m.get_total_counts()
            data = [["Metric", "Value"],
                    ["Employees",  str(kpi.get("EMPLOYEES","—"))],
                    ["Branches",   str(kpi.get("BRANCHES","—"))],
                    ["Customers",  str(kpi.get("CUSTOMERS","—"))],
                    ["Accounts",   str(kpi.get("ACCOUNTS","—"))],
                    ["Total Balance", f"PKR {float(kpi.get('TOTAL_BALANCE') or 0):,.2f}"],
                    ["Pending Loans", str(kpi.get("PENDING_LOANS","—"))]]
            t = Table(data, colWidths=[250, 200])
            t.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,0), colors.HexColor(NAVY)),
                ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
                ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
                ("GRID",       (0,0), (-1,-1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F0F4F8")]),
            ]))
            story.append(t)
            doc.build(story)
            import tkinter.messagebox as mb
            mb.showinfo("Export", f"Report saved to:\n{path}")
        except Exception as ex:
            import tkinter.messagebox as mb
            mb.showerror("Export Error", str(ex))