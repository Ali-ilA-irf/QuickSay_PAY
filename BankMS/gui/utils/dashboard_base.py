import customtkinter as ctk

COLORS = {
    "bg_primary":   "#0A1628",
    "bg_secondary": "#1E3A5F",
    "accent":       "#C9A84C",
    "accent_hover": "#E8C060",
    "text_primary": "#FFFFFF",
    "text_muted":   "#A0AEC0",
    "success":      "#2ECC71",
    "error":        "#E74C3C",
    "sidebar":      "#061020",
    "card":         "#132338",
    "hover":        "#1A3050",
}


class SidebarButton(ctk.CTkButton):
    """Nav button with active gold indicator."""
    def __init__(self, master, text, icon="", command=None, **kw):
        super().__init__(
            master,
            text=f"  {icon}   {text}",
            anchor="w",
            fg_color="transparent",
            hover_color=COLORS["hover"],
            text_color=COLORS["text_muted"],
            font=ctk.CTkFont(size=14),
            height=44,
            corner_radius=6,
            border_width=0,
            command=command,
            **kw,
        )

    def set_active(self, active: bool):
        if active:
            self.configure(fg_color=COLORS["hover"], text_color=COLORS["accent"])
        else:
            self.configure(fg_color="transparent",   text_color=COLORS["text_muted"])


class DashboardBase(ctk.CTkFrame):
    """
    Base class shared by all role dashboards.
    Layout: fixed sidebar (left) + content area (right).
    Subclasses implement _build_sidebar_buttons() and _build_pages().
    """
    ROLE_LABEL = "Dashboard"

    def __init__(self, master, user_data: dict, logout_cb, **kw):
        super().__init__(master, fg_color=COLORS["bg_primary"], **kw)
        self.user_data  = user_data
        self.logout_cb  = logout_cb
        self._nav_btns: list[SidebarButton] = []
        # Pages are kept as direct children of self.content_area
        self._page_frames: list[ctk.CTkFrame] = []

        self._build_layout()
        self._build_sidebar_buttons()
        self._build_pages()
        self._animate_sidebar_in()
        self._switch_page(0)

    # ── Main layout ───────────────────────────────────────────────────────────
    def _build_layout(self):
        # ─ Sidebar ─
        self.sidebar = ctk.CTkFrame(
            self, fg_color=COLORS["sidebar"], width=240, corner_radius=0,
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Header
        hdr = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=72)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        ctk.CTkLabel(
            hdr, text="🏦  BankMS",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLORS["accent"],
        ).place(relx=0.5, rely=0.5, anchor="center")

        # Divider
        ctk.CTkFrame(self.sidebar, fg_color=COLORS["bg_secondary"], height=1).pack(fill="x")

        # Scrollable nav
        self.nav_frame = ctk.CTkScrollableFrame(
            self.sidebar, fg_color="transparent",
            scrollbar_button_color=COLORS["sidebar"],
        )
        self.nav_frame.pack(fill="both", expand=True)

        # Footer: user info + logout
        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=100)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        ctk.CTkFrame(footer, fg_color=COLORS["bg_secondary"], height=1).pack(fill="x")
        ctk.CTkLabel(
            footer, text=f"👤  {self.user_data.get('USERNAME', 'User')}",
            font=ctk.CTkFont(size=13), text_color=COLORS["text_muted"],
        ).pack(pady=(10, 2))
        ctk.CTkLabel(
            footer, text=self.ROLE_LABEL,
            font=ctk.CTkFont(size=11), text_color=COLORS["accent"],
        ).pack()
        ctk.CTkButton(
            footer, text="⎋  Logout",
            fg_color="transparent", hover_color="#200808",
            text_color=COLORS["error"], height=32,
            command=self.logout_cb,
        ).pack(pady=6)

        # ─ Content area ─
        # This frame is where all pages live; we show/hide them with pack/pack_forget
        self.content_area = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"], corner_radius=0)
        self.content_area.pack(side="left", fill="both", expand=True)

    # ── Sidebar slide-in ──────────────────────────────────────────────────────
    def _animate_sidebar_in(self):
        self.sidebar.configure(width=1)
        self._grow_sidebar(1)

    def _grow_sidebar(self, w):
        if w < 240:
            nw = min(w + 20, 240)
            self.sidebar.configure(width=nw)
            self.after(10, lambda: self._grow_sidebar(nw))

    # ── Navigation ────────────────────────────────────────────────────────────
    def _add_nav_btn(self, text: str, icon: str = "•"):
        idx = len(self._nav_btns)
        btn = SidebarButton(
            self.nav_frame, text=text, icon=icon,
            command=lambda i=idx: self._switch_page(i),
        )
        btn.pack(fill="x", padx=6, pady=2)
        self._nav_btns.append(btn)
        return btn

    def _switch_page(self, index: int):
        if index >= len(self._page_frames):
            return
        for i, (btn, frame) in enumerate(zip(self._nav_btns, self._page_frames)):
            btn.set_active(i == index)
            if i == index:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

        # Trigger refresh if page supports it
        page = self._page_frames[index]
        if hasattr(page, "refresh") and callable(page.refresh):
            page.refresh()

    # ── Subclass hooks ────────────────────────────────────────────────────────
    def _build_sidebar_buttons(self):
        raise NotImplementedError

    def _build_pages(self):
        raise NotImplementedError

    # ── Page factory ─────────────────────────────────────────────────────────
    def new_page(self, title: str) -> ctk.CTkFrame:
        """Create a styled page frame parented to content_area."""
        page = ctk.CTkFrame(self.content_area, fg_color=COLORS["bg_primary"], corner_radius=0)
        # Title bar
        bar = ctk.CTkFrame(page, fg_color=COLORS["card"], height=52, corner_radius=0)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        ctk.CTkLabel(
            bar, text=title,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["accent"],
        ).pack(side="left", padx=24, pady=0)
        return page

    def placeholder_page(self, title: str, msg: str) -> ctk.CTkFrame:
        page = self.new_page(title)
        ctk.CTkLabel(
            page, text=msg,
            font=ctk.CTkFont(size=22),
            text_color=COLORS["text_muted"],
        ).pack(expand=True)
        return page
