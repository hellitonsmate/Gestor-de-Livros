"""Estilos compartilhados para a interface Tkinter do gestor de livros.

Centraliza cores, fontes e configuração do tema ttk para manter a aparência
consistente em toda a aplicação.
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

# Paleta de cores principal da aplicação
COLORS = {
    "bg": "#f5f5f5",
    "bg_secondary": "#ffffff",
    "accent": "#1976d2",
    "accent_dark": "#115293",
    "accent_text": "#ffffff",
    "text": "#222222",
    "muted_text": "#555555",
    "border": "#d0d0d0",
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
        background=COLORS["bg_secondary"],
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
    )
    style.configure(
        "TLabelframe.Label",
        background=COLORS["bg"],
        foreground=COLORS["muted_text"],
        font=FONTS["section"],
    )

    # Botões
    style.configure(
        "TButton",
        padding=6,
        font=FONTS["button"],
    )

    # Scrollbar
    style.configure(
        "Vertical.TScrollbar",
        background=COLORS["bg_secondary"],
    )

    return style

