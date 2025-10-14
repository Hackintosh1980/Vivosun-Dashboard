#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scattered_window.py – separates Modul-Fenster mit integriertem VPD-Scatter-Chart.
Nutzt die modulare Struktur (Header, Body, Footer).
"""

import tkinter as tk
from PIL import Image, ImageTk
import utils, config
from widgets.footer_widget import create_footer
from widgets.scattered_chart_widget import create_scattered_chart


def open_window(parent, config=config, utils=utils):
    """Öffnet das Scattered-VPD-Fenster."""
    win = tk.Toplevel(parent)
    win.title("🌡️ VIVOSUN – VPD Scattered Window")
    win.geometry("1000x700")
    win.configure(bg=config.BG)

    # ---------- HEADER ----------
    header = tk.Frame(win, bg=config.CARD)
    header.pack(side="top", fill="x", padx=10, pady=6)

    # Logo laden
    logo_path = "assets/Logo.png"
    try:
        img = Image.open(logo_path).resize((60, 60))
        logo = ImageTk.PhotoImage(img)
        lbl_logo = tk.Label(header, image=logo, bg=config.CARD)
        lbl_logo.image = logo
        lbl_logo.pack(side="left", padx=(5, 10))
    except Exception:
        lbl_logo = tk.Label(header, text="🌱", bg=config.CARD, fg=config.TEXT, font=("Segoe UI", 28))
        lbl_logo.pack(side="left", padx=(5, 10))

    tk.Label(
        header,
        text="VPD Scattered Live View",
        bg=config.CARD,
        fg=config.TEXT,
        font=("Segoe UI", 22, "bold")
    ).pack(side="left")

    # ---------- BODY (Chartbereich) ----------
    body = tk.Frame(win, bg=config.BG)
    body.pack(fill="both", expand=True, padx=20, pady=10)

    # Chartmodul einbinden
    chart_frame, reset_chart, stop_chart = create_scattered_chart(body, config)
    chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------- RESET BUTTON ----------
    tk.Button(
        header,
        text="🔄 Reset Chart",
        bg="#ff8844",
        fg="white",
        font=("Segoe UI", 12, "bold"),
        relief="flat",
        command=reset_chart
    ).pack(side="right", padx=10)

    # ---------- FOOTER ----------
    set_status, mark_data_update, set_sensor_status = create_footer(win, config)
    try:
        set_status(False)
        set_sensor_status(False, False)
    except Exception:
        pass

    # ---------- STATUS POLLING ----------
    def poll_status():
        """Liest status.json und aktualisiert Status & Sensoranzeige."""
        if not hasattr(poll_status, "_fail_counter"):
            poll_status._fail_counter = 0
            poll_status._last_connected = None

        try:
            data = utils.safe_read_json(config.STATUS_FILE) or {}

            connected = data.get("connected", False)
            main_ok = data.get("sensor_ok_main", False)
            ext_ok = data.get("sensor_ok_ext", False)

            if connected:
                poll_status._fail_counter = 0
                poll_status._last_connected = True
            else:
                poll_status._fail_counter += 1
                if poll_status._fail_counter >= 3:
                    poll_status._last_connected = False

            set_status(poll_status._last_connected)
            set_sensor_status(main_ok, ext_ok)

        except Exception:
            pass

        win.after(2000, poll_status)

    poll_status()

    # ---------- SHUTDOWN ----------
    def on_close():
        try:
            stop_chart()
        except Exception:
            pass
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", on_close)
    return win
