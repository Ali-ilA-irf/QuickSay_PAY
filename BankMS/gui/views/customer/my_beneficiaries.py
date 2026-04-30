import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from gui.models.beneficiary_model import BeneficiaryModel
from gui.models.account_model import AccountModel
from gui.utils.fast_table import make_treeview, populate_tree

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY   = "#0D1B2A"; GOLD = "#E8A020"; BG = "#F0F4F8"; WHITE = "#FFFFFF"
T1     = "#1A1A2E"; T2 = "#6B7280"; RED = "#E74C3C"; GREEN = "#27AE60"
FONT   = "Playfair Display"


class MyBeneficiariesView(ctk.CTkFrame):
    def __init__(self, master, customer_id, **kw):
        super().__init__(master, bg_color=BG, fg_color=BG, **kw)
        self.customer_id = customer_id
        self.ben_m = BeneficiaryModel()
        self.acc_m = AccountModel()
        
        self._build_ui()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=30, pady=(30, 10))
        tk.Label(hdr, text="My Beneficiaries", bg=BG, fg=NAVY, font=(FONT, 22, "bold")).pack(side="left")

        # Split layout: List on Left, Add Form on Right
        main_cont = tk.Frame(self, bg=BG)
        main_cont.pack(fill="both", expand=True, padx=20, pady=10)

        # Left: List
        left = ctk.CTkFrame(main_cont, fg_color=WHITE, corner_radius=12)
        left.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        tk.Label(left, text="Saved Beneficiaries", bg=WHITE, fg=T1, font=(FONT, 14, "bold")).pack(anchor="w", padx=20, pady=(20, 10))
        
        self._tv = make_treeview(left, ["ID", "Name", "IBAN", "Phone"])
        self._tv.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Right: Form
        right = ctk.CTkFrame(main_cont, fg_color=WHITE, corner_radius=12, width=320)
        right.pack(side="right", fill="y", padx=(10, 0))
        right.pack_propagate(False)

        tk.Label(right, text="Add Beneficiary", bg=WHITE, fg=T1, font=(FONT, 14, "bold")).pack(anchor="w", padx=20, pady=(20, 10))
        
        self.v_name = ctk.StringVar()
        self.v_iban = ctk.StringVar()
        self.v_phone = ctk.StringVar()

        self._make_field(right, "Name", self.v_name)
        self._make_field(right, "IBAN", self.v_iban)
        self._make_field(right, "Phone", self.v_phone)

        btn = ctk.CTkButton(right, text="Add Beneficiary", fg_color=NAVY, hover_color=GOLD, 
                            font=(FONT, 14, "bold"), command=self._add_beneficiary)
        btn.pack(fill="x", padx=20, pady=20)

    def _make_field(self, parent, label, var):
        tk.Label(parent, text=label, bg=WHITE, fg=T2, font=(FONT, 11)).pack(anchor="w", padx=20, pady=(10, 2))
        ent = ctk.CTkEntry(parent, textvariable=var, fg_color=BG, text_color=T1, border_width=0, height=36)
        ent.pack(fill="x", padx=20)

    def refresh(self) -> None:
        rows = self.ben_m.get_beneficiaries_by_customer(self.customer_id)
        data = [[r.get("BENEFICIARY_ID",""), r.get("BENEFICIARY_NAME",""), r.get("IBAN",""), r.get("PHONE","")] for r in rows]
        populate_tree(self._tv, data)

    def _add_beneficiary(self):
        name = self.v_name.get().strip()
        iban = self.v_iban.get().strip()
        phone = self.v_phone.get().strip()

        if not (name and iban):
            messagebox.showwarning("Validation", "Name and IBAN are required.")
            return

        if self.ben_m.add_beneficiary(name, phone, iban, self.customer_id):
            messagebox.showinfo("Success", "Beneficiary added successfully!")
            self.v_name.set(""); self.v_iban.set(""); self.v_phone.set("")
            self.refresh()
        else:
            messagebox.showerror("Error", "Failed to add beneficiary.")