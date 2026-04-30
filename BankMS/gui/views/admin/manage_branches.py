import tkinter as tk
import customtkinter as ctk
import tkinter.messagebox as mb
from gui.models.branch_model import BranchModel
from gui.utils.fast_table import make_treeview, populate_tree

NAVY = "#0D1B2A"; GOLD = "#E8A020"; GOLD_D = "#C8881A"
BG = "#F0F4F8"; WHITE = "#FFFFFF"
T1 = "#1A1A2E"; T2 = "#6B7280"
RED = "#E74C3C"; FONT = "Segoe UI"


class ManageBranchesPage(tk.Frame):
    COLS = ["Branch Code", "Address", "Phone", "Created On",
            "Employees", "Accounts", "Total Balance"]

    def __init__(self, master, **kw):
        super().__init__(master, bg=BG, **kw)
        self.branch_m  = BranchModel()
        self._all_rows = []
        self._selected = None
        self._build_toolbar()
        self._build_table()
        self._build_form_panel()
        self.refresh()

    # ── Toolbar ───────────────────────────────────────────────
    def _build_toolbar(self):
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=20, pady=(16, 8))
        self._sv = tk.StringVar()
        e = ctk.CTkEntry(bar, placeholder_text="🔍  Search branch code or address…",
                         textvariable=self._sv, fg_color=WHITE,
                         border_color=GOLD, border_width=1,
                         text_color=T1, placeholder_text_color="#9CA3AF", height=36, corner_radius=8)
        e.pack(side="left", fill="x", expand=True)
        e.bind("<KeyRelease>", lambda _: self._do_search())
        for text, cmd, bg in [
            ("↺ Refresh",   self.refresh,   WHITE),
            ("+ Add Branch", self._open_add, NAVY),
        ]:
            fg = T1 if bg == WHITE else WHITE
            tk.Button(bar, text=text, command=cmd, bg=bg, fg=fg,
                      font=(FONT, 11, "bold"), bd=0, padx=14, pady=8,
                      cursor="hand2").pack(side="left", padx=(6, 0))

    # ── Table ─────────────────────────────────────────────────
    def _build_table(self):
        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12)
        card.pack(fill="both", expand=True, padx=20, pady=(4, 4))
        self._tv = make_treeview(card, self.COLS)
        self._tv.bind("<<TreeviewSelect>>", self._on_sel)
        btn_row = tk.Frame(self, bg=BG)
        btn_row.pack(fill="x", padx=20, pady=(4, 16))
        self._del_btn = tk.Button(btn_row, text="🗑 Delete Selected",
                                  command=self._delete_sel,
                                  bg=WHITE, fg=RED, font=(FONT, 11),
                                  bd=1, padx=14, pady=6, cursor="hand2",
                                  state="disabled")
        self._del_btn.pack(side="left")

    # ── Form ──────────────────────────────────────────────────
    def _build_form_panel(self):
        self._fp = tk.Frame(self, bg=WHITE, width=370)
        hdr = tk.Frame(self._fp, bg=NAVY, height=52)
        hdr.pack(fill="x"); hdr.pack_propagate(False)
        tk.Label(hdr, text="Add Branch", bg=NAVY, fg=WHITE,
                 font=(FONT, 13, "bold")).pack(side="left", padx=16)
        tk.Button(hdr, text="✕", bg=NAVY, fg=WHITE, bd=0,
                  font=(FONT, 13), cursor="hand2",
                  command=self._close_form).pack(side="right", padx=12)

        body = tk.Frame(self._fp, bg=WHITE)
        body.pack(fill="both", expand=True, padx=20, pady=14)

        self._f_code  = self._field(body, "Branch Code")
        self._f_addr  = self._field(body, "Address")
        self._f_phone = self._field(body, "Phone")

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
        ctk.CTkEntry(parent, textvariable=var, fg_color=WHITE,
                     border_color=GOLD, border_width=1,
                     height=36, corner_radius=8,
                     text_color=T1).pack(fill="x")
        return var

    # ── Data ──────────────────────────────────────────────────
    def refresh(self):
        # Use vw_branch_summary for richer data
        from gui.db_connection import DatabaseConnection
        db = DatabaseConnection()
        rows = db.execute_query("SELECT * FROM vw_branch_summary") or []
        # also get created_on from vw_branch_details
        details = {r["BRANCH_CODE"]: r for r in
                   (db.execute_query("SELECT * FROM vw_branch_details") or [])}
        self._all_rows = rows
        self._sv.set("")
        self._render(rows, details)
        self._del_btn.config(state="disabled")
        self._selected = None

    def _do_search(self):
        kw = self._sv.get().strip().lower()
        data = [r for r in self._all_rows
                if not kw
                or kw in str(r.get("BRANCH_CODE","")).lower()
                or kw in str(r.get("BRANCH_ADDRESS","")).lower()]
        self._render(data, {})

    def _render(self, rows, details=None):
        details = details or {}
        populate_tree(self._tv, [
            [r.get("BRANCH_CODE",""),
             r.get("BRANCH_ADDRESS",""),
             details.get(r.get("BRANCH_CODE",""), {}).get("PHONE","—"),
             details.get(r.get("BRANCH_CODE",""), {}).get("CREATED_ON","—"),
             r.get("TOTAL_EMPLOYEES", 0),
             r.get("TOTAL_ACCOUNTS", 0),
             f"PKR {float(r.get('TOTAL_DEPOSITS') or 0):,.2f}"]
            for r in rows])

    def _on_sel(self, _=None):
        sel = self._tv.selection()
        if sel:
            self._selected = self._tv.item(sel[0])["values"][0]
            self._del_btn.config(state="normal")
        else:
            self._selected = None
            self._del_btn.config(state="disabled")

    def _open_add(self):
        for v in (self._f_code, self._f_addr, self._f_phone):
            v.set("")
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
        code  = self._f_code.get().strip().upper()
        addr  = self._f_addr.get().strip()
        phone = self._f_phone.get().strip()
        if not code or not addr:
            self._ferr.config(text="Branch Code and Address are required.")
            return
        ok = self.branch_m.create_branch(code, addr, phone)
        if ok:
            self._close_form()
            self.refresh()
        else:
            self._ferr.config(text="❌ Failed. Branch code may already exist.")

    def _delete_sel(self):
        if not self._selected:
            return
        if mb.askyesno("Confirm", f"Delete branch '{self._selected}'?\n"
                       "This will fail if employees or accounts are linked to it."):
            if self.branch_m.delete_branch(str(self._selected)):
                self.refresh()
            else:
                mb.showerror("Error", "Cannot delete — branch has linked records.")