#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
footer_widget.py – universelles Footer-Widget (2 Zustände)
- Nur Grün/Rot (Connected/Disconnected)
- Kein "Initializing", flackerfreier Start (after_idle)
"""
import tkinter as tk
import webbrowser
import datetime
import utils, config


def create_footer(parent, config):
    footer = tk.Frame(parent, bg=config.CARD)
    footer.pack(side="bottom", fill="x", padx=10, pady=6)

    # ---------- STATUS ----------
    status_frame = tk.Frame(footer, bg=config.CARD)
    status_frame.pack(side="left")

    status_led = tk.Canvas(status_frame, width=22, height=22, bg=config.CARD, highlightthickness=0)
    status_led.pack(side="left", padx=8)

    status_text = tk.Label(
        status_frame,
        text="",  # kein Initialtext
        bg=config.CARD,
        fg="gray",
        font=("Segoe UI", 11, "bold")
    )
    status_text.pack(side="left")

    last_update_time = [None]
    disconnect_counter = [0]
    _last_state = [None]

    def set_status(arg1=None, arg2=None):
        """
        - set_status(True/False) → LED-Status (Dashboard)
        - set_status("Text", "Farbe") → Direkttext (optional für Submodule)
        """
        if isinstance(arg1, str) and arg2:
            status_led.delete("all")
            status_text.config(text=arg1, fg=arg2)
            return

        connected = bool(arg1)
        if _last_state[0] == connected:
            return
        _last_state[0] = connected

        status_led.delete("all")
        if connected:
            status_led.create_oval(2, 2, 20, 20, fill="lime green", outline="")
            status_text.config(text="Connected", fg="lime green")
        else:
            status_led.create_oval(2, 2, 20, 20, fill="red", outline="")
            status_text.config(text="Disconnected", fg="red")

    # ---------- Initialstatus nach GUI-Render ----------
    def _init_status():
        try:
            current = utils.safe_read_json(config.STATUS_FILE) or {}
            if current.get("connected", False):
                set_status(True)
                last_update_time[0] = datetime.datetime.now()
            else:
                set_status(False)
        except Exception:
            set_status(False)

    parent.after_idle(_init_status)

    # ---------- Polling ----------
    def poll_status():
        now = datetime.datetime.now()
        status = utils.safe_read_json(config.STATUS_FILE) or {}
        connected = status.get("connected", False)

        if last_update_time[0] is None:
            last_update_time[0] = now

        delta = (now - last_update_time[0]).total_seconds()
        fresh = delta < 30

        if connected and fresh:
            disconnect_counter[0] = 0
            set_status(True)
        else:
            disconnect_counter[0] += 1
            if disconnect_counter[0] >= 3:
                set_status(False)

        parent.after(2000, poll_status)

    def mark_data_update():
        last_update_time[0] = datetime.datetime.now()

    parent.after(2000, poll_status)

    # ---------- INFO-LABEL ----------
    info = tk.Label(
        footer,
        text="🌱 Vivosun Dashboard  •  👨‍💻 Dominik Hackintosh  •  GitHub: Hackintosh1980/Vivosun-Dashboard",
        bg=config.CARD,
        fg=config.TEXT,
        font=("Segoe UI", 11),
        cursor="hand2"
    )
    info.pack(side="right")

    def open_github(_event=None):
        webbrowser.open("https://github.com/Hackintosh1980/Vivosun-Dashboard")

    info.bind("<Button-1>", open_github)

    return set_status, mark_data_update


def create_footer_light(parent, config=None):
    """Kleiner Footer ohne Statusanzeige – nur Version & GitHub-Link."""
    bg = getattr(config, "CARD", "#1e2a38")
    fg = getattr(config, "TEXT", "white")

    footer = tk.Frame(parent, bg=bg)
    footer.pack(side="bottom", fill="x", padx=10, pady=6)

    info = tk.Label(
        footer,
        text="🌱 Vivosun Dashboard  •  👨‍💻 Dominik Hackintosh  •  GitHub: Hackintosh1980/Vivosun-Dashboard",
        bg=bg,
        fg=fg,
        font=("Segoe UI", 11),
        cursor="hand2"
    )
    info.pack(side="right")

    def open_github(_event=None):
        webbrowser.open("https://github.com/Hackintosh1980/Vivosun-Dashboard")

    info.bind("<Button-1>", open_github)

    return footer
