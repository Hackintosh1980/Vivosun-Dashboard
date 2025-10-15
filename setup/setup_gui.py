#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_gui.py – Einstiegspunkt für das 🌱 VIVOSUN Setup
Startet das Tk-Fenster, lädt Theme aus config und baut das Layout über setup_ui auf.
"""

import os
import sys
import tkinter as tk

# Pfad sicherstellen, falls als Modul gestartet
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    import icon_loader
except Exception:
    icon_loader = None

from setup import setup_ui, setup_logic


def run_setup():
    # Theme laden (Name -> Theme-Objekt)
    theme_name = setup_logic.load_theme_from_config()
    theme = setup_logic.get_theme_by_name(theme_name)

    root = tk.Tk()
    root.title("🌱 VIVOSUN Setup")
    root.geometry("720x820")
    root.configure(bg=getattr(theme, "BG_MAIN", "#0b1620"))

    if icon_loader:
        try:
            icon_loader.set_app_icon(root)
        except Exception:
            pass

    # Layout aufbauen
    setup_ui.build_gui(root, theme)

    root.mainloop()


if __name__ == "__main__":
    run_setup()
