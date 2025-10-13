#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
theme_sunset.py – 🌇 Sunset Orange Theme (vollständig, kompatibel)
"""

import sys
import tkinter as tk

# -----------------------
# Farben
# -----------------------
BG_MAIN    = "#1b0d09"
CARD_BG    = "#2c120d"
TEXT       = "#fff2e5"
TEXT_DIM   = "#e0bba0"
BORDER     = "#3a2015"
GRID       = "#2a150c"

SUNSET_ORANGE = "#ff9966"
SUNSET_DARK   = "#cc7744"
ORANGE        = "#ff7043"
AMBER         = "#ffcc66"
GOLD          = "#ffcc33"
LIME          = "#ffd580"
LIME_DARK     = "#e6b800"
AQUA          = "#ffaa77"
AQUA_DARK     = "#cc8855"
RED           = "#ff4444"
DISABLED      = "#553322"
FOREST        = "#7a3a1a"

# -----------------------
# Buttons
# -----------------------
BTN_PRIMARY    = SUNSET_ORANGE
BTN_SECONDARY  = GOLD
BTN_HOVER      = SUNSET_DARK
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
                      relief="flat", highlightbackground=SUNSET_DARK, highlightthickness=1)

def themed_entry(master, var, width=28):
    return tk.Entry(master, textvariable=var, width=width, bg="#3a1f00", fg=TEXT, insertbackground=TEXT)

# -----------------------
# Compatibility aliases
# -----------------------
try:
    _mod = sys.modules.get(__name__)
    if not hasattr(_mod, "BTN_PRIMARY"): BTN_PRIMARY = locals().get("BTN_PRIMARY", SUNSET_ORANGE)
    if not hasattr(_mod, "BTN_HOVER"): BTN_HOVER = locals().get("BTN_HOVER", SUNSET_DARK)
    if not hasattr(_mod, "BTN_SECONDARY"): BTN_SECONDARY = locals().get("BTN_SECONDARY", GOLD)
    if not hasattr(_mod, "FOREST"): FOREST = locals().get("FOREST", FOREST)
    if not hasattr(_mod, "ORANGE"): ORANGE = locals().get("ORANGE", ORANGE)
    if not hasattr(_mod, "AQUA"): AQUA = locals().get("AQUA", AQUA)
    if not hasattr(_mod, "AQUA_DARK"): AQUA_DARK = locals().get("AQUA_DARK", AQUA_DARK)
    if not hasattr(_mod, "LIME"): LIME = locals().get("LIME", LIME)
    if not hasattr(_mod, "LIME_DARK"): LIME_DARK = locals().get("LIME_DARK", LIME_DARK)
    if not hasattr(_mod, "TEXT"): TEXT = locals().get("TEXT", TEXT)
except Exception:
    BTN_PRIMARY = SUNSET_ORANGE
    BTN_HOVER = SUNSET_DARK
    BTN_SECONDARY = GOLD
    FOREST = FOREST
    ORANGE = ORANGE
    AQUA = AQUA
    AQUA_DARK = AQUA_DARK
    LIME = LIME
    LIME_DARK = LIME_DARK
    TEXT = TEXT
