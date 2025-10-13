#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
theme_oceanic.py – 🌊 Oceanic Blue Theme (mit Button-Styling)
"""

import tkinter as tk

# ---------------------------------------------------------
# 🎨 Farben – Blue / Aqua Edition
# ---------------------------------------------------------
BG_MAIN   = "#07131a"
CARD_BG   = "#0e1e26"
AQUA      = "#33ddff"
AQUA_DARK = "#00a3cc"
NAVY      = "#0a3344"
ORANGE    = "#ffaa00"
TEXT      = "#e2faff"
TEXT_DIM  = "#99ddee"
BORDER    = "#104050"
GRID      = "#08303e"

# ---------------------------------------------------------
# 🖋 Fonts
# ---------------------------------------------------------
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_BTN   = ("Segoe UI", 11, "bold")
FONT_LABEL = ("Segoe UI", 10, "bold")

# ---------------------------------------------------------
# 🧩 Button Colors
# ---------------------------------------------------------
BTN_PRIMARY   = AQUA
BTN_HOVER     = AQUA_DARK
BTN_SECONDARY = NAVY
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
