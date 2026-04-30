import tkinter as tk
import customtkinter as ctk
from gui.models.audit_model import AuditModel
from gui.utils.fast_table import make_treeview, populate_tree

NAVY = "#0D1B2A"; GOLD = "#E8A020"
BG = "#F0F4F8"; WHITE = "#FFFFFF"
T1 = "#1A1A2E"; T2 = "#6B7280"; FONT = "Segoe UI"


class AuditLogsView(tk.Frame):
    """View system audit logs."""
    COLS = ["Log ID", "Description", "Timestamp", "Employee Name", "Role", "Branch"]

    def __init__(self, master, **kw):
        super().__init__(master, bg=BG, **kw)
        self.aud_m = AuditModel()
        self._all_rows = []
        self._build_toolbar()
        self._build_table()
        self.refresh()

    def _build_toolbar(self):
        # We wrap the search bars in a frame that matches the table's horizontal alignment
        bar = tk.Frame(self, bg=BG)
        bar.pack(fill="x", padx=20, pady=(16, 0))
        
        self.sv_id = tk.StringVar()
        self.sv_desc = tk.StringVar()
        self.sv_ts = tk.StringVar()
        self.sv_emp = tk.StringVar()
        self.sv_role = tk.StringVar()
        self.sv_branch = tk.StringVar()

        r1 = tk.Frame(bar, bg=BG)
        r1.pack(fill="x")
        
        def on_type(_): self._do_search()

        # ID (matches width 80)
        e_id = ctk.CTkEntry(r1, placeholder_text="ID", textvariable=self.sv_id, width=80, 
                           fg_color=WHITE, text_color=T1, placeholder_text_color="#9CA3AF",
                           border_color=GOLD, border_width=1)
        e_id.pack(side="left", padx=(0, 4))
        e_id.bind("<KeyRelease>", on_type)
        
        # Description (matches width 400, stretch)
        e_desc = ctk.CTkEntry(r1, placeholder_text="Search Description...", textvariable=self.sv_desc, 
                              width=400, fg_color=WHITE, text_color=T1, placeholder_text_color="#9CA3AF",
                              border_color=GOLD, border_width=1)
        e_desc.pack(side="left", fill="x", expand=True, padx=4)
        e_desc.bind("<KeyRelease>", on_type)

        # Timestamp (matches width 150)
        e_ts = ctk.CTkEntry(r1, placeholder_text="Date...", textvariable=self.sv_ts, width=150, 
                            fg_color=WHITE, text_color=T1, placeholder_text_color="#9CA3AF",
                            border_color=GOLD, border_width=1)
        e_ts.pack(side="left", padx=4)
        e_ts.bind("<KeyRelease>", on_type)
        
        # Employee (matches width 150, stretch)
        e_emp = ctk.CTkEntry(r1, placeholder_text="Employee...", textvariable=self.sv_emp, width=150, 
                             fg_color=WHITE, text_color=T1, placeholder_text_color="#9CA3AF",
                             border_color=GOLD, border_width=1)
        e_emp.pack(side="left", fill="x", expand=True, padx=4)
        e_emp.bind("<KeyRelease>", on_type)
        
        # Role (matches width 100)
        e_role = ctk.CTkEntry(r1, placeholder_text="Role", textvariable=self.sv_role, width=100, 
                              fg_color=WHITE, text_color=T1, placeholder_text_color="#9CA3AF",
                              border_color=GOLD, border_width=1)
        e_role.pack(side="left", padx=4)
        e_role.bind("<KeyRelease>", on_type)
        
        # Branch (matches width 100)
        e_branch = ctk.CTkEntry(r1, placeholder_text="Branch", textvariable=self.sv_branch, width=100, 
                                fg_color=WHITE, text_color=T1, placeholder_text_color="#9CA3AF",
                                border_color=GOLD, border_width=1)
        e_branch.pack(side="left", padx=4)
        e_branch.bind("<KeyRelease>", on_type)

        tk.Button(r1, text="↺", command=self.refresh,
                  bg=WHITE, fg=T1, font=(FONT, 11, "bold"),
                  bd=0, padx=8, pady=4, cursor="hand2").pack(side="right", padx=(8, 0))

    def _build_table(self):
        card = ctk.CTkFrame(self, fg_color=WHITE, corner_radius=12)
        card.pack(fill="both", expand=True, padx=20, pady=(4, 20))
        self._tv = make_treeview(card, self.COLS)
        self._tv.column("Log ID", width=80, stretch=False)
        self._tv.column("Description", width=400, stretch=True)
        self._tv.column("Timestamp", width=150, stretch=False)
        self._tv.column("Employee Name", width=150, stretch=True)
        self._tv.column("Role", width=100, stretch=False)
        self._tv.column("Branch", width=100, stretch=False)

    def refresh(self):
        self._all_rows = self.aud_m.get_all_logs() or []
        for v in (self.sv_id, self.sv_desc, self.sv_ts, self.sv_emp, self.sv_role, self.sv_branch):
            v.set("")
        self._render(self._all_rows)

    def _do_search(self):
        i = self.sv_id.get().strip().lower()
        d = self.sv_desc.get().strip().lower()
        t = self.sv_ts.get().strip().lower()
        e = self.sv_emp.get().strip().lower()
        r = self.sv_role.get().strip().lower()
        b = self.sv_branch.get().strip().lower()

        data = [row for row in self._all_rows
                if (not i or i in str(row.get("LOG_ID","")).lower())
                and (not d or d in str(row.get("DESCRIPTION","")).lower())
                and (not t or t in str(row.get("LOG_TIMESTAMP","") or row.get("TIMESTAMP","")).lower())
                and (not e or e in str(row.get("EMPLOYEE_NAME","")).lower())
                and (not r or r in str(row.get("ROLE","")).lower())
                and (not b or b in str(row.get("BRANCH_CODE","")).lower())]
        self._render(data)

    def _render(self, rows):
        populate_tree(self._tv, [
            [r.get("LOG_ID",""),
             r.get("DESCRIPTION",""),
             r.get("LOG_TIMESTAMP","") or r.get("TIMESTAMP",""),
             r.get("EMPLOYEE_NAME",""),
             r.get("ROLE",""),
             r.get("BRANCH_CODE","")]
            for r in rows])