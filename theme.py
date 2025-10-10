#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
theme.py – VIVOSUN Dashboard Theme v4.2
Cross-Platform Safe + Harmonized Matplotlib Fonts
"""

from __future__ import annotations
import os, sys, warnings
from tkinter import Tk, ttk
from cycler import cycler

warnings.filterwarnings("ignore", message="findfont", module="matplotlib")

# -------------------------------------------------------------
# Globale Variablen
# -------------------------------------------------------------
_mode = "dark"
MODES = ("dark", "light")

COLORS = {}
SPACING = {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 24}
RADII   = {"sm": 4, "md": 8, "lg": 12}

# ---- Font Stack (universell verfügbar) ----
FONT_BASE_STACK  = ["DejaVu Sans", "Arial", "Helvetica", "sans-serif"]
FONT_MONO_STACK  = ["DejaVu Sans Mono", "Consolas", "Courier New", "monospace"]

FONTS = {
    "base":  (FONT_BASE_STACK[0], 11),
    "mono":  (FONT_MONO_STACK[0], 11),
    "title": (FONT_BASE_STACK[0], 14, "bold"),
    "chart_value": (FONT_BASE_STACK[0], 40, "bold"),
}

# -------------------------------------------------------------
# Farbsets
# -------------------------------------------------------------
def set_mode(mode: str = "dark"):
    global _mode, COLORS
    _mode = "dark" if mode not in MODES else mode

    if _mode == "dark":
        COLORS = {
            "bg": "#0f1115",
            "card": "#171a21",
            "muted": "#1d222b",
            "text": "#e9edf2",
            "subtext": "#aab0bd",
            "accent": "#00e676",
            "accent2": "#33ff99",
            "warn": "#f1c40f",
            "error": "#ff5c5c",
            "ok": "#98c379",
            "grid": "#2b303a",
            "entry_bg": "#101417",
            "entry_fg": "#f2f4f8",
        }
    else:
        COLORS = {
            "bg": "#f8fafc",
            "card": "#ffffff",
            "muted": "#eef2f7",
            "text": "#1f2937",
            "subtext": "#4b5563",
            "accent": "#00c853",
            "accent2": "#00e676",
            "warn": "#b45309",
            "error": "#dc2626",
            "ok": "#16a34a",
            "grid": "#d1d5db",
            "entry_bg": "#ffffff",
            "entry_fg": "#1f2937",
        }

set_mode("dark")

# -------------------------------------------------------------
# ttk Styles
# -------------------------------------------------------------
def _ensure_style():
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # --- Grundlayout ---
    style.configure(
        ".",
        background=COLORS["bg"],
        foreground=COLORS["text"],
        font=FONTS["base"]
    )

    style.configure("Vivo.TFrame", background=COLORS["bg"])
    style.configure("VivoCard.TFrame", background=COLORS["card"])

    # --- Labels ---
    style.configure("Vivo.TLabel", background=COLORS["bg"], foreground=COLORS["text"])
    style.configure("VivoSub.TLabel", background=COLORS["bg"], foreground=COLORS["subtext"])
    style.configure("VivoTitle.TLabel", background=COLORS["bg"], foreground=COLORS["text"], font=FONTS["title"])
    style.configure("VivoOk.TLabel", foreground=COLORS["ok"])
    style.configure("VivoWarn.TLabel", foreground=COLORS["warn"])
    style.configure("VivoErr.TLabel", foreground=COLORS["error"])

    # --- Buttons ---
    style.configure(
        "Vivo.TButton",
        background=COLORS["muted"],
        foreground=COLORS["text"],
        padding=(SPACING["sm"], SPACING["xs"]),
        font=FONTS["base"],
        relief="flat"
    )
    style.map(
        "Vivo.TButton",
        background=[("active", COLORS["accent2"])],
        foreground=[("active", "#000")]
    )

    # Accent Button
    style.configure(
        "VivoAccent.TButton",
        background=COLORS["accent"],
        foreground="#0b0c0f",
        padding=(SPACING["sm"], SPACING["xs"]),
        font=(FONT_BASE_STACK[0], 11, "bold")
    )
    style.map("VivoAccent.TButton", background=[("active", COLORS["accent2"])])

    # Pfeil-Buttons
    style.configure(
        "VivoArrow.TButton",
        background=COLORS["accent"],
        foreground="#000",
        font=(FONT_BASE_STACK[0], 16, "bold"),
        padding=(12, 6),
        relief="flat"
    )
    style.map(
        "VivoArrow.TButton",
        background=[("active", COLORS["accent2"])],
        foreground=[("active", "#000")]
    )

    # --- Entry (Textfelder) ---
    style.configure(
        "Vivo.TEntry",
        fieldbackground=COLORS["entry_bg"],
        foreground=COLORS["entry_fg"],
        borderwidth=1,
        relief="flat",
        padding=(8, 5),
        font=(FONT_BASE_STACK[0], 14)
    )
    style.map(
        "Vivo.TEntry",
        fieldbackground=[
            ("readonly", COLORS["entry_bg"]),
            ("focus", COLORS["entry_bg"]),
            ("!disabled", COLORS["entry_bg"]),
        ],
        foreground=[
            ("disabled", COLORS["subtext"]),
            ("!disabled", COLORS["entry_fg"]),
        ]
    )

    # --- Progressbar ---
    style.configure(
        "Vivo.Horizontal.TProgressbar",
        troughcolor=COLORS["card"],
        background=COLORS["accent"],
        lightcolor=COLORS["accent2"],
        darkcolor=COLORS["accent"],
        thickness=16,
        bordercolor=COLORS["card"]
    )

# -------------------------------------------------------------
# Theme Anwenden
# -------------------------------------------------------------
def apply_theme(root: Tk):
    root.configure(bg=COLORS["bg"])
    _ensure_style()

def mk_card(parent, padding=None):
    if padding is None:
        padding = (SPACING["lg"], SPACING["md"])
    frame = ttk.Frame(parent, style="VivoCard.TFrame", padding=padding)
    try:
        frame.configure(borderwidth=1, relief="flat")
    except Exception:
        pass
    return frame

# -------------------------------------------------------------
# Matplotlib Styling
# -------------------------------------------------------------
def apply_matplotlib_defaults():
    import matplotlib as mpl
    mpl.rcParams.update({
        "font.family": FONT_BASE_STACK,
        "figure.facecolor": COLORS["bg"],
        "axes.facecolor": COLORS["card"],
        "axes.edgecolor": COLORS["grid"],
        "axes.labelcolor": COLORS["text"],
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "xtick.color": COLORS["subtext"],
        "ytick.color": COLORS["subtext"],
        "grid.color": COLORS["grid"],
        "grid.alpha": 0.5,
        "text.color": COLORS["text"],
        "savefig.facecolor": COLORS["bg"],
        "savefig.edgecolor": COLORS["bg"],
        "lines.linewidth": 2.0,
        "patch.edgecolor": COLORS["bg"],
    })
    mpl.rcParams["axes.prop_cycle"] = cycler(color=[
        COLORS["accent"], COLORS["accent2"], COLORS["ok"], COLORS["warn"], COLORS["error"]
    ])

def style_figure(fig):
    fig.set_facecolor(COLORS["bg"])
    for ax in fig.get_axes():
        ax.set_facecolor(COLORS["card"])
        ax.grid(True, linestyle="--", linewidth=0.7, color=COLORS["grid"])

# -------------------------------------------------------------
# Init Helper
# -------------------------------------------------------------
def init_all(root: Tk, mode: str = "dark"):
    set_mode(mode)
    apply_theme(root)
    try:
        apply_matplotlib_defaults()
    except Exception:
        pass

# -------------------------------------------------------------
# Getter
# -------------------------------------------------------------
def colors(): return COLORS
def spacing(): return SPACING
def fonts():   return FONTS
def radii():   return RADII
def mode():    return _mode
