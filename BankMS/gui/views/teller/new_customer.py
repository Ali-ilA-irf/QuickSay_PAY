import tkinter as tk
import customtkinter as ctk
from gui.models.customer_model import CustomerModel

NAVY = "#0D1B2A"; GOLD = "#E8A020"; BG = "#F0F4F8"; WHITE = "#FFFFFF"
T1 = "#1A1A2E"; T2 = "#6B7280"; GREEN = "#27AE60"; RED = "#E74C3C"
FONT = "Segoe UI"


class NewCustomerPage(tk.Frame):
    def __init__(self, master, user_data: dict, **kw):
        super().__init__(master, bg=BG, **kw)
        self.user_data = user_data
        self.cust_m = CustomerModel()
        self._build_ui()

    def _build_ui(self):
        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12)
        card.pack(fill="both", expand=True, padx=80, pady=80)
        
        tk.Label(card, text="👤 Register New Customer", bg=WHITE, fg=NAVY,
                 font=(FONT, 16, "bold")).pack(pady=(24, 16))

        self._f_name = self._field(card, "Full Name")
        self._f_addr = self._field(card, "Address")
        self._f_phone = self._field(card, "Phone Number")
        self._f_pass = self._field(card, "Login Password")

        self._ferr = tk.Label(card, text="", bg=WHITE, font=(FONT, 11))
        self._ferr.pack(pady=(8, 0))

        tk.Button(card, text="Register Customer", bg=GOLD, fg=NAVY,
                  font=(FONT, 12, "bold"), bd=0, padx=14, pady=12,
                  cursor="hand2", command=self._save).pack(fill="x", padx=30, pady=(12, 24))

    def _field(self, parent, label):
        tk.Label(parent, text=label, bg=WHITE, fg=T2, font=(FONT, 11)).pack(anchor="w", padx=30, pady=(10, 2))
        var = tk.StringVar()
        show = "●" if "Password" in label else ""
        ctk.CTkEntry(parent, textvariable=var, fg_color=WHITE,
                     placeholder_text=f"Enter {label.lower()}…",
                     show=show,
                     border_color=GOLD, border_width=1,
                     placeholder_text_color="#9CA3AF",
                     height=40, corner_radius=8, text_color=T1).pack(fill="x", padx=30)
        return var

    def _save(self):
        name = self._f_name.get().strip()
        addr = self._f_addr.get().strip()
        phone = self._f_phone.get().strip()
        pwd = self._f_pass.get().strip()
        
        if not name or not phone or not pwd:
            self._ferr.config(text="Name, Phone, and Password are required.", fg=RED)
            return
            
        if self.cust_m.create_customer(name, addr, phone, pwd, self.user_data.get("EMPLOYEE_ID")):
            self._ferr.config(text="✓ Customer registered successfully!", fg=GREEN)
            for v in (self._f_name, self._f_addr, self._f_phone, self._f_pass): v.set("")
        else:
            self._ferr.config(text="❌ Failed to register. Check console.", fg=RED)