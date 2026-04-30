import tkinter as tk
import customtkinter as ctk
from gui.models.loan_model import LoanModel
from gui.models.employee_model import EmployeeModel
from gui.utils.fast_table import make_treeview, populate_tree

NAVY   = "#0D1B2A"; GOLD = "#E8A020"; GOLD_D = "#C8881A"
BG     = "#F0F4F8"; WHITE = "#FFFFFF"
T1     = "#1A1A2E"; T2 = "#6B7280"
GREEN  = "#27AE60"; RED = "#E74C3C"; FONT = "Playfair Display"


class LoanApprovalPage(tk.Frame):
    def __init__(self, master, branch_code: str, user_data: dict, **kw):
        super().__init__(master, bg=BG, **kw)
        self.branch_code = branch_code
        self.user_data   = user_data
        self.loan_m      = LoanModel()
        self._all_rows   = []
        self._selected   = None

        self._build_toolbar()
        self._build_table()
        self._build_form_panel()

    def _build_toolbar(self):
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=20, pady=(16, 8))
        tk.Button(bar, text="↺ Refresh", command=self.refresh,
                  bg=WHITE, fg=T1, font=(FONT, 11, "bold"),
                  bd=0, padx=14, pady=8, cursor="hand2").pack(side="left")

    def _build_table(self):
        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12)
        card.pack(fill="both", expand=True, padx=20, pady=(4, 20))
        self._tv = make_treeview(card, ["Loan ID", "Customer", "Amount (PKR)", "Date Applied", "Status"])
        self._tv.bind("<<TreeviewSelect>>", self._on_sel)

    def _build_form_panel(self):
        self._fp = tk.Frame(self, bg=WHITE, width=500)
        hdr = tk.Frame(self._fp, bg=NAVY, height=52)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text="Review Loan", bg=NAVY, fg=WHITE,
                 font=(FONT, 13, "bold")).pack(side="left", padx=16)
        tk.Button(hdr, text="✕", bg=NAVY, fg=WHITE, bd=0,
                  font=(FONT, 13), cursor="hand2",
                  command=self._close_form).pack(side="right", padx=12)

        body = tk.Frame(self._fp, bg=WHITE)
        body.pack(fill="both", expand=True, padx=20, pady=14)

        self._l_id   = self._info_row(body, "Loan ID")
        self._l_cust = self._info_row(body, "Customer")
        self._l_amt  = self._info_row(body, "Amount")
        self._l_rate = self._info_row(body, "Interest Rate")
        self._l_term = self._info_row(body, "Term (Months)")

        self._ferr = tk.Label(body, text="", bg=WHITE, font=(FONT, 10))
        self._ferr.pack(pady=(16, 8))

        row = tk.Frame(body, bg=WHITE)
        row.pack(fill="x", pady=20)
        
        self.btn_app = ctk.CTkButton(row, text="✓ Approve Loan", fg_color=GREEN, hover_color="#219150",
                                     font=(FONT, 12, "bold"), height=45, corner_radius=8,
                                     command=self._approve)
        self.btn_app.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.btn_rej = ctk.CTkButton(row, text="✕ Reject Application", fg_color=RED, hover_color="#C0392B",
                                     font=(FONT, 12, "bold"), height=45, corner_radius=8,
                                     command=self._reject)
        self.btn_rej.pack(side="right", fill="x", expand=True, padx=(5, 0))

    def _info_row(self, parent, label):
        r = tk.Frame(parent, bg=WHITE)
        r.pack(fill="x", pady=6)
        tk.Label(r, text=label, bg=WHITE, fg=T2, font=(FONT, 11)).pack(side="left")
        val = tk.Label(r, text="—", bg=WHITE, fg=T1, font=(FONT, 11, "bold"))
        val.pack(side="right")
        return val

    def refresh(self):
        all_loans = self.loan_m.get_pending_loans() or []
        self._all_rows = []
        for l in all_loans:
            b = l.get("BRANCH_CODE") or l.get("REF_BRANCH_CODE")
            if b == self.branch_code or b is None:
                self._all_rows.append(l)
        self._render(self._all_rows)
        self._close_form()

    def _render(self, rows):
        data = []
        for r in rows:
            try:
                amt = float(r.get('LOAN_AMOUNT') or 0)
                amt_str = f"PKR {amt:,.2f}"
            except Exception:
                amt_str = "PKR 0.00"
                
            data.append([
                r.get("LOAN_ID","—"), 
                r.get("CUSTOMER_NAME","—"),
                amt_str,
                r.get("APP_DATE") or r.get("APPLICATION_DATE") or "—", 
                r.get("APPROVAL_STATUS","—")
            ])
        populate_tree(self._tv, data)

    def _on_sel(self, _=None):
        sel = self._tv.selection()
        if sel:
            l_id = self._tv.item(sel[0])["values"][0]
            row = next((r for r in self._all_rows if str(r.get("LOAN_ID")) == str(l_id)), None)
            if row:
                self._selected = row
                self._l_id.config(text=str(row.get("LOAN_ID")))
                self._l_cust.config(text=str(row.get("CUSTOMER_NAME")))
                self._l_amt.config(text=f"PKR {float(row.get('LOAN_AMOUNT') or 0):,.2f}", fg=GREEN)
                self._l_rate.config(text=f"{row.get('INTEREST_RATE',0)}%")
                self._l_term.config(text=str(row.get("TERM_MONTHS")))
                self._ferr.config(text="")
                self._show_form()

    def _show_form(self):
        self.update_idletasks()
        w = self.winfo_width() or 900
        self._fp.place(x=w, y=0, width=500, relheight=1.0)
        self._fp.lift()
        self._slide(w, w - 500)

    def _close_form(self):
        self.update_idletasks()
        w = self.winfo_width() or 900
        self._slide(w - 500, w, closing=True)

    def _slide(self, x, target, closing=False, step=40):
        going = (x > target) if not closing else (x < target)
        if going:
            x = (min if not closing else max)(x + (-step if not closing else step), target)
            self._fp.place(x=x)
            self.after(8, lambda: self._slide(x, target, closing, step))
        elif closing:
            self._fp.place_forget()

    def _approve(self):
        if not self._selected: return
        # Manager is an employee; login data has USER_ID for both types
        emp_id = self.user_data.get("USER_ID") or self.user_data.get("EMPLOYEE_ID")
        if not emp_id:
            self._ferr.config(text="Session Error: No User ID", fg=RED)
            return
            
        ok = self.loan_m.approve_loan(int(self._selected["LOAN_ID"]), int(emp_id))
        if ok: self.master.master.master.refresh_all()
        else: self._ferr.config(text="Operation failed", fg=RED)

    def _reject(self):
        if not self._selected: return
        emp_id = self.user_data.get("USER_ID") or self.user_data.get("EMPLOYEE_ID")
        if not emp_id:
            self._ferr.config(text="Session Error: No User ID", fg=RED)
            return

        ok = self.loan_m.reject_loan(int(self._selected["LOAN_ID"]), int(emp_id))
        if ok: self.master.master.master.refresh_all()
        else: self._ferr.config(text="Operation failed", fg=RED)