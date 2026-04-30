import tkinter as tk
import tkinter.ttk as ttk
import customtkinter as ctk
import threading
from gui.utils.fast_table import make_treeview, populate_tree

# ── Palette (Admin Palette Style) ──────────────────────────────────────────
NAVY   = "#0D1B2A"; NAVY2  = "#162534"; HOVER  = "#1A2B3C"
GOLD   = "#E8A020"; GOLD_D = "#C8881A"
BG     = "#F0F4F8"; WHITE  = "#FFFFFF"; BORDER = "#E2E8F0"
T1     = "#1A1A2E"; T2     = "#6B7280"
GREEN  = "#27AE60"; RED    = "#E74C3C"
FONT   = "Playfair Display"


class CustomerDashboard(tk.Frame):
    SIDEBAR_W = 240

    def __init__(self, master, user_data, logout_cb, **kw):
        super().__init__(master, bg=BG, **kw)
        self.user_data = user_data
        self.logout_cb = logout_cb
        self.customer_id = user_data.get("USER_ID")
        self._active = "Dashboard"
        self._nav_items = {}
        self._pages = {}

        self._build_layout()
        self._build_all_pages()
        self._switch("Dashboard")
        self._animate_sidebar_in()

    def _build_layout(self):
        # Sidebar
        self.sidebar = tk.Frame(self, bg=NAVY, width=1)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Brand Area
        brand = tk.Frame(self.sidebar, bg=NAVY, height=70)
        brand.pack(fill="x", pady=(20, 0))
        tk.Label(brand, text="QuickSay Pay", bg=NAVY, fg=GOLD, font=(FONT, 18, "bold")).pack()
        tk.Label(brand, text="Apke Dill Mein Hmara Account", bg=NAVY, fg=T2, font=(FONT, 8, "italic")).pack()

        # Profile Header
        hdr = tk.Frame(self.sidebar, bg=NAVY, height=120)
        hdr.pack(fill="x", pady=(10,0))
        hdr.pack_propagate(False)
        
        av = tk.Canvas(hdr, width=54, height=54, bg=NAVY, highlightthickness=0)
        av.place(relx=0.5, y=40, anchor="center")
        av.create_oval(2, 2, 52, 52, fill=GOLD, outline="")
        init = self.user_data.get("USERNAME", "C")[:2].upper()
        av.create_text(27, 27, text=init, fill=NAVY, font=(FONT, 16, "bold"))
        
        tk.Label(hdr, text=f"Hello, {self.user_data.get('DISPLAY_NAME', 'Customer')}", 
                 bg=NAVY, fg=WHITE, font=(FONT, 12, "bold")).place(relx=0.5, y=85, anchor="center")
        tk.Label(hdr, text="Valued Member", 
                 bg=NAVY, fg=GOLD, font=(FONT, 9)).place(relx=0.5, y=105, anchor="center")

        tk.Frame(self.sidebar, bg=NAVY2, height=1).pack(fill="x", padx=20, pady=10)

        # Navigation
        self.nav_cont = tk.Frame(self.sidebar, bg=NAVY)
        self.nav_cont.pack(fill="both", expand=True, pady=10)

        nav_items = [
            ("Dashboard", "📊"),
            ("My Accounts", "🏦"),
            ("Transactions", "🔄"),
            ("Loans", "💰"),
            ("Cards", "💳"),
            ("Beneficiaries", "👥")
        ]
        for name, icon in nav_items:
            self._add_nav_item(name, icon)

        # Bottom Actions
        bot = tk.Frame(self.sidebar, bg=NAVY)
        bot.pack(fill="x", side="bottom", pady=20)
        
        tk.Button(bot, text="⚙ Settings", bg=NAVY, fg=T2, bd=0, 
                  font=(FONT, 11), activebackground=NAVY, activeforeground=WHITE, 
                  cursor="hand2").pack(anchor="w", padx=24, pady=4)
        
        tk.Button(bot, text="⎋ Logout", bg=NAVY, fg=RED, bd=0, 
                  font=(FONT, 11), activebackground=NAVY, activeforeground=WHITE, 
                  cursor="hand2", command=self.logout_cb).pack(anchor="w", padx=24, pady=4)

        # Content Area
        self.content = tk.Frame(self, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        # Top Bar
        bar = tk.Frame(self.content, bg=WHITE, height=64)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Frame(bar, bg=BORDER, height=1).pack(side="bottom", fill="x")
        
        self._title_lbl = tk.Label(bar, text="Dashboard", bg=WHITE, fg=T1, font=(FONT, 17, "bold"))
        self._title_lbl.pack(side="left", padx=22)
        
        # Page Container
        self.pg_container = tk.Frame(self.content, bg=BG)
        self.pg_container.pack(fill="both", expand=True)

    def _add_nav_item(self, name, icon):
        row = tk.Frame(self.nav_cont, bg=NAVY, height=48)
        row.pack(fill="x", pady=2)
        row.pack_propagate(False)
        stripe = tk.Frame(row, bg=GOLD, width=4)
        lbl = tk.Label(row, text=f"{icon}   {name}", bg=NAVY, fg=WHITE, font=(FONT, 12))
        lbl.pack(side="left", padx=24)
        
        for w in (row, lbl):
            w.bind("<Enter>", lambda e: self._hover_on(name))
            w.bind("<Leave>", lambda e: self._hover_off(name))
            w.bind("<Button-1>", lambda e: self._switch(name))
            
        self._nav_items[name] = (row, stripe, lbl)

    def _hover_on(self, name):
        if self._active != name:
            r, _, l = self._nav_items[name]
            r.config(bg=HOVER); l.config(bg=HOVER)

    def _hover_off(self, name):
        if self._active != name:
            r, _, l = self._nav_items[name]
            r.config(bg=NAVY); l.config(bg=NAVY)

    def _animate_sidebar_in(self, w=1):
        if w < self.SIDEBAR_W:
            nw = min(w + 30, self.SIDEBAR_W)
            self.sidebar.configure(width=nw)
            self.after(8, lambda: self._animate_sidebar_in(nw))

    def _switch(self, name):
        if self._active in self._nav_items:
            row, stripe, lbl = self._nav_items[self._active]
            stripe.pack_forget()
            row.config(bg=NAVY); lbl.config(bg=NAVY, fg=WHITE)
        
        self._active = name
        if name in self._nav_items:
            row, stripe, lbl = self._nav_items[name]
            stripe.pack(side="left", fill="y")
            row.config(bg=NAVY2); lbl.config(bg=NAVY2, fg=GOLD)
            
        self._title_lbl.config(text=name)

        for pname, pg in self._pages.items():
            if pname == name:
                pg.pack(fill="both", expand=True)
                if hasattr(pg, "refresh"):
                    self.after(0, pg.refresh)
            else:
                pg.pack_forget()

    def refresh_all(self):
        """Triggers a refresh on all cached pages that have a refresh() method."""
        for name, pg in self._pages.items():
            if hasattr(pg, "refresh"):
                self.after(0, pg.refresh)

    def _build_all_pages(self):

        from gui.views.customer.dashboard_customer import CustomerHomePage
        from gui.views.customer.my_accounts import MyAccountsPage
        from gui.views.customer.my_transactions import MyTransactionsPage
        from gui.views.customer.my_loans import MyLoansPage
        from gui.views.customer.my_cards import MyCardsView

        from gui.views.customer.my_beneficiaries import MyBeneficiariesView

        self._pages["Dashboard"]     = CustomerHomePage(self.pg_container, self.customer_id, self.user_data)
        self._pages["My Accounts"]   = MyAccountsPage(self.pg_container, self.customer_id)
        self._pages["Transactions"]  = MyTransactionsPage(self.pg_container, self.customer_id)
        self._pages["Loans"]         = MyLoansPage(self.pg_container, self.customer_id)
        self._pages["Cards"]         = MyCardsView(self.pg_container, self.customer_id)
        self._pages["Beneficiaries"] = MyBeneficiariesView(self.pg_container, self.customer_id)