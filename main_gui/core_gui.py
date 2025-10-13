#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core_gui.py – Hauptfenster des 🌱 VIVOSUN Thermo Dashboard
Bindet Header, Charts, Log und Footer ein.
"""

import tkinter as tk
import json
from collections import deque

import config, utils
from main_gui.header_gui import build_header
from widgets.footer_widget import create_footer
from async_reader import start_reader_thread, set_log_callback, set_status_callback
from main_gui.log_gui import create_log_frame
from main_gui.charts_gui import create_charts


def run_app(device_id=None):
    """Startet das Dashboard."""
    root = tk.Tk()
    root.title(getattr(config, "APP_DISPLAY", "🌱 VIVOSUN Thermo Dashboard"))
    root.geometry("1600x900")
    root.configure(bg=getattr(config, "BG", "#0b1620"))

    # Haupt-Container (ordnet alles vertikal)
    main_frame = tk.Frame(root, bg=config.BG)
    main_frame.pack(fill="both", expand=True)
    main_frame.pack_propagate(False)

    # ---------- HEADER ----------
    header = build_header(main_frame, config, {}, {}, lambda msg=None: None)
    header.pack(side="top", fill="x", padx=10, pady=6)

    # ---------- CHARTS ----------
    charts_frame, data_buffers, time_buffer = create_charts(main_frame, config, lambda *a, **k: None)
    charts_frame.pack(side="top", fill="both", expand=True, padx=10, pady=(4, 6))

    # ---------- LOG ----------
    log, _app_closing = create_log_frame(main_frame, config)
    log("🌱 Dashboard gestartet – Logsystem aktiv")

    # ---------- FOOTER ----------
    set_status, mark_data_update = create_footer(main_frame, config)
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
        try:
            with open(config.STATUS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            set_status(data.get("connected", False))
        except Exception:
            pass
        root.after(2000, update_status_from_file)

    update_status_from_file()

    # ---------- SHUTDOWN ----------
    def on_close():
        try:
            _app_closing[0] = True
        except Exception:
            pass
        try:
            from async_reader import stop_reader
            log("[🧹] Stoppe Async-Reader …")
            stop_reader()
        except Exception as e:
            log(f"⚠️ Fehler beim Stoppen des Readers: {e}")
        root.quit()
        root.after(50, root.destroy)

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()
