import tkinter as tk
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
from gui.db_connection import DatabaseConnection

NAVY = "#0D1B2A"; GOLD = "#E8A020"
BG = "#F0F4F8"; WHITE = "#FFFFFF"
T1 = "#1A1A2E"; T2 = "#6B7280"; FONT = "Segoe UI"


class BranchReportsPage(tk.Frame):
    def __init__(self, master, branch_code: str, **kw):
        super().__init__(master, bg=BG, **kw)
        self.branch_code = branch_code
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=20, pady=(16, 8))
        tk.Label(bar, text="Branch Reports", bg=BG, fg=T1,
                 font=(FONT, 16, "bold")).pack(side="left")
        tk.Button(bar, text="↺ Refresh", command=self.refresh,
                  bg=WHITE, fg=T1, font=(FONT, 11, "bold"),
                  bd=0, padx=14, pady=8, cursor="hand2").pack(side="right")

        self.cv = tk.Canvas(self, bg=BG, highlightthickness=0)
        sb = tk.Scrollbar(self, orient="vertical", command=self.cv.yview)
        self.cv.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        self.cv.pack(side="left", fill="both", expand=True)
        self._inner = tk.Frame(self.cv, bg=BG)
        self._win = self.cv.create_window((0, 0), window=self._inner, anchor="nw")
        self._inner.bind("<Configure>", lambda e: (
            self.cv.configure(scrollregion=self.cv.bbox("all")),
            self.cv.itemconfig(self._win, width=self.cv.winfo_width()),
        ))
        self.cv.bind("<Configure>", lambda e: self.cv.itemconfig(self._win, width=e.width))

    def refresh(self):
        for w in self._inner.winfo_children(): w.destroy()
        
        db = DatabaseConnection()
        rows = db.execute_query("SELECT * FROM vw_branch_summary WHERE branch_code = :1", (self.branch_code,))
        b_data = rows[0] if rows else {}

        # 1. Stat cards
        row = tk.Frame(self._inner, bg=BG)
        row.pack(fill="x", padx=20, pady=(12, 8))

        stats = [
            ("Employees",  b_data.get("TOTAL_EMPLOYEES", 0), "👥"),
            ("Accounts",   b_data.get("TOTAL_ACCOUNTS", 0),  "🏦"),
            ("Balance",    f"PKR {float(b_data.get('TOTAL_DEPOSITS', 0) or 0):,.0f}", "💰"),
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

        # 2. Charts
        r = tk.Frame(self._inner, bg=BG)
        r.pack(fill="x", padx=20, pady=8)
        
        loan_card = ctk.CTkFrame(r, fg_color=WHITE, corner_radius=12, height=300)
        loan_card.pack(fill="both", expand=True, padx=6)
        loan_card.pack_propagate(False)
        self._draw_loan_pie(loan_card)

    def _draw_loan_pie(self, parent):
        tk.Label(parent, text="Branch Loan Status Breakdown", bg=WHITE, fg=T1,
                 font=(FONT, 11, "bold")).pack(anchor="w", padx=12, pady=(10, 0))
        
        # Use a localized db connection for the thread
        from gui.db_connection import DatabaseConnection
        
        def _fetch():
            db = DatabaseConnection()
            q = """SELECT approval_status, COUNT(*) as cnt FROM LOAN 
                   WHERE ref_account_id IN (SELECT account_id FROM ACCOUNT WHERE ref_branch_code = :1)
                   GROUP BY approval_status"""
            rows = db.execute_query(q, (self.branch_code,)) or []
            
            def _render():
                if not parent.winfo_exists(): return
                labels = [r.get("APPROVAL_STATUS","") for r in rows]
                vals   = [float(r.get("CNT") or 0) for r in rows]
                
                if not vals:
                    labels = ["No Loans"]; vals = [1]
                    
                colors = { "APPROVED": NAVY, "PENDING": GOLD, "REJECTED": "#E74C3C", "No Loans": "#D1D9E6" }
                clr = [colors.get(l, "#888888") for l in labels]
                
                fig, ax = plt.subplots(figsize=(4, 3))
                fig.patch.set_facecolor(WHITE)
                ax.pie(vals, labels=labels, colors=clr, autopct="%1.0f%%", startangle=90,
                       textprops={"fontsize": 8, "color": T1}, wedgeprops={"linewidth": 1.5, "edgecolor": WHITE})
                
                cv = FigureCanvasTkAgg(fig, master=parent)
                cv.draw()
                cv.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
                plt.close(fig)
            
            self.after(0, _render)
            
        threading.Thread(target=_fetch, daemon=True).start()