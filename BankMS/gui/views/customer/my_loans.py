import tkinter as tk
import customtkinter as ctk
import threading
from tkinter import messagebox
from gui.models.loan_model import LoanModel
from gui.models.loan_payment_model import LoanPaymentModel
from gui.models.account_model import AccountModel
from gui.utils.fast_table import make_treeview, populate_tree

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY   = "#0D1B2A"; GOLD = "#E8A020"; BG = "#F0F4F8"; WHITE = "#FFFFFF"
T1     = "#1A1A2E"; T2 = "#6B7280"; GREEN = "#27AE60"; RED = "#E74C3C"
FONT   = "Playfair Display"


class MyLoansPage(tk.Frame):
    COLS = ["Loan ID", "Amount (PKR)", "Rate", "Term (Mo)", "Applied", "Status", "Remaining (PKR)", "Est. Monthly"]

    def __init__(self, master, customer_id, **kw):
        super().__init__(master, bg=BG, **kw)
        self.customer_id = customer_id
        self.loan_m = LoanModel()
        
        self._build_ui()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=30, pady=(30, 10))
        
        tk.Label(hdr, text="My Loans", bg=BG, fg=NAVY, 
                 font=(FONT, 18, "bold")).pack(side="left")
        
        btn_frame = tk.Frame(hdr, bg=BG)
        btn_frame.pack(side="right")
        
        tk.Button(btn_frame, text="💵 Pay Installment", command=self._pay_installment,
                  bg=GREEN, fg=WHITE, font=(FONT, 10, "bold"),
                  bd=0, padx=12, pady=6, cursor="hand2").pack(side="left", padx=(0, 10))

        tk.Button(btn_frame, text="↺ Refresh", command=self.refresh,
                  bg=WHITE, fg=T1, font=(FONT, 10, "bold"),
                  bd=0, padx=12, pady=6, cursor="hand2").pack(side="left")

        # Table Card
        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12)
        card.pack(fill="both", expand=True, padx=30, pady=20)
        
        self._tv = make_treeview(card, self.COLS)

    def refresh(self):
        # Only show active (APPROVED) loans — PAID loans are removed automatically
        all_rows = self.loan_m.get_loans_by_customer(self.customer_id) or []
        rows = [r for r in all_rows if r.get("APPROVAL_STATUS", "") != 'PAID']

        data = []
        for r in rows:
            amt      = float(r.get("LOAN_AMOUNT") or 0)
            remaining = float(r.get("CURRENT_REMAINING_BALANCE") or amt)
            data.append([
                r.get("LOAN_ID", "—"),
                f"PKR {amt:,.2f}",
                f"{r.get('INTEREST_RATE', 0)}%",
                r.get("TERM_MONTHS", "—"),
                r.get("APP_DATE") or r.get("APPLICATION_DATE") or "—",
                r.get("APPROVAL_STATUS", "—"),
                f"PKR {remaining:,.2f}",
            ])

        self.after(0, lambda: populate_tree(self._tv, data))

        def _worker():
            final = []
            for i, r in enumerate(rows):
                loan_id = r.get("LOAN_ID")
                est = 0.0
                try:
                    if loan_id is not None:
                        est = self.loan_m.calc_monthly_interest(int(loan_id))
                except Exception:
                    est = 0.0
                amt      = float(r.get("LOAN_AMOUNT") or 0)
                remaining = float(r.get("CURRENT_REMAINING_BALANCE") or amt)
                final.append([
                    r.get("LOAN_ID", "—"),
                    f"PKR {amt:,.2f}",
                    f"{r.get('INTEREST_RATE', 0)}%",
                    r.get("TERM_MONTHS", "—"),
                    r.get("APP_DATE") or r.get("APPLICATION_DATE") or "—",
                    r.get("APPROVAL_STATUS", "—"),
                    f"PKR {remaining:,.2f}",
                    f"PKR {est:,.2f}"
                ])
            self.after(0, lambda: populate_tree(self._tv, final))
        threading.Thread(target=_worker, daemon=True).start()

    def _pay_installment(self):
        sel = self._tv.selection()
        if not sel:
            messagebox.showwarning("Select Loan", "Please select a loan to pay.")
            return
            
        item = self._tv.item(sel[0])["values"]
        status = item[5]
        if status != 'APPROVED':
            messagebox.showwarning("Invalid", "You can only pay approved/active loans.")
            return
            
        loan_id   = item[0]
        status    = item[5]
        remaining_str = item[6].replace('PKR', '').replace(',', '').strip()  # Remaining (PKR) column
        est_str   = item[7].replace('PKR', '').replace(',', '').strip() if len(item) > 7 else '0'

        try:
            current_remaining = float(remaining_str)
        except ValueError:
            current_remaining = 0.0
        try:
            amt = float(est_str)     # monthly instalment
        except ValueError:
            amt = 0.0
        if amt <= 0:
            messagebox.showwarning("No Balance", "This loan requires no payment.")
            return

        # Correct remaining balance after this payment
        new_remaining = max(0.0, current_remaining - amt)

        acc_m = AccountModel()
        accs = acc_m.get_accounts_by_customer(self.customer_id)
        if not accs:
            messagebox.showerror("Error", "You have no accounts to pay from.")
            return

        top = ctk.CTkToplevel(self)
        top.title("Pay Installment")
        top.geometry("400x400")
        top.transient(self.master)
        top.grab_set()

        tk.Label(top, text="Pay Installment", font=(FONT, 16, "bold")).pack(pady=(20, 6))
        tk.Label(top, text=f"Instalment Amount:  PKR {amt:,.2f}").pack()
        tk.Label(top, text=f"Remaining After Payment:  PKR {new_remaining:,.2f}",
                 fg=GREEN if new_remaining == 0 else NAVY).pack(pady=(4, 0))
        if new_remaining == 0:
            tk.Label(top, text="✅ Loan will be marked as PAID",
                     fg=GREEN, font=(FONT, 10, "bold")).pack(pady=(2, 0))

        tk.Label(top, text="Select Account to Deduct:").pack(pady=(12, 0))
        acc_var = ctk.StringVar(value=str(accs[0]["ACCOUNT_ID"]))

        for a in accs:
            disp = f"{a['ACCOUNT_NUMBER']} (Balance: PKR {float(a.get('CURRENT_BALANCE') or 0):,.2f})"
            ctk.CTkRadioButton(top, text=disp, variable=acc_var, value=str(a["ACCOUNT_ID"])).pack(pady=5)

        def _confirm():
            acc_id = int(acc_var.get())
            pay_m = LoanPaymentModel()
            try:
                if pay_m.record_payment(loan_id, self.customer_id, acc_id, amt, new_remaining):
                    messagebox.showinfo("Success", "Payment successful.")
                    top.destroy()
                    self.refresh()
                    # Traverse up to the main dashboard container to trigger refresh_all
                    self.master.master.master.master.refresh_all()
                else:
                    messagebox.showerror("Failed", "Payment failed. Check account balance.")
            except Exception as e:
                err = str(e).split('\n')[0]
                messagebox.showerror("Error", err)

        ctk.CTkButton(top, text="Confirm Payment", command=_confirm, fg_color=GREEN).pack(pady=20)