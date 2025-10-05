#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
icon_loader.py – Einheitliches Icon-Handling für macOS & Windows/Linux
- Setzt Haupt- und Dock-Icon beim Start
- Hängt Subwindows (Toplevel) ans Hauptfenster-Icon
"""

import os
import sys
import tkinter as tk


def resource_path(relative_path: str) -> str:
    """Pfad auch im PyInstaller-Bundle korrekt auflösen."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def set_app_icon(root: tk.Tk):
    """
    Setzt Fenster- und Dock-Icon plattformübergreifend.
    Muss direkt nach dem Erzeugen von root = tk.Tk() aufgerufen werden.
    """
    icon_png = resource_path("assets/logo.png")

    # --- Tkinter Fenster-Icon setzen ---
    if os.path.exists(icon_png):
        try:
            img = tk.PhotoImage(file=icon_png)
            root.iconphoto(True, img)
        except Exception as e:
            print("⚠️ Konnte Fenster-Icon nicht setzen:", e)

    # --- macOS Dock-Icon explizit setzen ---
    if sys.platform == "darwin":
        try:
            from AppKit import NSApplication, NSImage
            icon_icns = resource_path("assets/logo.icns")
            if os.path.exists(icon_icns):
                app = NSApplication.sharedApplication()
                img = NSImage.alloc().initWithContentsOfFile_(icon_icns)
                if img:
                    app.setApplicationIconImage_(img)
        except Exception as e:
            print("⚠️ Dock-Icon setzen fehlgeschlagen:", e)


def link_icon(win: tk.Toplevel, parent: tk.Tk):
    """
    Subwindow (Toplevel) übernimmt das Icon vom Hauptfenster
    und wird im Dock gruppiert.
    """
    try:
        # Gleiches Icon wie parent übernehmen
        win.iconphoto(False, parent.iconphoto())
        # Visuell mit Hauptfenster koppeln
        win.transient(parent)
        try:
            win.wm_group(parent)
        except Exception:
            pass
    except Exception as e:
        print("⚠️ Subwindow-Icon nicht gesetzt:", e)
