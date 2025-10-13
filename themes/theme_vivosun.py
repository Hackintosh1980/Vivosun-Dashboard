#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
theme_vivosun.py – 🌱 VIVOSUN Green Theme (mit Button-Styling)
"""

import tkinter as tk

# ---------------------------------------------------------
# 🎨 Farben – Green Edition
# ---------------------------------------------------------
BG_MAIN   = "#06110f"
CARD_BG   = "#0e1f18"
LIME      = "#a8ff60"
LIME_DARK = "#66cc33"
FOREST    = "#145c33"
AQUA      = "#00e0a0"
ORANGE    = "#ffaa00"
TEXT      = "#e5ffe5"
TEXT_DIM  = "#99cc99"
BORDER    = "#1e3d2e"
GRID      = "#113322"

# ---------------------------------------------------------
# 🖋 Fonts
# ---------------------------------------------------------
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_BTN   = ("Segoe UI", 11, "bold")
FONT_LABEL = ("Segoe UI", 10, "bold")

# ---------------------------------------------------------
# 🧩 Button Colors
# ---------------------------------------------------------
BTN_PRIMARY   = LIME
BTN_HOVER     = LIME_DARK
BTN_SECONDARY = FOREST
BTN_RESET     = ORANGE
BTN_TEXT      = "#000000"

# ---------------------------------------------------------
# 🔧 Factory Helpers
# ---------------------------------------------------------
def make_button(master, text, cmd, color=None, hover=None, font=FONT_BTN):
    color = color or BTN_PRIMARY
    hover = hover or BTN_HOVER
    btn = tk.Button(
        master,
        text=text,
        command=cmd,
        bg=color,
        fg=BTN_TEXT,
        font=font,
        relief="flat",
        activebackground=hover,
        activeforeground=BTN_TEXT,
        cursor="hand2",
        bd=0,
        padx=12,
        pady=6,
        highlightthickness=2,
        highlightbackground=hover
    )

    # Hover effect
    def on_enter(e):
        btn.configure(bg=hover)

    def on_leave(e):
        btn.configure(bg=color)

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)

    return btn


def make_frame(master, **kwargs):
    bg = kwargs.pop("bg", CARD_BG)
    return tk.Frame(master, bg=bg, **kwargs)


def apply_theme(widget, fg=TEXT, bg=BG_MAIN):
    try:
        widget.configure(bg=bg, fg=fg)
    except Exception:
        pass
