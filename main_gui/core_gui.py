#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core_gui.py – Hauptfenster des 🌱 VIVOSUN Thermo Dashboard
Bindet Header, Charts-Platzhalter, Log und Footer ein.
"""

import tkinter as tk
import json
from collections import deque
from tkinter import TclError

import config, utils
from main_gui.header_gui import build_header
from widgets.footer_widget import create_footer
from async_reader import start_reader_thread, set_log_callback, set_status_callback
from main_gui.log_gui import create_log_frame
from main_gui.charts_gui import create_charts
from PIL import Image, ImageTk  # bleibt hier, falls später Bilder gebraucht werden


def run_app(device_id=None):
    """Startet das Dashboard."""
    root = tk.Tk()
    root.title(getattr(config, "APP_DISPLAY", "🌱 VIVOSUN Thermo Dashboard"))
    root.geometry("1600x900")
    root.configure(bg=getattr(config, "BG", "#0b1620"))

    # ---------- HEADER ----------
    header = build_header(root, config, {}, {}, lambda msg=None: None)

    # ---------- LOG ----------
    log, _app_closing = create_log_frame(root, config)
    log("🌱 Dashboard gestartet – Logsystem aktiv")

    # ---------- CHARTS ----------
    charts_frame = create_charts(root, config, log)

    # ---------- FOOTER ----------
    set_status, mark_data_update = create_footer(root, config)
    try:
        set_status(False)
    except Exception:
        pass

    # ---------- READER CALLBACKS ----------
    set_log_callback(log)
    set_status_callback(set_status)

    try:
        start_reader_thread(device_id)
        log(f"🔌 Verbinde mit Gerät {device_id} ...")
    except Exception as e:
        log(f"❌ Fehler beim Starten des Readers: {e}")

    # ---------- STATUS WATCHER ----------
    def update_status_from_file():
        """Liest periodisch status.json und aktualisiert LED."""
        try:
            with open(config.STATUS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            connected = data.get("connected", False)
            set_status(connected)
        except Exception:
            pass
        root.after(2000, update_status_from_file)  # alle 2 Sekunden prüfen

    update_status_from_file()

# ---------- SHUTDOWN HANDLER ----------
    def on_close():
        """Sauberer Programm-Shutdown (Reader + GUI)."""
        # Log-Callback stummschalten / App schließt
        try:
            _app_closing[0] = True
        except Exception:
            pass

        # Reader beenden
        try:
            from async_reader import stop_reader
            log("[🧹] Stoppe Async-Reader …")
            stop_reader()
        except Exception as e:
            log(f"⚠️ Fehler beim Stoppen des Readers: {e}")

        # Mainloop beenden und Fenster sicher zerstören
        try:
            root.quit()
        except Exception:
            pass
        try:
            root.after(50, root.destroy)
        except Exception:
            pass

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
