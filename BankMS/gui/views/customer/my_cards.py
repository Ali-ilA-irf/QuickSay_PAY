import tkinter as tk
import customtkinter as ctk
from gui.models.card_model import CardModel

# ── Palette ───────────────────────────────────────────────────────────────────
NAVY   = "#0D1B2A"; GOLD = "#E8A020"; BG = "#F0F4F8"; WHITE = "#FFFFFF"
T1     = "#1A1A2E"; T2 = "#6B7280"; RED = "#E74C3C"; GREEN = "#27AE60"
FONT   = "Playfair Display"


class MyCardsView(ctk.CTkFrame):
    def __init__(self, master, customer_id, **kw):
        super().__init__(master, bg_color=BG, fg_color=BG, **kw)
        self.customer_id = customer_id
        self.card_m = CardModel()
        
        self._build_ui()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=BG)
        hdr.pack(fill="x", padx=30, pady=(30, 10))
        tk.Label(hdr, text="My Cards", bg=BG, fg=NAVY, font=(FONT, 22, "bold")).pack(side="left")
        
        # Container for cards
        self.cards_frame = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        self.cards_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def refresh(self) -> None:
        # Clear existing cards
        for widget in self.cards_frame.winfo_children():
            widget.destroy()

        cards = self.card_m.get_cards_by_customer(self.customer_id)
        if not cards:
            tk.Label(self.cards_frame, text="No cards found.", bg=BG, fg=T2, font=(FONT, 14)).pack(pady=40)
            return

        # Display cards in a simple list or grid
        for c in cards:
            self._create_card_widget(c)

    def _create_card_widget(self, card_data):
        card_id = card_data.get("CARD_ID", "")
        c_num = card_data.get("CARD_NUMBER", "**** **** **** 0000")
        c_type = card_data.get("CARD_TYPE", "DEBIT")
        status = card_data.get("CARD_STATUS", "ACTIVE")
        exp = card_data.get("EXPIRES_ON", "12/28")
        acc_num = card_data.get("ACCOUNT_NUMBER", "")

        # Obfuscate card number except last 4 digits
        if len(c_num) > 4:
            display_num = "**** **** **** " + c_num[-4:]
        else:
            display_num = c_num

        # Main card container
        container = ctk.CTkFrame(self.cards_frame, fg_color=WHITE, corner_radius=12)
        container.pack(fill="x", pady=10, padx=10)

        # Left side - Visual Card
        visual = ctk.CTkFrame(container, fg_color=NAVY, corner_radius=8, width=280, height=160)
        visual.pack(side="left", padx=20, pady=20)
        visual.pack_propagate(False)

        tk.Label(visual, text="QuickSay Pay", bg=NAVY, fg=GOLD, font=(FONT, 14, "bold")).place(x=15, y=15)
        tk.Label(visual, text=c_type.upper(), bg=NAVY, fg=WHITE, font=(FONT, 10, "bold")).place(relx=1.0, x=-15, y=15, anchor="ne")
        
        tk.Label(visual, text=display_num, bg=NAVY, fg=WHITE, font=(FONT, 18, "bold", "italic")).place(x=15, rely=0.5, anchor="w")
        
        tk.Label(visual, text="VALID THRU", bg=NAVY, fg=T2, font=(FONT, 7)).place(x=15, rely=0.8, anchor="w")
        tk.Label(visual, text=exp, bg=NAVY, fg=WHITE, font=(FONT, 10)).place(x=15, rely=0.9, anchor="w")

        # Right side - Details & Actions
        details = tk.Frame(container, bg=WHITE)
        details.pack(side="left", fill="both", expand=True, padx=20, pady=20)

        tk.Label(details, text=f"Account: {acc_num}", bg=WHITE, fg=T1, font=(FONT, 12, "bold")).pack(anchor="w")
        tk.Label(details, text=f"Status: {status}", bg=WHITE, fg=GREEN if status == "ACTIVE" else RED, font=(FONT, 11)).pack(anchor="w", pady=(4, 10))

        if status == "ACTIVE":
            def block_card(cid=card_id):
                if self.card_m.deactivate_card(cid):
                    self.refresh()
            
            btn = ctk.CTkButton(details, text="Block Card", fg_color=RED, hover_color="#C0392B", 
                                font=(FONT, 12, "bold"), width=120, command=block_card)
            btn.pack(anchor="sw", side="bottom")