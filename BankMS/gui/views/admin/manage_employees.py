import tkinter as tk
import customtkinter as ctk
import tkinter.messagebox as mb
from gui.models.employee_model import EmployeeModel
from gui.models.branch_model import BranchModel
from gui.utils.fast_table import make_treeview, populate_tree

NAVY = "#0D1B2A"; GOLD = "#E8A020"; GOLD_D = "#C8881A"
BG = "#F0F4F8"; WHITE = "#FFFFFF"
T1 = "#1A1A2E"; T2 = "#6B7280"
RED = "#E74C3C"; GREEN = "#27AE60"; FONT = "Segoe UI"


class ManageEmployeesPage(tk.Frame):
    COLS = ["ID", "Username", "Role", "Branch", "Address"]

    def __init__(self, master, **kw):
        super().__init__(master, bg=BG, **kw)
        self.emp_m    = EmployeeModel()
        self.branch_m = BranchModel()
        self._all_rows  = []
        self._selected  = None
        self._mode      = "add"
        self._form_open = False

        self._build_toolbar()
        self._build_table()
        self._build_form_panel()
        self.refresh()

    # ── Toolbar ───────────────────────────────────────────────
    def _build_toolbar(self):
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=20, pady=(16, 8))

        self._sv = tk.StringVar()
        e = ctk.CTkEntry(bar, placeholder_text="🔍  Search username, role or branch…",
                         textvariable=self._sv, fg_color=WHITE,
                         border_color=GOLD, border_width=1,
                         text_color=T1, placeholder_text_color="#9CA3AF", height=36, corner_radius=8)
        e.pack(side="left", fill="x", expand=True)
        e.bind("<KeyRelease>", lambda _: self._do_search())

        for text, cmd, bg in [
            ("↺ Refresh",     self.refresh,        WHITE),
            ("+ Add Employee", self._open_add, NAVY),
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
        self._edit_btn = tk.Button(btn_row, text="✎ Edit",
                                   command=self._open_edit,
                                   bg=WHITE, fg=NAVY, font=(FONT, 11),
                                   bd=1, padx=14, pady=6, cursor="hand2",
                                   state="disabled")
        self._edit_btn.pack(side="left", padx=(0, 8))
        self._del_btn  = tk.Button(btn_row, text="🗑 Delete",
                                   command=self._delete_sel,
                                   bg=WHITE, fg=RED, font=(FONT, 11),
                                   bd=1, padx=14, pady=6, cursor="hand2",
                                   state="disabled")
        self._del_btn.pack(side="left")

    # ── Form panel ────────────────────────────────────────────
    def _build_form_panel(self):
        self._fp = tk.Frame(self, bg=WHITE, width=390)
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

        # Fields
        self._f_user = self._field(body, "Username")
        self._f_pass = self._field(body, "Password", show="●")

        tk.Label(body, text="Role", bg=WHITE, fg=T2,
                 font=(FONT, 11)).pack(anchor="w", pady=(10, 2))
        self._f_role = ctk.CTkComboBox(
            body, values=["ADMIN", "MANAGER", "TELLER"],
            fg_color=WHITE, border_color=GOLD, button_color=GOLD,
            height=36, corner_radius=8, text_color=T1)
        self._f_role.pack(fill="x")

        tk.Label(body, text="Branch Code", bg=WHITE, fg=T2,
                 font=(FONT, 11)).pack(anchor="w", pady=(10, 2))
        self._f_branch = ctk.CTkComboBox(
            body, values=self.branch_m.get_branch_codes() or ["—"],
            fg_color=WHITE, border_color=GOLD, button_color=GOLD,
            height=36, corner_radius=8, text_color=T1)
        self._f_branch.pack(fill="x")

        self._ferr = tk.Label(body, text="", bg=WHITE, fg=RED,
                              font=(FONT, 10), wraplength=330)
        self._ferr.pack(pady=(8, 0))

        tk.Button(body, text="💾  Save", bg=GOLD, fg=NAVY,
                  font=(FONT, 12, "bold"), bd=0, padx=14, pady=10,
                  cursor="hand2", activebackground=GOLD_D,
                  command=self._save).pack(fill="x", pady=(12, 0))

    def _field(self, parent, label, show=""):
        tk.Label(parent, text=label, bg=WHITE, fg=T2,
                 font=(FONT, 11)).pack(anchor="w", pady=(10, 2))
        var = tk.StringVar()
        ctk.CTkEntry(parent, textvariable=var, show=show,
                     fg_color=WHITE, border_color=GOLD, border_width=1,
                     height=36, corner_radius=8,
                     text_color=T1).pack(fill="x")
        return var

    # ── Data ──────────────────────────────────────────────────
    def refresh(self):
        self._all_rows = self.emp_m.get_all_employees()
        self._sv.set("")
        self._render(self._all_rows)
        self._set_actions(False)

    def _do_search(self):
        kw = self._sv.get().strip().lower()
        data = [r for r in self._all_rows
                if not kw
                or kw in str(r.get("USERNAME","")).lower()
                or kw in str(r.get("ROLE","")).lower()
                or kw in str(r.get("BRANCH_CODE","")).lower()]
        self._render(data)

    def _render(self, rows):
        populate_tree(self._tv, [
            [r.get("EMPLOYEE_ID",""), r.get("USERNAME",""),
             r.get("ROLE",""), r.get("BRANCH_CODE",""),
             r.get("BRANCH_ADDRESS","")]
            for r in rows])

    def _on_sel(self, _=None):
        sel = self._tv.selection()
        if sel:
            self._selected = self._tv.item(sel[0])["values"][0]
            self._set_actions(True)
        else:
            self._set_actions(False)

    def _set_actions(self, on: bool):
        s = "normal" if on else "disabled"
        self._edit_btn.config(state=s)
        self._del_btn.config(state=s)
        if not on:
            self._selected = None

    # ── Form open/close ───────────────────────────────────────
    def _open_add(self):
        self._mode = "add"
        self._ftitle.config(text="Add Employee")
        self._f_user.set(""); self._f_pass.set("")
        self._f_role.set("TELLER")
        codes = self.branch_m.get_branch_codes()
        self._f_branch.set(codes[0] if codes else "")
        self._ferr.config(text="")
        self._show_form()

    def _open_edit(self):
        row = next((r for r in self._all_rows
                    if str(r.get("EMPLOYEE_ID","")) == str(self._selected)), None)
        if not row:
            return
        self._mode = "edit"
        self._ftitle.config(text="Edit Employee")
        self._f_user.set(str(row.get("USERNAME","")))
        self._f_pass.set("")
        self._f_role.set(str(row.get("ROLE","")))
        self._f_branch.set(str(row.get("BRANCH_CODE","")))
        self._ferr.config(text="")
        self._show_form()

    def _show_form(self):
        self.update_idletasks()
        w = self.winfo_width() or 900
        self._fp.place(x=w, y=0, width=390, relheight=1.0)
        self._fp.lift()
        self._slide(w, w - 390)

    def _close_form(self):
        self.update_idletasks()
        w = self.winfo_width() or 900
        self._slide(w - 390, w, closing=True)

    def _slide(self, x, target, closing=False, step=40):
        going = x > target if not closing else x < target
        if going:
            x = (max if closing else min)(x + (step if closing else -step), target)
            self._fp.place(x=x)
            self.after(8, lambda: self._slide(x, target, closing, step))
        elif closing:
            self._fp.place_forget()

    # ── Save / Delete ─────────────────────────────────────────
    def _save(self):
        u = self._f_user.get().strip()
        p = self._f_pass.get().strip()
        r = self._f_role.get().strip()
        b = self._f_branch.get().strip()
        if not u or not r or not b:
            self._ferr.config(text="Username, Role and Branch are required.")
            return
        if self._mode == "add":
            if not p:
                self._ferr.config(text="Password is required.")
                return
            ok = self.emp_m.create_employee(u, p, r, b)
        else:
            ok = self.emp_m.update_employee(int(self._selected), r, b)
        if ok:
            self._close_form()
            self.refresh()
        else:
            self._ferr.config(text="❌ Operation failed. Check console.")

    def _delete_sel(self):
        if not self._selected:
            return
        if mb.askyesno("Confirm", f"Delete employee ID {self._selected}?"):
            if self.emp_m.delete_employee(int(self._selected)):
                self.refresh()