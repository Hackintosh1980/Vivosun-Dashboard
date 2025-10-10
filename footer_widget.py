#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
footer_widget.py – universelles Footer-Widget für VIVOSUN Dashboard & Module
Erzeugt Status-LED + Info-Link, Rückgabe: (set_status, poll_status)
"""

import tkinter as tk
import webbrowser
import datetime
import utils, config   # 🆕 wir brauchen Zugriff auf status.json

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
        text="Disconnected",
        bg=config.CARD,
        fg="orange",
        font=("Segoe UI", 11, "bold")
    )
    status_text.pack(side="left")

    # interner Zeitstempel 🆕
    last_update_time = [None]

    def set_status(connected=True):
        """Extern aufrufbar: LED direkt setzen"""
        status_led.delete("all")
        if connected:
            status_led.create_oval(2, 2, 20, 20, fill="lime green", outline="")
            status_text.config(text="Connected", fg="lime green")
        else:
            status_led.create_oval(2, 2, 20, 20, fill="red", outline="")
            status_text.config(text="Disconnected", fg="red")

    set_status(False)

    # 🆕 --- Automatische LED-Logik über status.json + freshness ---
    def poll_status():
        """Wird periodisch aufgerufen (z. B. alle 2 s)"""
        now = datetime.datetime.now()
        status = utils.safe_read_json(config.STATUS_FILE) or {}
        status_connected = status.get("connected", False)

        if last_update_time[0] is None:
            connected = False
        else:
            delta = (now - last_update_time[0]).total_seconds()
            connected = delta < 30

        final_connected = connected and status_connected
        set_status(final_connected)

        # nächste Prüfung planen (Tkinter-Loop)
        parent.after(2000, poll_status)

    def mark_data_update():
        """Von der GUI aufrufen, wenn neue Sensordaten eintreffen."""
        last_update_time[0] = datetime.datetime.now()

    # 🆕 Erste Poll-Runde starten
    parent.after(2000, poll_status)

    # ---------- INFO RECHTS ----------
    info = tk.Label(
        footer,
        text="🌱 Vivosun Dashboard v1.2.2  •  👨‍💻 Dominik Hackintosh  •  GitHub: sormy/vivosun-thermo",
        bg=config.CARD,
        fg=config.TEXT,
        font=("Segoe UI", 11),
        cursor="hand2"
    )
    info.pack(side="right")

    def open_github(event):
        webbrowser.open("https://github.com/sormy/vivosun-thermo")

    info.bind("<Button-1>", open_github)

    # 🆕 Wir geben jetzt 2 Funktionen zurück:
    return set_status, mark_data_update
