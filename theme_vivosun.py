#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
theme_vivosun.py – 🌱 VIVOSUN Global Theme System
Verbindet Setup, Dashboard & Widgets im einheitlichen Lime-Green Design.
"""

# ---------------------------------------------------------
# 🎨 Farben – VIVOSUN Green Edition
# ---------------------------------------------------------
BG_MAIN   = "#06110f"   # Haupt-Hintergrund (dunkelgrün/schwarz)
CARD_BG   = "#0e1f18"   # Panels / Frames
LIME      = "#a8ff60"   # Primärfarbe (Akzent, Buttons)
LIME_DARK = "#66cc33"   # Hover / Rahmen
FOREST    = "#145c33"   # Sekundärfarbe
AQUA      = "#00e0a0"   # Aktive Elemente
ORANGE    = "#ffaa00"   # Warnung / Reset-Akzent
TEXT      = "#e5ffe5"   # Hauptschrift
TEXT_DIM  = "#99cc99"   # Sekundäre Schrift
BORDER    = "#1e3d2e"   # Rahmen / Trenner
GRID      = "#113322"   # Matplotlib-Grid-Linien

# ---------------------------------------------------------
# 🖋 Fonts
# ---------------------------------------------------------
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_BTN   = ("Segoe UI", 11, "bold")
FONT_LABEL = ("Segoe UI", 10, "bold")

# ---------------------------------------------------------
# 🧩 Sammelobjekt (für einfachen Import)
# ---------------------------------------------------------
VIVOSUN_COLORS = {
    "bg_main": BG_MAIN,
    "card_bg": CARD_BG,
    "lime": LIME,
    "lime_dark": LIME_DARK,
    "forest": FOREST,
    "aqua": AQUA,
    "orange": ORANGE,
    "text": TEXT,
    "text_dim": TEXT_DIM,
    "border": BORDER,
    "grid": GRID,
    "font_title": FONT_TITLE,
    "font_btn": FONT_BTN,
    "font_label": FONT_LABEL,
}

# ---------------------------------------------------------
# 🔧 Helper – vereinfachte Button- und Frame-Erstellung
# ---------------------------------------------------------
import tkinter as tk

def make_button(master, text, cmd, color=LIME, font=FONT_BTN):
    return tk.Button(
        master, text=text, command=cmd,
        bg=color, fg="black", font=font,
        activebackground=LIME_DARK, activeforeground="black",
        relief="flat", padx=10, pady=6, cursor="hand2",
        highlightbackground=LIME_DARK, highlightthickness=2
    )

def make_frame(master, **kwargs):
    bg = kwargs.pop("bg", CARD_BG)
    return tk.Frame(master, bg=bg, **kwargs)

def apply_theme(widget, fg=TEXT, bg=BG_MAIN):
    """Einheitlicher Hintergrund & Schrift anwenden."""
    try:
        widget.configure(bg=bg, fg=fg)
    except Exception:
        pass
