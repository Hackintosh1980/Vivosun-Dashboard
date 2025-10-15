#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_window.py – 🌿 Themefähiges Testfenster mit ausgelagertem Live-Chart.
"""

import tkinter as tk
from PIL import Image, ImageTk
import utils, config
from widgets.footer_widget import create_footer
from widgets.test_chart_widget import create_chart_widget

THEME = getattr(config, "THEME", None) or config


def open_window(parent, config=config, utils=utils):
    win = tk.Toplevel(parent)
    win.title("🧪 VIVOSUN – Live Data Window")
    win.geometry("1100x750")
    win.configure(bg=THEME.BG_MAIN)

    # ---------- HEADER ----------
    header = THEME.make_frame(win, bg=THEME.CARD_BG)
    header.pack(side="top", fill="x", padx=10, pady=(8, 12))

    # Logo
    try:
        img = Image.open("assets/Logo.png").resize((60, 60))
        logo = ImageTk.PhotoImage(img)
        lbl_logo = tk.Label(header, image=logo, bg=THEME.CARD_BG)
        lbl_logo.image = logo
        lbl_logo.pack(side="left", padx=(5, 10))
    except Exception:
        tk.Label(header, text="🌱", bg=THEME.CARD_BG, fg=THEME.TEXT,
                 font=("Segoe UI", 28, "bold")).pack(side="left", padx=(5, 10))

    tk.Label(
        header,
        text="VIVOSUN Live Data Test Window",
        bg=THEME.CARD_BG,
        fg=THEME.BTN_PRIMARY,
        font=THEME.FONT_TITLE
    ).pack(side="left", padx=(10, 20))

    # ---------- CHART ----------
    chart_wrapper = THEME.make_frame(win, bg=THEME.BG_MAIN, padx=20, pady=20)
    chart_wrapper.pack(fill="both", expand=True)

    chart_frame, reset_chart, stop_chart = create_chart_widget(chart_wrapper, theme=THEME)
    chart_frame.pack(fill="both", expand=True)

    THEME.make_button(
        header,
        "🔄 Reset Chart",
        reset_chart,
        color=getattr(THEME, "BTN_RESET", "#FF8844")
    ).pack(side="right", padx=10, pady=6)

    # ---------- FOOTER ----------
    footer = THEME.make_frame(win, bg=THEME.CARD_BG)
    footer.pack(fill="x", side="bottom", pady=(4, 8))

    set_status, mark_data_update, set_sensor_status = create_footer(win, config)
    try:
        set_status(False)
        set_sensor_status(False, False)
    except Exception:
        pass

    # ---------- STATUS POLLING ----------
    def poll_status():
        try:
            data = utils.safe_read_json(config.STATUS_FILE) or {}
            set_status(data.get("connected", False))
            set_sensor_status(data.get("sensor_ok_main", False), data.get("sensor_ok_ext", False))
        except Exception:
            pass
        win.after(2000, poll_status)

    poll_status()

    # ---------- CLEANUP ----------
    def on_close():
        try:
            stop_chart()
        except Exception:
            pass
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", on_close)
    return win
