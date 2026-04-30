"""
gui/utils/fast_table.py
-----------------------
Provides make_treeview() — a styled ttk.Treeview that renders
instantly as a single native widget (no per-row CTk overhead).
"""
import tkinter as tk
import tkinter.ttk as ttk

COLORS = {
    "bg_primary":   "#0A1628",
    "bg_secondary": "#1E3A5F",
    "accent":       "#C9A84C",
    "text_primary": "#FFFFFF",
    "text_muted":   "#A0AEC0",
    "card":         "#132338",
    "row_alt":      "#0E2040",
    "selected":     "#1E3A5F",
}


def apply_treeview_style(style_name: str = "BankMS.Treeview"):
    """
    Configures a ttk.Style for a dark-themed Treeview.
    Call once at app startup or before first use.
    """
    style = ttk.Style()
    style.theme_use("default")

    style.configure(
        style_name,
        background=COLORS["card"],
        foreground=COLORS["text_muted"],
        fieldbackground=COLORS["card"],
        rowheight=34,
        font=("Segoe UI", 11),
        borderwidth=0,
        relief="flat",
    )
    style.configure(
        f"{style_name}.Heading",
        background=COLORS["bg_secondary"],
        foreground=COLORS["accent"],
        font=("Segoe UI", 11, "bold"),
        borderwidth=0,
        relief="flat",
        padding=(10, 6),
    )
    style.map(
        style_name,
        background=[("selected", COLORS["selected"])],
        foreground=[("selected", COLORS["text_primary"])],
    )
    style.map(
        f"{style_name}.Heading",
        background=[("active", COLORS["bg_secondary"])],
    )


def make_treeview(parent, columns: list[str], stretch: bool = True) -> ttk.Treeview:
    """
    Create and return a fully styled Treeview widget.
    Rows can be inserted with tv.insert('', 'end', values=(...)).
    Call clear_tree(tv) before re-populating.
    """
    apply_treeview_style()

    frame = tk.Frame(parent, bg=COLORS["card"])
    frame.pack(fill="both", expand=True, padx=0, pady=0)

    # Scrollbar
    sb = ttk.Scrollbar(frame, orient="vertical")
    sb.pack(side="right", fill="y")

    tv = ttk.Treeview(
        frame,
        columns=columns,
        show="headings",
        style="BankMS.Treeview",
        yscrollcommand=sb.set,
    )
    sb.config(command=tv.yview)

    for col in columns:
        tv.heading(col, text=col, anchor="w")
        tv.column(col, anchor="w", minwidth=80,
                  stretch=stretch)

    tv.pack(fill="both", expand=True)

    # Alternating row colours via tags
    tv.tag_configure("odd",  background=COLORS["card"])
    tv.tag_configure("even", background=COLORS["row_alt"])

    return tv


def populate_tree(tv: ttk.Treeview, rows: list[list]):
    """
    Clear and repopulate a Treeview with rows instantly.
    `rows` is a list of lists/tuples matching the column count.
    """
    tv.delete(*tv.get_children())
    for i, row in enumerate(rows):
        tag = "even" if i % 2 == 0 else "odd"
        tv.insert("", "end", values=row, tags=(tag,))
