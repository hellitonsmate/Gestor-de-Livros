"""Estilos compartilhados para a interface Tkinter do gestor de livros.

Centraliza cores, fontes e configuração do tema ttk para manter a aparência
consistente em toda a aplicação.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

# Paleta de cores principal da aplicação
COLORS = {
    "bg": "#eef2f7",
    "bg_secondary": "#ffffff",
    "accent": "#1565c0",
    "accent_dark": "#0d47a1",
    "danger": "#c62828",
    "danger_dark": "#8e0000",
    "accent_text": "#ffffff",
    "text": "#1f2937",
    "muted_text": "#4b5563",
    "border": "#cfd8e3",
    "list_bg": "#ffffff",
}

# Fontes padrão usadas na interface
FONTS = {
    "title": ("Segoe UI", 14, "bold"),
    "section": ("Segoe UI", 11, "bold"),
    "normal": ("Segoe UI", 10),
    "mono": ("Courier New", 10),
    "button": ("Segoe UI", 10, "bold"),
}


def apply_style(root: tk.Tk) -> ttk.Style:
    """Aplica o tema ttk e configura estilos padrão."""
    style = ttk.Style(root)

    # Tenta usar um tema moderno; se não existir, mantém o padrão.
    for theme in ("clam", "default", "alt"):
        try:
            style.theme_use(theme)
            break
        except tk.TclError:
            continue

    # Janela principal
    root.configure(bg=COLORS["bg"])

    # Frames
    style.configure(
        "Main.TFrame",
        background=COLORS["bg"],
    )
    style.configure(
        "Card.TFrame",
        background=COLORS["bg_secondary"],
        relief="groove",
        borderwidth=1,
    )

    # Labels
    style.configure(
        "TLabel",
        background=COLORS["bg"],
        foreground=COLORS["text"],
        font=FONTS["normal"],
    )
    style.configure(
        "Section.TLabel",
        background=COLORS["bg"],
        foreground=COLORS["muted_text"],
        font=FONTS["section"],
    )

    # Labelframes
    style.configure(
        "TLabelframe",
        background=COLORS["bg"],
        borderwidth=1,
        relief="solid",
        bordercolor=COLORS["border"],
    )
    style.configure(
        "TLabelframe.Label",
        background=COLORS["bg"],
        foreground=COLORS["muted_text"],
        font=FONTS["section"],
    )
    style.configure(
        "Panel.TLabelframe",
        background=COLORS["bg_secondary"],
        borderwidth=1,
        relief="solid",
        bordercolor=COLORS["border"],
        padding=2,
    )
    style.configure(
        "Panel.TLabelframe.Label",
        background=COLORS["bg_secondary"],
        foreground=COLORS["muted_text"],
        font=FONTS["section"],
    )
    style.configure(
        "Panel.TFrame",
        background=COLORS["bg_secondary"],
    )
    style.configure(
        "Panel.TLabel",
        background=COLORS["bg_secondary"],
        foreground=COLORS["text"],
        font=FONTS["normal"],
    )

    # Botões
    style.configure(
        "TButton",
        padding=(10, 7),
        font=FONTS["button"],
    )
    style.configure(
        "Primary.TButton",
        background=COLORS["accent"],
        foreground=COLORS["accent_text"],
    )
    style.map(
        "Primary.TButton",
        background=[("active", COLORS["accent_dark"])],
        foreground=[("active", COLORS["accent_text"])],
    )
    style.configure(
        "Danger.TButton",
        background=COLORS["danger"],
        foreground=COLORS["accent_text"],
    )
    style.map(
        "Danger.TButton",
        background=[("active", COLORS["danger_dark"])],
        foreground=[("active", COLORS["accent_text"])],
    )

    # Scrollbar
    style.configure(
        "Vertical.TScrollbar",
        background=COLORS["bg_secondary"],
    )

    # Tabela de livros
    style.configure(
        "Books.Treeview",
        background=COLORS["list_bg"],
        fieldbackground=COLORS["list_bg"],
        foreground=COLORS["text"],
        font=FONTS["normal"],
        rowheight=28,
        bordercolor=COLORS["border"],
        borderwidth=1,
    )
    style.configure(
        "Books.Treeview.Heading",
        background=COLORS["accent"],
        foreground=COLORS["accent_text"],
        font=FONTS["button"],
        relief="flat",
        padding=(6, 6),
    )
    style.map(
        "Books.Treeview",
        background=[("selected", COLORS["accent"])],
        foreground=[("selected", COLORS["accent_text"])],
    )
    style.map(
        "Books.Treeview.Heading",
        background=[("active", COLORS["accent_dark"])],
    )

    return style
