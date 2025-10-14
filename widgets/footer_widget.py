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

    # ---------- STATUS LINKS ----------
    status_frame = tk.Frame(footer, bg=config.CARD)
    status_frame.pack(side="left")

    status_led = tk.Canvas(status_frame, width=22, height=22, bg=config.CARD, highlightthickness=0)
    status_led.pack(side="left", padx=8)

    status_text = tk.Label(
        status_frame,
        text="Initializing...",
        bg=config.CARD,
        fg="gray",
        font=("Segoe UI", 11, "bold")
    )
    status_text.pack(side="left", padx=(0, 10))

    # ---------- SENSOR STATUS ----------
    sensor_text = tk.Label(
        status_frame,
        text="🌡️ Internal: —   🌡️ External: —",
        bg=config.CARD,
        fg="gray",
        font=("Segoe UI", 11)
    )
    sensor_text.pack(side="left", padx=(10, 10))

    last_update_time = [None]

    # ---------- STATUS-LED ----------
    def set_status(connected=None):
        """Setzt LED und Textzustand (geglättet, verhindert Flackern)."""
        status_led.delete("all")

        if connected is None:
            status_led.create_oval(2, 2, 20, 20, fill="gray", outline="")
            status_text.config(text="Initializing...", fg="gray")

        elif connected:
            status_led.create_oval(2, 2, 20, 20, fill="lime green", outline="")
            status_text.config(text="[🟢] Connected", fg="lime green")

        else:
            status_led.create_oval(2, 2, 20, 20, fill="red", outline="")
            status_text.config(text="[🔴] Disconnected", fg="red")

    def set_sensor_status(main_ok=False, ext_ok=False):
        """Aktualisiert die Sensorstatus-Anzeige."""
        internal = "✅" if main_ok else "⚠️"
        external = "✅" if ext_ok else "⚠️"
        color = "lime green" if main_ok or ext_ok else "orange"
        sensor_text.config(
            text=f"🌡️ Internal: {internal}     🌡️ External: {external}",
            fg=color
        )

    def mark_data_update():
        """Speichert Zeitpunkt letzter Datenaktualisierung (Dashboard-Kompatibilität)."""
        last_update_time[0] = datetime.datetime.now()

    # ---------- POLLING (geglättet) ----------
    def poll_status():
        """Überwacht status.json, geglättet (3 Polls Toleranz)."""
        if not hasattr(poll_status, "_fail_counter"):
            poll_status._fail_counter = 0
            poll_status._last_connected = None

        try:
            status = utils.safe_read_json(config.STATUS_FILE) or {}
            connected = status.get("connected", False)
            main_ok = status.get("sensor_ok_main", False)
            ext_ok = status.get("sensor_ok_ext", False)

            # --- Glättung (Debounce) ---
            if connected:
                poll_status._fail_counter = 0
                if poll_status._last_connected is not True:
                    set_status(True)
                poll_status._last_connected = True
            else:
                poll_status._fail_counter += 1
                if poll_status._fail_counter >= 3:
                    if poll_status._last_connected is not False:
                        set_status(False)
                    poll_status._last_connected = False

            # --- Sensorstatus direkt aktualisieren ---
            set_sensor_status(main_ok, ext_ok)

        except Exception as e:
            print(f"⚠️ Footer Poll Error: {e}")

        parent.after(2000, poll_status)

    # ---------- INITIAL STATUS ----------
    try:
        current = utils.safe_read_json(config.STATUS_FILE) or {}
        set_status(current.get("connected"))
        set_sensor_status(
            current.get("sensor_ok_main", False),
            current.get("sensor_ok_ext", False)
        )
        last_update_time[0] = datetime.datetime.now()
    except Exception:
        set_status(None)

    poll_status()

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
