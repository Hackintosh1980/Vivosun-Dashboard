#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
theme_oceanic.py – 🌊 Oceanic Blue Theme (vollständig, kompatibel)
"""

import sys
import tkinter as tk

# -----------------------
# Farben
# -----------------------
BG_MAIN    = "#07121e"
CARD_BG    = "#0b2033"
TEXT       = "#d6f6ff"
TEXT_DIM   = "#90bcd4"
BORDER     = "#102a40"
GRID       = "#123248"

# named accents
AQUA        = "#33ccff"
AQUA_DARK   = "#0077aa"
CYAN        = AQUA
CYAN_DARK   = AQUA_DARK
LIME        = "#66ffcc"
LIME_DARK   = "#33ccaa"
FOREST      = "#0a6b63"
ORANGE      = "#ffbb33"
AMBER       = "#ffcc66"
RED         = "#ff4444"
DISABLED    = "#30475e"

# -----------------------
# Button colors
# -----------------------
BTN_PRIMARY    = AQUA
BTN_SECONDARY  = CYAN
BTN_HOVER      = AQUA_DARK
BTN_RESET      = ORANGE
BTN_DANGER     = RED
BTN_DISABLED   = DISABLED
BTN_SAVE       = LIME
BTN_WARNING    = ORANGE

# -----------------------
# Fonts
# -----------------------
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_BTN   = ("Segoe UI", 11, "bold")
FONT_LABEL = ("Segoe UI", 10, "bold")
FONT_CODE  = ("Consolas", 9)

# -----------------------
# Helpers
# -----------------------
def make_button(master, text, cmd=None, color=BTN_PRIMARY, font=FONT_BTN):
    return tk.Button(
        master, text=text, command=cmd,
        bg=color, fg="black", font=font,
        activebackground=BTN_HOVER, activeforeground="black",
        relief="flat", padx=10, pady=6, cursor="hand2",
        highlightbackground=BTN_HOVER, highlightthickness=1, bd=0
    )

def make_frame(master, **kwargs):
    bg = kwargs.pop("bg", CARD_BG)
    return tk.Frame(master, bg=bg, **kwargs)

def apply_theme(widget, fg=TEXT, bg=BG_MAIN):
    try:
        widget.configure(bg=bg, fg=fg)
    except Exception:
        pass

def themed_spinbox(master, var, frm, to, inc=0.1, width=6):
    return tk.Spinbox(master, textvariable=var, from_=frm, to=to, increment=inc,
                      width=width, bg=CARD_BG, fg=TEXT, justify="center",
                      relief="flat", highlightbackground=AQUA_DARK, highlightthickness=1)

def themed_entry(master, var, width=28):
    return tk.Entry(master, textvariable=var, width=width, bg="#1e2a38", fg=TEXT, insertbackground=TEXT)

# -----------------------
# Compatibility aliases
# -----------------------
try:
    _mod = sys.modules.get(__name__)
    if not hasattr(_mod, "BTN_PRIMARY"): BTN_PRIMARY = locals().get("BTN_PRIMARY", AQUA)
    if not hasattr(_mod, "BTN_HOVER"): BTN_HOVER = locals().get("BTN_HOVER", AQUA_DARK)
    if not hasattr(_mod, "BTN_SECONDARY"): BTN_SECONDARY = locals().get("BTN_SECONDARY", CYAN)
    if not hasattr(_mod, "FOREST"): FOREST = locals().get("FOREST", FOREST)
    if not hasattr(_mod, "ORANGE"): ORANGE = locals().get("ORANGE", ORANGE)
    if not hasattr(_mod, "AQUA"): AQUA = locals().get("AQUA", AQUA)
    if not hasattr(_mod, "AQUA_DARK"): AQUA_DARK = locals().get("AQUA_DARK", AQUA_DARK)
    if not hasattr(_mod, "LIME"): LIME = locals().get("LIME", LIME)
    if not hasattr(_mod, "LIME_DARK"): LIME_DARK = locals().get("LIME_DARK", LIME_DARK)
    if not hasattr(_mod, "TEXT"): TEXT = locals().get("TEXT", TEXT)
except Exception:
    BTN_PRIMARY = AQUA
    BTN_HOVER = AQUA_DARK
    BTN_SECONDARY = CYAN
    FOREST = FOREST
    ORANGE = ORANGE
    AQUA = AQUA
    AQUA_DARK = AQUA_DARK
    LIME = LIME
    LIME_DARK = LIME_DARK
    TEXT = TEXT
