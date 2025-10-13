#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
theme_sunset.py – 🔥 VIVOSUN Sunset Edition
Warmer Darkmode mit orange-roten Akzenten und hellen Kontrastfarben.
"""

# ---------------------------------------------------------
# 🎨 Farben – Sunset Theme
# ---------------------------------------------------------
BG_MAIN   = "#1a0d0d"   # Dunkelrot-brauner Hintergrund
CARD_BG   = "#2b1414"   # Panels / Frames
BTN_PRIMARY   = "#ff9933"  # Hauptbuttons (Orange)
BTN_SECONDARY = "#ffbb66"  # Zweitbuttons (Hellorange)
BTN_RESET     = "#e53935"  # Warnung / Reset
BTN_HOVER     = "#ffb84d"  # Hover-Farbe
BORDER        = "#442020"  # Rahmenfarbe
TEXT          = "#fff4e5"  # Haupttext (leicht beige)
TEXT_DIM      = "#f5cba7"  # Sekundärer Text (hellorange)
ACCENT        = "#ff6600"  # Icons, aktive Elemente
GRID          = "#552a1a"  # Matplotlib-Grid

# ---------------------------------------------------------
# 🖋 Fonts
# ---------------------------------------------------------
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_BTN   = ("Segoe UI", 11, "bold")
FONT_LABEL = ("Segoe UI", 10, "bold")

# ---------------------------------------------------------
# 🧩 Sammelobjekt (für leichten Zugriff)
# ---------------------------------------------------------
VIVOSUN_COLORS = {
    "bg_main": BG_MAIN,
    "card_bg": CARD_BG,
    "btn_primary": BTN_PRIMARY,
    "btn_secondary": BTN_SECONDARY,
    "btn_reset": BTN_RESET,
    "border": BORDER,
    "text": TEXT,
    "text_dim": TEXT_DIM,
    "accent": ACCENT,
    "grid": GRID,
    "font_title": FONT_TITLE,
    "font_btn": FONT_BTN,
    "font_label": FONT_LABEL,
}

# ---------------------------------------------------------
# 🔧 Tkinter Helper – standardisiert das Aussehen
# ---------------------------------------------------------
import tkinter as tk


def make_button(master, text, cmd, color=BTN_PRIMARY, font=FONT_BTN):
    """Erstellt einen thematisch passenden Button mit Hover-Effekt."""
    btn = tk.Button(
        master,
        text=text,
        command=cmd,
        bg=color,
        fg="black",
        font=font,
        activebackground=BTN_HOVER,
        activeforeground="black",
        relief="flat",
        padx=10,
        pady=6,
        cursor="hand2",
        highlightbackground=BORDER,
        highlightthickness=2
    )

    def on_enter(e): btn.configure(bg=BTN_HOVER)
    def on_leave(e): btn.configure(bg=color)
    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


def make_frame(master, **kwargs):
    """Erzeugt ein Frame mit Sunset-Hintergrund."""
    bg = kwargs.pop("bg", CARD_BG)
    return tk.Frame(master, bg=bg, **kwargs)


def apply_theme(widget, fg=TEXT, bg=BG_MAIN):
    """Wendet Farben global an ein Tkinter-Widget an."""
    try:
        widget.configure(bg=bg, fg=fg)
    except Exception:
        pass
