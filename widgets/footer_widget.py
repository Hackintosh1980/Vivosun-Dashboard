#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
footer_widget.py – universelles Footer-Widget für VIVOSUN Dashboard & Module
Erzeugt Status-LED + Info-Link, Rückgabe: (set_status, poll_status)
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
        text="Disconnected",
        bg=config.CARD,
        fg="orange",
        font=("Segoe UI", 11, "bold")
    )
    status_text.pack(side="left")

    last_update_time = [None]

    def set_status(connected=True):
        status_led.delete("all")
        if connected:
            status_led.create_oval(2, 2, 20, 20, fill="lime green", outline="")
            status_text.config(text="Connected", fg="lime green")
        else:
            status_led.create_oval(2, 2, 20, 20, fill="red", outline="")
            status_text.config(text="Disconnected", fg="red")

    set_status(False)

    def poll_status():
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

        parent.after(2000, poll_status)

    def mark_data_update():
        last_update_time[0] = datetime.datetime.now()

    parent.after(2000, poll_status)

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

    return set_status, mark_data_update


def create_footer_light(parent, config=None):
    """
    Kleiner Footer ohne Statusanzeige – nur Version & GitHub-Link.
    """
    bg = getattr(config, "CARD", "#1e2a38")
    fg = getattr(config, "TEXT", "white")

    footer = tk.Frame(parent, bg=bg)
    footer.pack(side="bottom", fill="x", padx=10, pady=6)

    info = tk.Label(
        footer,
        text="🌱 Vivosun Dashboard v1.2.2  •  👨‍💻 Dominik Hackintosh  •  GitHub: sormy/vivosun-thermo",
        bg=bg,
        fg=fg,
        font=("Segoe UI", 11),
        cursor="hand2"
    )
    info.pack(side="right")

    def open_github(event):
        webbrowser.open("https://github.com/sormy/vivosun-thermo")

    info.bind("<Button-1>", open_github)

    return footer
