"""
dashboard_teller.py — Placeholder stub.
This module will be fully implemented in a future phase.
"""
import customtkinter as ctk


class TellerDashboardView(ctk.CTkFrame):
    """Stub: will be implemented in a future phase."""

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=20, weight='bold'),
        ).pack(expand=True)

    def refresh(self) -> None:
        """Called by DashboardBase when this page becomes active."""
        pass