#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core_gui.py – Hauptfenster des 🌱 VIVOSUN Thermo Dashboard
Fix: feste Reihenfolge (Header → Charts → Footer → Log)
"""

import tkinter as tk
import json
from PIL import Image, ImageTk
from collections import deque

import config, utils
from main_gui.header_gui import build_header
from main_gui.charts_gui import create_charts
from widgets.footer_widget import create_footer
from main_gui.log_gui import create_log_frame
from async_reader import start_reader_thread, set_log_callback, set_status_callback


def run_app(device_id=None):
    root = tk.Tk()
    root.title(getattr(config, "APP_DISPLAY", "🌱 VIVOSUN Thermo Dashboard"))
    root.geometry("1600x900")
    root.configure(bg=getattr(config, "BG", "#0b1620"))

    # ---------- BASIS ----------
    data_buffers, time_buffer = {}, []


    # ---------- CHARTS ----------
    charts_frame, data_buffers, time_buffer = create_charts(root, config, lambda msg=None: None)
    charts_frame.pack(side="top", fill="both", expand=True, padx=10, pady=6)

    # ---------- HEADER ----------
    header = build_header(root, config, data_buffers, time_buffer, lambda msg=None: None)
    # Header visuell vor die Charts verschieben (oben halten!)
    header.pack(side="top", fill="x", padx=10, pady=8, before=charts_frame)    
    # ---------- FOOTER ----------
    footer_frame = tk.Frame(root, bg=config.CARD)
    footer_frame.pack(side="top", fill="x")
    set_status, mark_data_update = create_footer(footer_frame, config)
    try:
        set_status(False)
    except Exception:
        pass

    # ---------- LOG ----------
    log, _app_closing = create_log_frame(root, config)
    log("🌱 Dashboard gestartet – Logsystem aktiv")

    # ---------- CALLBACKS ----------
    set_log_callback(log)
    set_status_callback(set_status)
    try:
        start_reader_thread(device_id)
        log(f"🔌 Verbinde mit Gerät {device_id} ...")
    except Exception as e:
        log(f"❌ Fehler beim Starten des Readers: {e}")

    # ---------- STATUS WATCH ----------
    def update_status_from_file():
        try:
            with open(config.STATUS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            connected = data.get("connected", False)
            set_status(connected)
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
