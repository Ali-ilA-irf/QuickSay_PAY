import tkinter as tk
import customtkinter as ctk
from gui.models.transaction_model import TransactionModel
from gui.models.account_model import AccountModel

NAVY = "#0D1B2A"; GOLD = "#E8A020"; BG = "#F0F4F8"; WHITE = "#FFFFFF"
T1 = "#1A1A2E"; T2 = "#6B7280"; GREEN = "#27AE60"; RED = "#E74C3C"
BORDER = "#E2E8F0"
FONT = "Playfair Display"


class TransferPage(tk.Frame):
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
        card.pack(fill="both", expand=True, padx=80, pady=40)
        
        tk.Label(card, text="🔄 Transfer Funds", bg=WHITE, fg=NAVY,
                 font=(FONT, 16, "bold")).pack(pady=(24, 16))

        # Sender Section
        tk.Label(card, text="From Account (Sender)", bg=WHITE, fg=T2, font=(FONT, 11, "bold")).pack(anchor="w", padx=30, pady=(10, 2))
        
        self.s_search = ctk.StringVar()
        s_entry = ctk.CTkEntry(card, textvariable=self.s_search, placeholder_text="🔍  Search sender (acct no. or name)…",
                               fg_color=WHITE, border_color=GOLD, border_width=1,
                               height=36, corner_radius=8, text_color=T1, placeholder_text_color="#9CA3AF")
        s_entry.pack(fill="x", padx=30, pady=(0, 6))
        s_entry.bind("<KeyRelease>", lambda _: self._filter_sender())

        self.sender_var = ctk.StringVar()
        self.sender_menu = ctk.CTkOptionMenu(card, variable=self.sender_var, values=["Loading..."],
                                             fg_color=WHITE, text_color=T1, button_color=NAVY,
                                             height=40, corner_radius=8, anchor="w",
                                             command=self._on_sender_select)
        self.sender_menu.pack(fill="x", padx=30)

        self._s_bal = tk.Label(card, text="", bg=WHITE, fg=T2, font=(FONT, 10, "italic"))
        self._s_bal.pack(anchor="w", padx=30, pady=(2, 8))

        tk.Frame(card, bg=BG, height=2).pack(fill="x", padx=30, pady=16)

        # Receiver Section
        tk.Label(card, text="To Account (Receiver)", bg=WHITE, fg=T2, font=(FONT, 11, "bold")).pack(anchor="w", padx=30, pady=(10, 2))
        
        self.r_search = ctk.StringVar()
        r_entry = ctk.CTkEntry(card, textvariable=self.r_search, placeholder_text="🔍  Search receiver (acct no. or name)…",
                               fg_color=WHITE, border_color=GOLD, border_width=1,
                               height=36, corner_radius=8, text_color=T1, placeholder_text_color="#9CA3AF")
        r_entry.pack(fill="x", padx=30, pady=(0, 6))
        r_entry.bind("<KeyRelease>", lambda _: self._filter_recv())

        self.recv_var = ctk.StringVar()
        self.recv_menu = ctk.CTkOptionMenu(card, variable=self.recv_var, values=["Loading..."],
                                           fg_color=WHITE, text_color=T1, button_color=GOLD,
                                           height=40, corner_radius=8, anchor="w",
                                           command=self._on_recv_select)
        self.recv_menu.pack(fill="x", padx=30)

        self._r_bal = tk.Label(card, text="", bg=WHITE, fg=T2, font=(FONT, 10, "italic"))
        self._r_bal.pack(anchor="w", padx=30, pady=(2, 8))

        self._f_amt = self._field(card, "Amount to Transfer (PKR)")

        self._ferr = tk.Label(card, text="", bg=WHITE, font=(FONT, 11))
        self._ferr.pack(pady=(8, 0))

        tk.Button(card, text="Execute Transfer", bg=NAVY, fg=WHITE,
                  font=(FONT, 12, "bold"), bd=0, padx=14, pady=12,
                  cursor="hand2", command=self._transfer).pack(fill="x", padx=30, pady=(12, 24))

    def _field(self, parent, label):
        tk.Label(parent, text=label, bg=WHITE, fg=T2, font=(FONT, 11)).pack(anchor="w", padx=30, pady=(10, 2))
        var = tk.StringVar()
        ctk.CTkEntry(parent, textvariable=var, fg_color=WHITE,
                     border_color=GOLD, border_width=1,
                     height=40, corner_radius=8, text_color=T1).pack(fill="x", padx=30)
        return var

    def refresh(self):
        self.all_accs = self.acc_m.get_all_accounts() or []
        self.acc_data = {f"{a.get('ACCOUNT_NUMBER')} - {a.get('CUSTOMER_NAME')}": a for a in self.all_accs}
        self.s_search.set("")
        self.r_search.set("")
        self._filter_sender()
        self._filter_recv()

    def _filter_sender(self):
        kw = self.s_search.get().strip().lower()
        filtered = [f"{a.get('ACCOUNT_NUMBER')} - {a.get('CUSTOMER_NAME')}" 
                    for a in self.all_accs 
                    if kw in str(a.get("ACCOUNT_NUMBER", "")).lower() or kw in str(a.get("CUSTOMER_NAME", "")).lower()]
        
        if filtered:
            self.sender_menu.configure(values=filtered)
            if self.sender_var.get() not in filtered:
                self.sender_var.set(filtered[0])
            self._on_sender_select(self.sender_var.get())
        else:
            self.sender_menu.configure(values=["No Accounts found"])
            self.sender_var.set("No Accounts found")
            self._s_bal.config(text="")

    def _on_sender_select(self, val):
        a = self.acc_data.get(val)
        if a:
            bal = float(a.get("CURRENT_BALANCE") or 0)
            self._s_bal.config(text=f"Current Balance: PKR {bal:,.2f}")

    def _filter_recv(self):
        kw = self.r_search.get().strip().lower()
        filtered = [f"{a.get('ACCOUNT_NUMBER')} - {a.get('CUSTOMER_NAME')}" 
                    for a in self.all_accs 
                    if kw in str(a.get("ACCOUNT_NUMBER", "")).lower() or kw in str(a.get("CUSTOMER_NAME", "")).lower()]
        
        if filtered:
            self.recv_menu.configure(values=filtered)
            if self.recv_var.get() not in filtered:
                self.recv_var.set(filtered[0])
            self._on_recv_select(self.recv_var.get())
        else:
            self.recv_menu.configure(values=["No Accounts found"])
            self.recv_var.set("No Accounts found")
            self._r_bal.config(text="")

    def _on_recv_select(self, val):
        a = self.acc_data.get(val)
        if a:
            bal = float(a.get("CURRENT_BALANCE") or 0)
            self._r_bal.config(text=f"Current Balance: PKR {bal:,.2f}")

    def _transfer(self):
        if not hasattr(self, 'acc_data') or not self.acc_data: return
        try:
            s_key = self.sender_var.get()
            r_key = self.recv_var.get()
            
            if s_key not in self.acc_data or r_key not in self.acc_data:
                self._ferr.config(text="Please select valid accounts.", fg=RED)
                return
                
            sender = self.acc_data[s_key]
            receiver = self.acc_data[r_key]
            
            s_acc_id = sender.get("ACCOUNT_ID")
            r_acc_num = receiver.get("ACCOUNT_NUMBER")
            
            amt = float(self._f_amt.get().strip() or 0)
            
            if amt <= 0: raise ValueError
            if sender.get("ACCOUNT_ID") == receiver.get("ACCOUNT_ID"):
                self._ferr.config(text="Sender and Receiver cannot be the same.", fg=RED)
                return
            
            ok = self.txn_m.transfer(s_acc_id, self.branch_code, amt, r_acc_num, self.user_data.get("EMPLOYEE_ID"))
            if ok:
                self._ferr.config(text=f"✓ Transfer of PKR {amt:,.2f} successful!", fg=GREEN)
                self._f_amt.set("")
                self.refresh()
                self._show_receipt({
                    "Type": "Funds Transfer",
                    "Amount": f"PKR {amt:,.2f}",
                    "From Account": sender.get("ACCOUNT_NUMBER"),
                    "To Account": receiver.get("ACCOUNT_NUMBER"),
                    "Status": "Successful"
                })
            else:
                self._ferr.config(text="❌ Failed to transfer. Insufficient funds or error.", fg=RED)
        except ValueError:
            self._ferr.config(text="Invalid amount.", fg=RED)
        except Exception as e:
            err_msg = str(e).split('\n')[0]
            self._ferr.config(text=f"❌ {err_msg}", fg=RED)

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