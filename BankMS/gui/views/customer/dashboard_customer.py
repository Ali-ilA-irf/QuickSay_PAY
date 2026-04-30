import tkinter as tk
import customtkinter as ctk
import tkinter.ttk as ttk
from tkinter import messagebox
from gui.models.account_model import AccountModel
from gui.models.transaction_model import TransactionModel
from gui.models.loan_model import LoanModel
from gui.models.beneficiary_model import BeneficiaryModel
from gui.utils.fast_table import make_treeview, populate_tree

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY   = "#0D1B2A"; GOLD = "#E8A020"; BG = "#F0F4F8"; WHITE = "#FFFFFF"
T1     = "#1A1A2E"; T2 = "#6B7280"; GREEN = "#27AE60"; RED = "#E74C3C"
BORDER = "#E2E8F0"; FONT = "Playfair Display"


class CustomerHomePage(tk.Frame):
    def __init__(self, master, customer_id, user_data, **kw):
        super().__init__(master, bg=BG, **kw)
        self.customer_id = customer_id
        self.user_data = user_data
        self.acc_m = AccountModel()
        self.txn_m = TransactionModel()
        self.loan_m = LoanModel()
        self.ben_m = BeneficiaryModel()
        
        self._build_ui()

    def _build_ui(self):
        # Welcome Area
        welcome_f = tk.Frame(self, bg=BG)
        welcome_f.pack(fill="x", padx=30, pady=(30, 20))
        
        tk.Label(welcome_f, text=f"Hello, {self.user_data.get('DISPLAY_NAME', 'Customer')}!", 
                 bg=BG, fg=NAVY, font=(FONT, 24, "bold")).pack(anchor="w")
        tk.Label(welcome_f, text="Here is your financial overview for today.", 
                 bg=BG, fg=T2, font=(FONT, 12)).pack(anchor="w", pady=(4, 0))

        # KPI row
        kpi_f = tk.Frame(self, bg=BG)
        kpi_f.pack(fill="x", padx=24)

        # ── Total Balance Card
        self.c_bal = self._kpi_card(kpi_f, "Total Available Balance", "PKR 0.00", GOLD, "💰")
        # ── Accounts Card
        self.c_acc = self._kpi_card(kpi_f, "Active Accounts", "0", GREEN, "🏦")
        # ── Recent Txns Card
        self.c_txn = self._kpi_card(kpi_f, "Recent Transactions (30d)", "0", NAVY, "🔄")

        # Bottom section: Recent Transactions & Quick Actions
        bottom_f = tk.Frame(self, bg=BG)
        bottom_f.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Recent Transactions List (simplified for now)
        txn_list_f = ctk.CTkFrame(bottom_f, fg_color=WHITE, corner_radius=12)
        txn_list_f.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.Label(txn_list_f, text="Recent Transactions", bg=WHITE, fg=NAVY, 
                 font=(FONT, 14, "bold")).pack(anchor="w", padx=20, pady=20)
        
        self.txn_cont = tk.Frame(txn_list_f, bg=WHITE)
        self.txn_cont.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self._tv = make_treeview(self.txn_cont, ["Date", "Type", "Amount", "Account", "Recipient"])
        self._tv.pack(fill="both", expand=True)
        
        # Quick Actions
        actions_f = ctk.CTkFrame(bottom_f, fg_color=WHITE, corner_radius=12, width=300)
        actions_f.pack(side="right", fill="both", padx=(10, 0))
        actions_f.pack_propagate(False)
        
        tk.Label(actions_f, text="Quick Actions", bg=WHITE, fg=NAVY, 
                 font=(FONT, 14, "bold")).pack(anchor="w", padx=20, pady=20)
        
        self._action_btn(actions_f, "💸 Send Money", GREEN, self._send_money)
        self._action_btn(actions_f, "📱 Pay Bills", GOLD, self._pay_bills)
        self._action_btn(actions_f, "📈 Request Loan", NAVY, self._request_loan)

    def _kpi_card(self, parent, title, value, color, icon):
        card = ctk.CTkFrame(parent, fg_color=WHITE, corner_radius=12, height=140)
        card.pack(side="left", fill="x", expand=True, padx=6)
        card.pack_propagate(False)
        
        tk.Label(card, text=f"{icon}  {title}", bg=WHITE, fg=T2, font=(FONT, 11)).pack(anchor="w", padx=20, pady=(20, 5))
        lbl = tk.Label(card, text=value, bg=WHITE, fg=color, font=(FONT, 24, "bold"))
        lbl.pack(anchor="w", padx=20)
        return lbl

    def _action_btn(self, parent, text, color, cmd=None):
        btn = ctk.CTkButton(parent, text=text, fg_color=color, hover_color=color,
                            font=(FONT, 12, "bold"), height=45, corner_radius=8, cursor="hand2",
                            command=cmd if cmd is not None else (lambda: None))
        btn.pack(fill="x", padx=20, pady=8)

    def _show_receipt(self, details: dict):
        top = ctk.CTkToplevel(self)
        top.title("Transaction Receipt")
        top.geometry("400x500")
        top.transient(self.master)
        top.grab_set()
        top.configure(fg_color=BG)
        
        card = ctk.CTkFrame(top, fg_color=WHITE, corner_radius=15)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(card, text="QuickSay Pay", bg=WHITE, fg=NAVY, font=(FONT, 20, "bold")).pack(pady=(20, 5))
        tk.Label(card, text="Transaction Receipt", bg=WHITE, fg=T2, font=(FONT, 12)).pack(pady=(0, 20))
        
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=20, pady=10)
        
        for k, v in details.items():
            r = tk.Frame(card, bg=WHITE)
            r.pack(fill="x", padx=30, pady=8)
            tk.Label(r, text=k, bg=WHITE, fg=T2, font=(FONT, 11)).pack(side="left")
            tk.Label(r, text=v, bg=WHITE, fg=T1, font=(FONT, 11, "bold")).pack(side="right")
            
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(card, text="Close", fg_color=NAVY, hover_color=GOLD, 
                      command=top.destroy).pack(pady=10)

    def _send_money(self):
        accs = self.acc_m.get_accounts_by_customer(self.customer_id) or []
        if not accs:
            messagebox.showinfo("No accounts", "You have no accounts to send money from.")
            return
            
        bens = self.ben_m.get_beneficiaries_by_customer(self.customer_id) or []
        
        top = ctk.CTkToplevel(self)
        top.title("Send Money")
        top.geometry("450x550")
        top.transient(self.master)
        top.grab_set()
        top.configure(fg_color=BG)

        tk.Label(top, text="Send Money", bg=BG, fg=NAVY, font=(FONT, 20, "bold")).pack(anchor="w", padx=24, pady=(24, 12))

        tk.Label(top, text="From Account", bg=BG, fg=T2, font=(FONT, 11)).pack(anchor="w", padx=24)
        from_var = tk.StringVar()
        options = []
        acct_map = {}
        for a in accs:
            disp = f"{a.get('ACCOUNT_NUMBER')} (PKR {float(a.get('CURRENT_BALANCE') or 0):,.2f})"
            options.append(disp)
            acct_map[disp] = a
        cb = ctk.CTkComboBox(top, values=options, variable=from_var, fg_color=WHITE, text_color=T1, border_color=GOLD, width=400)
        cb.pack(padx=24, pady=6)

        tk.Label(top, text="To Beneficiary / IBAN", bg=BG, fg=T2, font=(FONT, 11)).pack(anchor="w", padx=24, pady=(12,0))
        to_var = tk.StringVar()
        ben_opts = [b.get("IBAN") for b in bens] if bens else ["Manual Entry..."]
        cb2 = ctk.CTkComboBox(top, values=ben_opts, variable=to_var, fg_color=WHITE, text_color=T1, border_color=GOLD, width=400)
        cb2.pack(padx=24, pady=6)

        tk.Label(top, text="Amount (PKR)", bg=BG, fg=T2, font=(FONT, 11)).pack(anchor="w", padx=24, pady=(12,0))
        amt_var = tk.StringVar()
        ctk.CTkEntry(top, textvariable=amt_var, fg_color=WHITE, text_color=T1, border_color=GOLD, width=400).pack(padx=24, pady=6)

        def do_send():
            sel = from_var.get()
            if not sel: return
            try:
                amt = float(amt_var.get())
                if amt <= 0: raise ValueError
            except:
                messagebox.showerror("Error", "Enter a valid positive amount.")
                return
            to_acc = to_var.get().strip()
            if not to_acc or to_acc == "Manual Entry...":
                messagebox.showerror("Error", "Select or enter a recipient IBAN.")
                return
                
            acc = acct_map[sel]
            ok = self.txn_m.transfer(acc.get('ACCOUNT_ID'), acc.get('BRANCH_CODE'), amt, to_acc, None)
            if ok:
                top.destroy()
                self._show_receipt({
                    "Type": "Transfer",
                    "Amount": f"PKR {amt:,.2f}",
                    "From Account": acc.get('ACCOUNT_NUMBER'),
                    "To IBAN": to_acc,
                    "Status": "Successful"
                })
                self.master.master.master.refresh_all()
            else:
                messagebox.showerror("Failed", "Transfer failed. Check balance or target IBAN.")

        ctk.CTkButton(top, text="Transfer Funds", fg_color=GREEN, hover_color="#219653", 
                      font=(FONT, 14, "bold"), height=40, command=do_send).pack(pady=(30, 10))

    def _pay_bills(self):
        self._send_money()

    def _request_loan(self):
        accs = self.acc_m.get_accounts_by_customer(self.customer_id) or []
        if not accs:
            messagebox.showinfo("No accounts", "You need an active account to apply for a loan.")
            return
            
        top = ctk.CTkToplevel(self)
        top.title("Request Loan")
        top.geometry("450x550")
        top.transient(self.master)
        top.grab_set()
        top.configure(fg_color=BG)

        tk.Label(top, text="Request Loan", bg=BG, fg=NAVY, font=(FONT, 20, "bold")).pack(anchor="w", padx=24, pady=(24, 12))

        tk.Label(top, text="Account to credit", bg=BG, fg=T2, font=(FONT, 11)).pack(anchor="w", padx=24)
        from_var = tk.StringVar()
        options = []
        acct_map = {}
        for a in accs:
            disp = f"{a.get('ACCOUNT_NUMBER')} (PKR {float(a.get('CURRENT_BALANCE') or 0):,.2f})"
            options.append(disp)
            acct_map[disp] = a
        cb = ctk.CTkComboBox(top, values=options, variable=from_var, fg_color=WHITE, text_color=T1, border_color=GOLD, width=400)
        cb.pack(padx=24, pady=6)

        tk.Label(top, text="Loan Amount (PKR)", bg=BG, fg=T2, font=(FONT, 11)).pack(anchor="w", padx=24, pady=(12,0))
        amt_var = tk.StringVar()
        ctk.CTkEntry(top, textvariable=amt_var, fg_color=WHITE, text_color=T1, border_color=GOLD, width=400).pack(padx=24, pady=6)

        tk.Label(top, text="Term (months)", bg=BG, fg=T2, font=(FONT, 11)).pack(anchor="w", padx=24, pady=(12,0))
        term_var = tk.StringVar(value='12')
        ctk.CTkEntry(top, textvariable=term_var, fg_color=WHITE, text_color=T1, border_color=GOLD, width=400).pack(padx=24, pady=6)
        
        tk.Label(top, text="Interest Rate (%)", bg=BG, fg=T2, font=(FONT, 11)).pack(anchor="w", padx=24, pady=(12,0))
        rate_var = tk.StringVar(value='10.0')
        ctk.CTkEntry(top, textvariable=rate_var, fg_color=WHITE, text_color=T1, border_color=GOLD, width=400, state="disabled").pack(padx=24, pady=6)

        def do_request():
            sel = from_var.get()
            if not sel: return
            try:
                amt = float(amt_var.get())
                term = int(term_var.get())
                rate = float(rate_var.get())
                if amt <= 0 or term <= 0 or rate <= 0: raise ValueError
            except:
                messagebox.showerror("Error", "Enter valid numeric values.")
                return
                
            acc = acct_map[sel]
            ok = self.loan_m.request_loan(acc.get('ACCOUNT_ID'), self.customer_id, amt, rate, term)
            if ok:
                top.destroy()
                self._show_receipt({
                    "Type": "Loan Request",
                    "Amount Requested": f"PKR {amt:,.2f}",
                    "Term": f"{term} months",
                    "Status": "PENDING APPROVAL"
                })
                self.master.master.master.refresh_all()
            else:
                messagebox.showerror("Failed", "Loan request failed.")

        ctk.CTkButton(top, text="Submit Request", fg_color=NAVY, hover_color=GOLD, 
                      font=(FONT, 14, "bold"), height=40, command=do_request).pack(pady=(30, 10))

    def refresh(self):
        # Fetch actual data (use DB function for accuracy)
        try:
            total_bal = self.acc_m.get_customer_balance(self.customer_id)
        except Exception:
            total_bal = 0.0
        accs = self.acc_m.get_accounts_by_customer(self.customer_id) or []

        self.after(0, lambda: self.c_bal.config(text=f"PKR {total_bal:,.2f}"))
        self.after(0, lambda: self.c_acc.config(text=str(len(accs))))

        # Recent Transactions
        txns = self.txn_m.get_transactions_by_customer(self.customer_id) or []
        # Update Txn count in KPI
        self.after(0, lambda: self.c_txn.config(text=str(len(txns))))
        
        data = []
        for r in txns[:10]: # show only top 10 on home
            amt = float(r.get("TRANSACTION_AMOUNT") or 0)
            data.append([
                r.get("TXN_DATE", ""),
                r.get("TRANSACTION_TYPE", ""),
                f"PKR {amt:,.2f}",
                r.get("ACCOUNT_NUMBER", ""),
                r.get("RECEIVING_ACCOUNT", "Self")
            ])
            
        self.after(0, lambda: populate_tree(self._tv, data))