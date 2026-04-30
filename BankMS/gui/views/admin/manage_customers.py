import tkinter as tk
import customtkinter as ctk
from gui.models.customer_model import CustomerModel
from gui.utils.fast_table import make_treeview, populate_tree

NAVY = "#0D1B2A"; GOLD = "#E8A020"; GOLD_D = "#C8881A"
BG = "#F0F4F8"; WHITE = "#FFFFFF"
T1 = "#1A1A2E"; T2 = "#6B7280"; RED = "#E74C3C"; FONT = "Segoe UI"


class ManageCustomersPage(tk.Frame):
    COLS = ["ID", "Name", "Address", "Phone", "Created On"]

    def __init__(self, master, **kw):
        super().__init__(master, bg=BG, **kw)
        self.cust_m    = CustomerModel()
        self._all_rows = []
        self._selected = None
        self._mode     = "add"
        self._build_toolbar()
        self._build_table()
        self._build_form_panel()
        self.refresh()

    def _build_toolbar(self):
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=20, pady=(16, 8))
        self._sv = tk.StringVar()
        e = ctk.CTkEntry(bar, placeholder_text="🔍  Search name or phone…",
                         textvariable=self._sv, fg_color=WHITE,
                         border_color=GOLD, border_width=1,
                         text_color=T1, placeholder_text_color="#9CA3AF", height=36, corner_radius=8)
        e.pack(side="left", fill="x", expand=True)
        e.bind("<KeyRelease>", lambda _: self._do_search())
        for text, cmd, bg in [
            ("↺ Refresh",     self.refresh,   WHITE),
            ("+ Add Customer", self._open_add, NAVY),
        ]:
            fg = T1 if bg == WHITE else WHITE
            tk.Button(bar, text=text, command=cmd, bg=bg, fg=fg,
                      font=(FONT, 11, "bold"), bd=0, padx=14, pady=8,
                      cursor="hand2").pack(side="left", padx=(6, 0))

    def _build_table(self):
        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12)
        card.pack(fill="both", expand=True, padx=20, pady=(4, 4))
        self._tv = make_treeview(card, self.COLS)
        self._tv.bind("<<TreeviewSelect>>", self._on_sel)
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=20, pady=(4, 16))
        self._edit_btn = tk.Button(btn_row, text="✎ Edit",
                                   command=self._open_edit,
                                   bg=WHITE, fg=NAVY, font=(FONT, 11),
                                   bd=1, padx=14, pady=6, cursor="hand2",
                                   state="disabled")
        self._edit_btn.pack(side="left")

    def _build_form_panel(self):
        self._fp = tk.Frame(self, bg=WHITE, width=370)
        hdr = tk.Frame(self._fp, bg=NAVY, height=52)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        self._ftitle = tk.Label(hdr, text="", bg=NAVY, fg=WHITE,
                                font=(FONT, 13, "bold"))
        self._ftitle.pack(side="left", padx=16)
        tk.Button(hdr, text="✕", bg=NAVY, fg=WHITE, bd=0,
                  font=(FONT, 13), cursor="hand2",
                  command=self._close_form).pack(side="right", padx=12)

        body = tk.Frame(self._fp, bg=WHITE)
        body.pack(fill="both", expand=True, padx=20, pady=14)

        self._f_name  = self._field(body, "Full Name")
        self._f_addr  = self._field(body, "Address")
        self._f_phone = self._field(body, "Phone")
        self._f_pass  = self._field(body, "Password")

        self._ferr = tk.Label(body, text="", bg=WHITE, fg=RED,
                              font=(FONT, 10), wraplength=310)
        self._ferr.pack(pady=(8, 0))
        tk.Button(body, text="💾  Save", bg=GOLD, fg=NAVY,
                  font=(FONT, 12, "bold"), bd=0, padx=14, pady=10,
                  cursor="hand2", activebackground=GOLD_D,
                  command=self._save).pack(fill="x", pady=(12, 0))

    def _field(self, parent, label):
        tk.Label(parent, text=label, bg=WHITE, fg=T2,
                 font=(FONT, 11)).pack(anchor="w", pady=(10, 2))
        var = tk.StringVar()
        show = "●" if label == "Password" else ""
        ctk.CTkEntry(parent, textvariable=var, fg_color=WHITE,
                     show=show,
                     border_color=GOLD, border_width=1,
                     height=36, corner_radius=8,
                     text_color=T1).pack(fill="x")
        return var

    def refresh(self):
        self._all_rows = self.cust_m.get_all_customers()
        self._sv.set("")
        self._render(self._all_rows)
        self._selected = None
        self._edit_btn.config(state="disabled")

    def _do_search(self):
        kw = self._sv.get().strip().lower()
        data = [r for r in self._all_rows
                if not kw
                or kw in str(r.get("CUSTOMER_NAME","")).lower()
                or kw in str(r.get("PHONE","")).lower()]
        self._render(data)

    def _render(self, rows):
        populate_tree(self._tv, [
            [r.get("CUSTOMER_ID",""), r.get("CUSTOMER_NAME",""),
             r.get("CUSTOMER_ADDRESS",""), r.get("PHONE",""),
             r.get("CREATED_ON","")]
            for r in rows])

    def _on_sel(self, _=None):
        sel = self._tv.selection()
        if sel:
            self._selected = self._tv.item(sel[0])["values"][0]
            self._edit_btn.config(state="normal")
        else:
            self._selected = None
            self._edit_btn.config(state="disabled")

    def _open_add(self):
        self._mode = "add"
        self._ftitle.config(text="Add Customer")
        for v in (self._f_name, self._f_addr, self._f_phone, self._f_pass):
            v.set("")
        self._ferr.config(text="")
        self._show_form()

    def _open_edit(self):
        row = next((r for r in self._all_rows
                    if str(r.get("CUSTOMER_ID","")) == str(self._selected)), None)
        if not row:
            return
        self._mode = "edit"
        self._ftitle.config(text="Edit Customer")
        self._f_name.set(str(row.get("CUSTOMER_NAME","")))
        self._f_addr.set(str(row.get("CUSTOMER_ADDRESS","")))
        self._f_phone.set(str(row.get("PHONE","")))
        self._f_pass.set("") # Clear password on edit for security
        self._ferr.config(text="")
        self._show_form()

    def _show_form(self):
        self.update_idletasks()
        w = self.winfo_width() or 900
        self._fp.place(x=w, y=0, width=370, relheight=1.0)
        self._fp.lift()
        self._slide(w, w - 370)

    def _close_form(self):
        self.update_idletasks()
        w = self.winfo_width() or 900
        self._slide(w - 370, w, closing=True)

    def _slide(self, x, target, closing=False, step=40):
        going = (x > target) if not closing else (x < target)
        if going:
            x = (min if not closing else max)(x + (-step if not closing else step), target)
            self._fp.place(x=x)
            self.after(8, lambda: self._slide(x, target, closing, step))
        elif closing:
            self._fp.place_forget()

    def _save(self):
        name  = self._f_name.get().strip()
        addr  = self._f_addr.get().strip()
        phone = self._f_phone.get().strip()
        pwd   = self._f_pass.get().strip()
        
        if not name or not phone:
            self._ferr.config(text="Name and Phone are required.")
            return
        if self._mode == "add":
            if not pwd:
                self._ferr.config(text="Password is required for new customers.")
                return
            ok = self.cust_m.create_customer(name, addr, phone, pwd)
        else:
            # Edit customer doesn't change password in this view for simplicity
            ok = self.cust_m.update_customer(int(self._selected), name, addr, phone)
        if ok:
            self._close_form()
            self.refresh()
        else:
            self._ferr.config(text="❌ Operation failed. Check console.")