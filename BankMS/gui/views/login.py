import customtkinter as ctk
import tkinter as tk
import threading
import random
from gui.models.employee_model import EmployeeModel

COLORS = {
    "bg_primary":   "#0A1628",
    "bg_secondary": "#1E3A5F",
    "accent":       "#C9A84C",
    "accent_hover": "#E8C060",
    "text_primary": "#FFFFFF",
    "text_muted":   "#A0AEC0",
    "error":        "#E74C3C",
    "card":         "#132338",
    "sidebar":      "#061020",
}


# ── Particle ──────────────────────────────────────────────────────────────────
class Particle:
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.x      = random.uniform(0, w)
        self.y      = random.uniform(0, h)
        self.radius = random.uniform(2, 5)
        self.vx     = random.uniform(-0.5, 0.5)
        self.vy     = random.uniform(-0.5, 0.5)
        self.alpha  = random.uniform(0.3, 1.0)
        # Compute display colour once (blended with bg)
        self._update_color()

    def _update_color(self):
        # Gold = C9, A8, 4C  |  bg = 0A, 16, 28
        a = self.alpha * 0.75
        r = int(0xC9 * a + 0x0A * (1 - a))
        g = int(0xA8 * a + 0x16 * (1 - a))
        b = int(0x4C * a + 0x28 * (1 - a))
        self.color = f"#{r:02x}{g:02x}{b:02x}"

    def move(self, w, h):
        self.w, self.h = w, h
        self.x += self.vx
        self.y += self.vy
        if self.x < 0 or self.x > w:
            self.vx *= -1
        if self.y < 0 or self.y > h:
            self.vy *= -1


def _make_particles(count, w, h):
    return [Particle(w, h) for _ in range(count)]


# ── Login Window ──────────────────────────────────────────────────────────────
class LoginWindow(ctk.CTkFrame):

    PARTICLE_COUNT = 120   # More particles, full-screen spread

    def __init__(self, master, on_success):
        super().__init__(master, fg_color=COLORS["bg_primary"])
        self.on_success  = on_success
        self.model       = EmployeeModel()
        self._particles  = []
        self._after_ids  = []
        self._animating  = False

        # We bind to <Configure> so we know the real size before spawning particles
        self.bind("<Configure>", self._on_resize)

        self._build_canvas()    # plain tk.Canvas — ctk has no CTkCanvas
        self._build_card()

        # Start slide-in animation after a small delay (gives window time to render)
        self._slide_offset = 50
        self.after(80, self._do_slide)

    # ── Canvas / Particles ────────────────────────────────────────────────────
    def _build_canvas(self):
        # Use plain tkinter Canvas — CustomTkinter does NOT have CTkCanvas
        self.canvas = tk.Canvas(
            self,
            bg=COLORS["bg_primary"],
            highlightthickness=0,
        )
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

    def _on_resize(self, event):
        w, h = event.width, event.height
        if w < 10 or h < 10:
            return
        # Re-spawn particles sized to the real canvas dimensions
        self._particles = _make_particles(self.PARTICLE_COUNT, w, h)
        if not self._animating:
            self._animating = True
            self._animate_particles()

    def _animate_particles(self):
        if not self.winfo_exists():
            return
        c = self.canvas
        w = self.winfo_width()
        h = self.winfo_height()
        c.delete("p")
        for p in self._particles:
            p.move(w, h)
            c.create_oval(
                p.x - p.radius, p.y - p.radius,
                p.x + p.radius, p.y + p.radius,
                fill=p.color, outline="", tags="p",
            )
        aid = self.after(28, self._animate_particles)
        self._after_ids.append(aid)

    # ── Login Card ────────────────────────────────────────────────────────────
    def _build_card(self):
        self.card = ctk.CTkFrame(
            self,
            fg_color=COLORS["card"],
            corner_radius=20,
            width=440,
            height=490,
            border_width=1,
            border_color=COLORS["accent"],
        )
        self.card.place(relx=0.5, rely=0.6, anchor="center")  # start lower
        self.card.pack_propagate(False)

        inner = ctk.CTkFrame(self.card, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=44, pady=36)

        # ── Logo
        ctk.CTkLabel(inner, text="🏦",
                     font=ctk.CTkFont(size=54),
                     text_color=COLORS["accent"]).pack(pady=(0, 4))

        ctk.CTkLabel(inner, text="QuickSay Pay",
                     font=ctk.CTkFont(family="Playfair Display", size=26, weight="bold"),
                     text_color=COLORS["accent"]).pack()

        ctk.CTkLabel(inner, text="Apke Dill Mein Hmara Account",
                     font=ctk.CTkFont(family="Playfair Display", size=13, slant="roman"),
                     text_color=COLORS["text_muted"]).pack(pady=(2, 18))

        # ── Fields
        self.username_var = ctk.StringVar()
        self.password_var = ctk.StringVar()
        self._make_field(inner, "👤  Username or Phone", self.username_var, show="")
        self._make_field(inner, "🔒  Password", self.password_var, show="●")

        # ── Error label
        self.error_lbl = ctk.CTkLabel(inner, text="",
                                      text_color=COLORS["error"],
                                      font=ctk.CTkFont(size=12))
        self.error_lbl.pack(pady=(6, 0))

        # ── Login button
        self.login_btn = ctk.CTkButton(
            inner,
            text="LOGIN",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["bg_primary"],
            height=46,
            corner_radius=10,
            command=self._handle_login,
        )
        self.login_btn.pack(fill="x", pady=(14, 0))

    def _make_field(self, parent, placeholder, var, show):
        e = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            textvariable=var,
            show=show,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS["bg_secondary"],
            border_color=COLORS["accent"],
            placeholder_text_color="#6B7280",
            border_width=1,
            height=44,
            corner_radius=9,
            text_color=COLORS["text_primary"],
        )
        e.pack(fill="x", pady=6)
        e.bind("<FocusIn>",  lambda _: e.configure(border_color=COLORS["accent_hover"], border_width=2))
        e.bind("<FocusOut>", lambda _: e.configure(border_color=COLORS["accent"],       border_width=1))
        e.bind("<Return>",   lambda _: self._handle_login())
        return e

    # ── Slide-in animation ────────────────────────────────────────────────────
    def _do_slide(self):
        if not self.winfo_exists():
            return
        if self._slide_offset > 0:
            self._slide_offset = max(0, self._slide_offset - 4)
            rely = 0.5 + self._slide_offset / 900
            self.card.place(relx=0.5, rely=rely, anchor="center")
            aid = self.after(10, self._do_slide)
            self._after_ids.append(aid)

    # ── Shake animation ───────────────────────────────────────────────────────
    def _shake_card(self):
        offsets = [14, -14, 11, -11, 8, -8, 5, -5, 2, -2, 0]
        self._do_shake(offsets)

    def _do_shake(self, offsets):
        if not self.winfo_exists():
            return
        if not offsets:
            self.card.place(relx=0.5, rely=0.5, anchor="center", x=0)
            return
        self.card.place(relx=0.5, rely=0.5, anchor="center", x=offsets[0])
        aid = self.after(38, lambda: self._do_shake(offsets[1:]))
        self._after_ids.append(aid)

    # ── Auth logic ────────────────────────────────────────────────────────────
    def _handle_login(self):
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        if not username or not password:
            self._show_error("Please enter both username and password.")
            return
        self.login_btn.configure(text="Connecting…", state="disabled")
        self.error_lbl.configure(text="")
        threading.Thread(
            target=self._auth_worker, args=(username, password), daemon=True
        ).start()

    def _auth_worker(self, username, password):
        user_data = self.model.authenticate_user(username, password)
        self.after(0, lambda: self._on_auth_done(user_data))

    def _on_auth_done(self, user_data):
        if not self.winfo_exists():
            return
        self.login_btn.configure(text="LOGIN", state="normal")
        if user_data:
            self._cleanup()
            self.on_success(user_data)   # hands off to App.on_login_success
        else:
            self._show_error("Invalid username or password.")
            self._shake_card()

    def _show_error(self, msg):
        if self.winfo_exists():
            self.error_lbl.configure(text=msg)

    # ── Cleanup ───────────────────────────────────────────────────────────────
    def _cleanup(self):
        self._animating = False
        for aid in self._after_ids:
            try:
                self.after_cancel(aid)
            except Exception:
                pass
        self._after_ids.clear()

    def destroy(self):
        self._cleanup()
        super().destroy()
