import tkinter as tk
import customtkinter as ctk
from gui.models.transaction_model import TransactionModel
from gui.models.account_model import AccountModel

NAVY = "#0D1B2A"; GOLD = "#E8A020"; BG = "#F0F4F8"; WHITE = "#FFFFFF"
T1 = "#1A1A2E"; T2 = "#6B7280"; GREEN = "#27AE60"; RED = "#E74C3C"
BORDER = "#E2E8F0"
FONT = "Playfair Display"


class CashTxnPage(tk.Frame):
    def __init__(self, master, branch_code: str, user_data: dict, **kw):
        super().__init__(master, bg=BG, **kw)
        self.branch_code = branch_code
        self.user_data   = user_data
        self.txn_m       = TransactionModel()
        self.acc_m       = AccountModel()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12)
        card.pack(fill="both", expand=True, padx=80, pady=80)
        
        tk.Label(card, text="💵 Cash Deposit / Withdrawal", bg=WHITE, fg=NAVY,
                 font=(FONT, 16, "bold")).pack(pady=(24, 16))

        tk.Label(card, text="Search Account (No. or Name)", bg=WHITE, fg=T2, font=(FONT, 11)).pack(anchor="w", padx=30, pady=(10, 2))
        self.search_var = ctk.StringVar()
        s_entry = ctk.CTkEntry(card, textvariable=self.search_var, placeholder_text="🔍  Search account number or name…",
                               fg_color=WHITE, border_color=GOLD, border_width=1,
                               height=36, corner_radius=8, text_color=T1, placeholder_text_color="#9CA3AF")
        s_entry.pack(fill="x", padx=30)
        s_entry.bind("<KeyRelease>", lambda _: self._filter_accounts())

        tk.Label(card, text="Select Account", bg=WHITE, fg=T2, font=(FONT, 11)).pack(anchor="w", padx=30, pady=(10, 2))
        self.acc_var = ctk.StringVar()
        self.acc_menu = ctk.CTkOptionMenu(card, variable=self.acc_var, values=["Loading..."],
                                          fg_color=WHITE, text_color=T1, button_color=NAVY,
                                          height=40, corner_radius=8, anchor="w",
                                          command=self._on_acc_select)
        self.acc_menu.pack(fill="x", padx=30)

        self._l_bal = tk.Label(card, text="", bg=WHITE, fg=T2, font=(FONT, 10, "italic"))
        self._l_bal.pack(anchor="w", padx=30, pady=(2, 8))

        self._f_amt = self._field(card, "Amount (PKR)")

        self._ferr = tk.Label(card, text="", bg=WHITE, font=(FONT, 11))
        self._ferr.pack(pady=(8, 0))

        row = tk.Frame(card, bg=WHITE)
        row.pack(fill="x", padx=30, pady=(12, 24))
        tk.Button(row, text="Deposit", bg=GREEN, fg=WHITE,
                  font=(FONT, 12, "bold"), bd=0, padx=14, pady=12,
                  cursor="hand2", command=self._deposit).pack(side="left", fill="x", expand=True, padx=(0, 4))
        tk.Button(row, text="Withdraw", bg=GOLD, fg=NAVY,
                  font=(FONT, 12, "bold"), bd=0, padx=14, pady=12,
                  cursor="hand2", command=self._withdraw).pack(side="right", fill="x", expand=True, padx=(4, 0))

    def _field(self, parent, label):
        tk.Label(parent, text=label, bg=WHITE, fg=T2, font=(FONT, 11)).pack(anchor="w", padx=30, pady=(10, 2))
        var = tk.StringVar()
        ctk.CTkEntry(parent, textvariable=var, fg_color=WHITE,
                     border_color=GOLD, border_width=1,
                     height=40, corner_radius=8, text_color=T1).pack(fill="x", padx=30)
        return var

    def refresh(self):
        self.all_accs = self.acc_m.get_all_accounts() or []
        self._filter_accounts()

    def _filter_accounts(self):
        kw = self.search_var.get().strip().lower()
        filtered = [a for a in self.all_accs if kw in str(a.get("ACCOUNT_NUMBER", "")).lower() or kw in str(a.get("CUSTOMER_NAME", "")).lower()]
        self.acc_map = {f"{a.get('ACCOUNT_NUMBER')} - {a.get('CUSTOMER_NAME')}": a for a in filtered}
        vals = list(self.acc_map.keys())
        if vals:
            self.acc_menu.configure(values=vals)
            self.acc_var.set(vals[0])
            self._on_acc_select(vals[0])
        else:
            self.acc_menu.configure(values=["No Accounts found"])
            self.acc_var.set("No Accounts found")
            self._l_bal.config(text="")

    def _on_acc_select(self, val):
        a = self.acc_map.get(val)
        if a:
            bal = float(a.get("CURRENT_BALANCE") or 0)
            self._l_bal.config(text=f"Current Balance: PKR {bal:,.2f}")

    def _deposit(self):
        self._process("DEPOSIT")

    def _withdraw(self):
        self._process("WITHDRAWAL")

    def _process(self, ttype):
        if not hasattr(self, 'acc_map') or not self.acc_map: return
        try:
            aid = self.acc_map[self.acc_var.get()]["ACCOUNT_ID"]
            amt = float(self._f_amt.get().strip() or 0)
            if amt <= 0: raise ValueError

            if ttype == "DEPOSIT":
                ok = self.txn_m.deposit(aid, self.branch_code, amt, self.user_data.get("EMPLOYEE_ID"))
            else:
                ok = self.txn_m.withdraw(aid, self.branch_code, amt, self.user_data.get("EMPLOYEE_ID"))

            if ok:
                self._ferr.config(text=f"✓ {ttype.capitalize()} of PKR {amt:,.2f} successful!", fg=GREEN)
                self._f_amt.set("")
                self.refresh()
                self._show_receipt({
                    "Type": ttype.capitalize(),
                    "Amount": f"PKR {amt:,.2f}",
                    "Account": self.acc_map[self.acc_var.get()]["ACCOUNT_NUMBER"],
                    "Status": "Successful"
                })
            else:
                self._ferr.config(text=f"❌ Failed to {ttype.lower()}. Insufficient funds or error.", fg=RED)
        except ValueError:
            self._ferr.config(text="Invalid amount.", fg=RED)
        except Exception as e:
            err_msg = str(e).split('\n')[0]
            self._ferr.config(text=f"❌ {err_msg}", fg=RED)

    def _show_receipt(self, details: dict):
        top = ctk.CTkToplevel(self)
        top.title("Transaction Receipt")
        top.geometry("400x450")
        top.transient(self.master)
        top.grab_set()
        top.configure(fg_color=BG)
        
        card = ctk.CTkFrame(top, fg_color=WHITE, corner_radius=15)
        card.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(card, text="QuickSay Pay", bg=WHITE, fg=NAVY, font=(FONT, 20, "bold")).pack(pady=(20, 5))
        tk.Label(card, text="Teller Receipt", bg=WHITE, fg=T2, font=(FONT, 12)).pack(pady=(0, 20))
        
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=20, pady=10)
        
        for k, v in details.items():
            r = tk.Frame(card, bg=WHITE)
            r.pack(fill="x", padx=30, pady=8)
            tk.Label(r, text=k, bg=WHITE, fg=T2, font=(FONT, 11)).pack(side="left")
            tk.Label(r, text=v, bg=WHITE, fg=T1, font=(FONT, 11, "bold")).pack(side="right")
            
        tk.Frame(card, bg=BORDER, height=1).pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(card, text="Print / Close", fg_color=NAVY, hover_color=GOLD, 
                      command=top.destroy).pack(pady=10)