#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
theme_picker.py – universeller Theme-Auswahl-Widget für das 🌱 VIVOSUN Dashboard
Kann in Settings, Header oder anderen Fenstern eingebunden werden.
"""

import tkinter as tk
from tkinter import ttk
from themes import theme_vivosun, theme_oceanic

try:
    from themes import theme_sunset
    THEMES = {
        "🌿 VIVOSUN Green": theme_vivosun,
        "🌊 Oceanic Blue": theme_oceanic,
        "🔥 VIVOSUN Sunset": theme_sunset,
    }
except ImportError:
    THEMES = {
        "🌿 VIVOSUN Green": theme_vivosun,
        "🌊 Oceanic Blue": theme_oceanic,
    }


def create_theme_picker(parent, current_theme_name, on_change=None, theme=None):
    """
    Erstellt ein Theme-Picker-Widget (Label + Combobox).
    
    parent        – Tkinter-Container, in den das Widget eingefügt wird
    current_theme_name – aktuell gesetztes Theme (z.B. aus config)
    on_change     – Callback-Funktion bei Theme-Wechsel
    theme         – aktives Theme-Objekt (für Farben)
    """
    if theme is None:
        theme = theme_vivosun  # Fallback

    tk.Label(
        parent,
        text="🎨 Theme:",
        bg=theme.BG_MAIN,
        fg=theme.TEXT,
        font=theme.FONT_LABEL,
        anchor="w"
    ).grid(row=0, column=0, sticky="w", pady=8)

    theme_var = tk.StringVar(value=current_theme_name)
    theme_dropdown = ttk.Combobox(
        parent,
        textvariable=theme_var,
        values=list(THEMES.keys()),
        state="readonly",
        width=25
    )
    theme_dropdown.grid(row=0, column=1, sticky="w", pady=8)

    # Style anpassen
    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "TCombobox",
        fieldbackground=theme.CARD_BG,
        background=theme.CARD_BG,
        foreground=theme.TEXT,
        arrowcolor=theme.TEXT
    )

    def _on_change(event=None):
        if callable(on_change):
            on_change(theme_var.get())

    theme_dropdown.bind("<<ComboboxSelected>>", _on_change)

    return theme_var, theme_dropdown, THEMES
