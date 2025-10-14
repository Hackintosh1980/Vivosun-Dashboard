#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
footer_widget.py – universelles Footer-Widget für VIVOSUN Dashboard & Module
Zeigt Verbindungsstatus + interne & externe Sensorzustände an.
Lesbar aus status.json (connected, sensor_ok_main, sensor_ok_ext)
"""

import tkinter as tk
import webbrowser
import datetime
import utils, config


def create_footer(parent, config):
    footer = tk.Frame(parent, bg=config.CARD)
    footer.pack(side="bottom", fill="x", padx=10, pady=6)

    # ---------- STATUS-LINKS ----------
    status_frame = tk.Frame(footer, bg=config.CARD)
    status_frame.pack(side="left")

    # Verbindung-LED
    status_led = tk.Canvas(status_frame, width=22, height=22, bg=config.CARD, highlightthickness=0)
    status_led.pack(side="left", padx=8)

    status_text = tk.Label(
        status_frame,
        text="[⚪] Initializing...",
        bg=config.CARD,
        fg="gray",
        font=("Segoe UI", 11, "bold")
    )
    status_text.pack(side="left", padx=(0, 10))

    # Sensorstatus-Anzeige
    sensor_text = tk.Label(
        status_frame,
        text="🌡️ Internal: ⏳     🌡️ External: ⏳",
        bg=config.CARD,
        fg=config.TEXT,
        font=("Segoe UI", 11, "bold")
    )
    sensor_text.pack(side="left")

    last_update_time = [None]
    disconnect_counter = [0]
    _last_state = [None]

    # ---------- Statusfunktionen ----------
    def set_status(connected=None):
        """Aktualisiert Verbindungsstatus-LED und Text."""
        if _last_state[0] == connected:
            return
        _last_state[0] = connected

        status_led.delete("all")

        if connected is None:
            status_led.create_oval(2, 2, 20, 20, fill="gray", outline="")
            status_text.config(text="[⚪] Initializing...", fg="gray")

        elif connected:
            status_led.create_oval(2, 2, 20, 20, fill="lime green", outline="")
            status_text.config(text="[🟢] Connected", fg="lime green")

        else:
            status_led.create_oval(2, 2, 20, 20, fill="red", outline="")
            status_text.config(text="[🔴] Disconnected", fg="red")

    def set_sensor_status(internal_ok=None, external_ok=None):
        """Aktualisiert die Anzeige der internen / externen Sensoren."""
        if internal_ok is None and external_ok is None:
            sensor_text.config(text="🌡️ Internal: ⏳     🌡️ External: ⏳")
            return

        int_symbol = "✅" if internal_ok else "❌"
        ext_symbol = "✅" if external_ok else "❌"
        sensor_text.config(
            text=f"🌡️ Internal: {int_symbol}     🌡️ External: {ext_symbol}"
        )

    # ---------- Sofortstatus prüfen ----------
    try:
        current = utils.safe_read_json(config.STATUS_FILE) or {}
        set_status(current.get("connected", None))
        set_sensor_status(
            current.get("sensor_ok_main"),
            current.get("sensor_ok_ext")
        )
        last_update_time[0] = datetime.datetime.now()
    except Exception:
        set_status(None)
        set_sensor_status(None, None)

    # ---------- Polling ----------
    def poll_status():
        now = datetime.datetime.now()
        status = utils.safe_read_json(config.STATUS_FILE) or {}
        status_connected = status.get("connected", False)

        if last_update_time[0] is None:
            last_update_time[0] = now

        delta = (now - last_update_time[0]).total_seconds()
        fresh = delta < 30

        if status_connected and fresh:
            disconnect_counter[0] = 0
            set_status(True)
        else:
            disconnect_counter[0] += 1
            if disconnect_counter[0] >= 3:
                set_status(False)

        set_sensor_status(
            status.get("sensor_ok_main"),
            status.get("sensor_ok_ext")
        )

        parent.after(2000, poll_status)

    def mark_data_update():
        last_update_time[0] = datetime.datetime.now()

    parent.after(2000, poll_status)

    # ---------- INFO-LABEL ----------
    info = tk.Label(
        footer,
        text="🌱 Vivosun Dashboard v1.2.3  •  👨‍💻 Dominik Hackintosh  •  GitHub: Hackintosh1980/Vivosun-Dashboard",
        bg=config.CARD,
        fg=config.TEXT,
        font=("Segoe UI", 11),
        cursor="hand2"
    )
    info.pack(side="right")

    def open_github(event):
        webbrowser.open("https://github.com/Hackintosh1980/Vivosun-Dashboard")

    info.bind("<Button-1>", open_github)

    return set_status, mark_data_update, set_sensor_status


def create_footer_light(parent, config=None):
    """Kleiner Footer ohne Statusanzeige – nur Version & GitHub-Link."""
    bg = getattr(config, "CARD", "#1e2a38")
    fg = getattr(config, "TEXT", "white")

    footer = tk.Frame(parent, bg=bg)
    footer.pack(side="bottom", fill="x", padx=10, pady=6)

    info = tk.Label(
        footer,
        text="🌱 Vivosun Dashboard v1.2.3  •  👨‍💻 Dominik Hackintosh  •  GitHub: Hackintosh1980/Vivosun-Dashboard",
        bg=bg,
        fg=fg,
        font=("Segoe UI", 11),
        cursor="hand2"
    )
    info.pack(side="right")

    def open_github(event):
        webbrowser.open("https://github.com/Hackintosh1980/Vivosun-Dashboard")

    info.bind("<Button-1>", open_github)

    return footer
