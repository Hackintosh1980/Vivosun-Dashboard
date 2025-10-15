#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌱 VIVOSUN Setup GUI – Root-Fenster + Theme-Picker
"""

import tkinter as tk
from tkinter import ttk
import os, sys
from main_gui import theme_picker
import config, utils, icon_loader
from themes import theme_vivosun, theme_oceanic
from . import setup_layout

THEMES = {
    "🌿 VIVOSUN Green": theme_vivosun,
    "🌊 Oceanic Blue": theme_oceanic,
}

def load_theme():
    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    return THEMES.get(cfg.get("theme"), theme_vivosun)

def run_setup():
    theme = load_theme()

    root = tk.Tk()
    root.title("🌱 VIVOSUN Setup")
    root.geometry("560x780")
    root.configure(bg=theme.BG_MAIN)
    icon_loader.set_app_icon(root)

    # Theme Picker
    topbar = tk.Frame(root, bg=theme.CARD_BG)
    topbar.pack(fill="x", pady=(8, 10))

    tk.Label(topbar, text="🎨 Theme:", bg=theme.CARD_BG, fg=theme.TEXT_DIM, font=theme.FONT_LABEL).pack(side="left", padx=(12, 6))

    def on_theme_change(new_name):
        new_theme = theme_picker.get_available_themes().get(new_name)
        if new_theme:
            theme_picker.save_theme_to_config(new_name)
            setup_layout.build_gui(root, new_theme)

    dropdown, theme_var = theme_picker.create_theme_picker(topbar, current_theme="🌿 VIVOSUN Green", on_change=on_theme_change)
    dropdown.pack(side="left", padx=(0, 12))

    # Layout erzeugen
    setup_layout.build_gui(root, theme)

    root.mainloop()
