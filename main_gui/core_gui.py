#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
core_gui.py – Hauptfenster des 🌱 VIVOSUN Thermo Dashboard
Optimierte Version:
- Sauberes Thread-Handling (kein Ctrl+C nötig)
- Flackerfreier Start
- Einheitliches Logging
"""
import tkinter as tk
import json

import config, utils
from main_gui.header_gui import build_header
from main_gui.charts_gui import create_charts
from widgets.footer_widget import create_footer
from main_gui.log_gui import create_log_frame
from async_reader import start_reader_thread, set_log_callback, set_status_callback, stop_reader


def run_app(device_id=None):
    # ---------- Hauptfenster ----------
    root = tk.Tk()
    root.title(getattr(config, "APP_DISPLAY", "🌱 VIVOSUN Thermo Dashboard"))
    root.geometry("1600x900")
    root.configure(bg=getattr(config, "BG", "#0b1620"))
    root.resizable(True, True)

    # ---------- LOG ----------
    log, _app_closing = create_log_frame(root, config)
    log("🌱 Dashboard gestartet – Logsystem aktiv")

    # ---------- CHARTS ----------
    charts_frame, data_buffers, time_buffer = create_charts(root, config, log)
    charts_frame.pack(side="top", fill="both", expand=True, padx=10, pady=6)

    # ---------- HEADER ----------
    header = build_header(root, config, data_buffers, time_buffer, log)
    header.pack(side="top", fill="x", padx=10, pady=8, before=charts_frame)

    # ---------- FOOTER ----------
    footer_frame = tk.Frame(root, bg=config.CARD)
    footer_frame.pack(side="top", fill="x")
    set_status, mark_data_update = create_footer(footer_frame, config)
    set_status(False)

    # ---------- CALLBACKS ----------
    set_log_callback(log)
    set_status_callback(set_status)

    # ---------- Async Reader starten ----------
    try:
        start_reader_thread(device_id)
        log(f"🔌 Verbinde mit Gerät {device_id or '(auto)'} …")
    except Exception as e:
        log(f"❌ Fehler beim Starten des Readers: {e}")

    # ---------- STATUS WATCH ----------
    def update_status_from_file():
        try:
            status = utils.safe_read_json(config.STATUS_FILE) or {}
            set_status(status.get("connected", False))
        except Exception:
            pass
        root.after(2000, update_status_from_file)

    root.after(1000, update_status_from_file)

    # ---------- Shutdown-Handler ----------
    def on_close():
        log("[🧹] Stoppe Dashboard …")
        _app_closing[0] = True

        try:
            log("⏹️ Stoppe Async-Reader …")
            stop_reader()
        except Exception as e:
            log(f"⚠️ Fehler beim Stoppen des Readers: {e}")

        # GUI beenden (kurze Verzögerung, damit Threads anhalten)
        def _finish():
            try:
                log("👋 Beende GUI …")
            except Exception:
                pass
            try:
                root.quit()
            finally:
                root.destroy()

        root.after(150, _finish)

    root.protocol("WM_DELETE_WINDOW", on_close)
    log("✅ System bereit – GUI aktiv")
    root.mainloop()
