#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
theme_picker.py – Wiederverwendbarer Theme-Picker für 🌱 VIVOSUN Dashboard & Setup
"""

import tkinter as tk
from tkinter import ttk
import utils, config
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


def get_available_themes():
    return THEMES


def load_theme_from_config():
    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    t = cfg.get("theme", "🌿 VIVOSUN Green")
    return t if t in THEMES else "🌿 VIVOSUN Green"


def save_theme_to_config(t):
    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    cfg["theme"] = t
    utils.safe_write_json(config.CONFIG_FILE, cfg)


def create_theme_picker(parent, current_theme=None, on_change=None):
    theme_var = tk.StringVar(value=current_theme or load_theme_from_config())
    combo = ttk.Combobox(
        parent,
        textvariable=theme_var,
        values=list(THEMES.keys()),
        state="readonly",
        width=25,
    )

    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "TCombobox",
        fieldbackground="#1b1b1b",
        background="#1b1b1b",
        foreground="#dddddd",
        arrowcolor="#cccccc",
    )

    def _on_select(event=None):
        selected = theme_var.get()
        save_theme_to_config(selected)
        if on_change:
            on_change(selected)

    combo.bind("<<ComboboxSelected>>", _on_select)
    return combo, theme_var
