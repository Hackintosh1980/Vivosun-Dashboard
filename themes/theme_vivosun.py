#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
theme_vivosun.py – 🌱 VIVOSUN Green Theme (vollständig, kompatibel)
"""

import sys
import tkinter as tk

# -----------------------
# Farben (Primary / Accents)
# -----------------------
BG_MAIN    = "#06110f"
CARD_BG    = "#0e1f18"
TEXT       = "#e5ffe5"
TEXT_DIM   = "#99cc99"
BORDER     = "#1e3d2e"
GRID       = "#113322"

# Accents / named colors (komplett)
LIME         = "#a8ff60"
LIME_DARK    = "#66cc33"
FOREST       = "#145c33"
AQUA         = "#00e0a0"
AQUA_DARK    = "#009970"
ORANGE       = "#ffaa00"
AMBER        = "#ffb347"
RED          = "#ff4444"
DISABLED     = "#445544"

# -----------------------
# Button & widget colors
# -----------------------
BTN_PRIMARY    = LIME
BTN_SECONDARY  = AQUA
BTN_HOVER      = LIME_DARK
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
                      relief="flat", highlightbackground=LIME_DARK, highlightthickness=1)

def themed_entry(master, var, width=28):
    return tk.Entry(master, textvariable=var, width=width, bg="#2c3e50", fg=TEXT, insertbackground=TEXT)

# -----------------------
# Compatibility aliases (vollständige Abdeckung)
# -----------------------
try:
    _mod = sys.modules.get(__name__)
    if not hasattr(_mod, "BTN_PRIMARY"): BTN_PRIMARY = locals().get("BTN_PRIMARY", LIME)
    if not hasattr(_mod, "BTN_HOVER"): BTN_HOVER = locals().get("BTN_HOVER", LIME_DARK)
    if not hasattr(_mod, "BTN_SECONDARY"): BTN_SECONDARY = locals().get("BTN_SECONDARY", AQUA)
    if not hasattr(_mod, "FOREST"): FOREST = locals().get("FOREST", FOREST)
    if not hasattr(_mod, "ORANGE"): ORANGE = locals().get("ORANGE", ORANGE)
    if not hasattr(_mod, "AQUA"): AQUA = locals().get("AQUA", AQUA)
    if not hasattr(_mod, "AQUA_DARK"): AQUA_DARK = locals().get("AQUA_DARK", AQUA_DARK)
    if not hasattr(_mod, "LIME"): LIME = locals().get("LIME", LIME)
    if not hasattr(_mod, "LIME_DARK"): LIME_DARK = locals().get("LIME_DARK", LIME_DARK)
    if not hasattr(_mod, "TEXT"): TEXT = locals().get("TEXT", TEXT)
except Exception:
    BTN_PRIMARY = LIME
    BTN_HOVER = LIME_DARK
    BTN_SECONDARY = AQUA
    FOREST = FOREST
    ORANGE = ORANGE
    AQUA = AQUA
    AQUA_DARK = AQUA_DARK
    LIME = LIME
    LIME_DARK = LIME_DARK
    TEXT = TEXT
