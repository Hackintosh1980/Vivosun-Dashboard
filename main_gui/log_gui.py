#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
log_gui.py – separates Log-Fenster für 🌱 VIVOSUN Dashboard
Erzeugt ein ScrolledText-Feld und gibt eine log(msg)-Funktion zurück.
"""

import tkinter as tk
from tkinter import scrolledtext, TclError
import datetime


def create_log_frame(parent, config):
    """Erzeugt das Log-Fenster unten im Dashboard und gibt log(msg)-Funktion zurück."""
    logframe = tk.Frame(parent, bg=config.BG)
    logframe.pack(side="bottom", fill="x", pady=6)

    logbox = scrolledtext.ScrolledText(
        logframe,
        height=4,
        bg="#071116",
        fg="#bff5c9",
        font=("Consolas", 9)
    )
    logbox.pack(fill="x", padx=8, pady=4)

    _app_closing = [False]  # Flag für sauberes Beenden

    def log(msg):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{ts}] {msg}")  # Immer in Konsole
        try:
            if _app_closing[0]:
                return
            if not parent or not parent.winfo_exists():
                return
            logbox.insert("end", f"[{ts}] {msg}\n")
            logbox.see("end")
        except TclError:
            pass

    return log, _app_closing
