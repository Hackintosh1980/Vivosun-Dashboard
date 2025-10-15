#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_window.py – 🌿 Themefähiges Testfenster mit kompaktem Live-Chart (6 Kurven)
Chart expandiert kontrolliert, Footer bleibt immer sichtbar.
"""

import tkinter as tk
from PIL import Image, ImageTk
import utils, config
from widgets.footer_widget import create_footer
from widgets.test_chart_widget import create_chart_widget  # dein Chart-Modul

# --- Aktives Theme laden ---
THEME = getattr(config, "THEME", None) or config


def open_window(parent, config=config, utils=utils):
    """Öffnet das Testfenster (kompakt, Theme-aware, Live-Daten)."""
    win = tk.Toplevel(parent)
    win.title("🧪 VIVOSUN – Live Data Test Window")
    win.geometry("1150x780")
    win.configure(bg=THEME.BG_MAIN)

    # ---------- HEADER ----------
    header = THEME.make_frame(win, bg=THEME.CARD_BG)
    header.pack(side="top", fill="x", padx=10, pady=(8, 10))

    # --- Logo ---
    try:
        img = Image.open("assets/Logo.png").resize((60, 60))
        logo = ImageTk.PhotoImage(img)
        lbl_logo = tk.Label(header, image=logo, bg=THEME.CARD_BG)
        lbl_logo.image = logo
        lbl_logo.pack(side="left", padx=(5, 10))
    except Exception:
        tk.Label(
            header, text="🌱",
            bg=THEME.CARD_BG, fg=THEME.TEXT,
            font=("Segoe UI", 28, "bold")
        ).pack(side="left", padx=(5, 10))

    # --- Titel ---
    tk.Label(
        header,
        text="VIVOSUN Live Data Window",
        bg=THEME.CARD_BG,
        fg=THEME.BTN_PRIMARY,
        font=THEME.FONT_TITLE
    ).pack(side="left", padx=(10, 20))

    # ---------- RESET BUTTON ----------
    reset_btn = THEME.make_button(
        header,
        "🔄 Reset Chart",
        None,
        color=THEME.BTN_RESET if hasattr(THEME, "BTN_RESET") else "#FF8844"
    )
    reset_btn.pack(side="right", padx=10, pady=6)

    # ---------- CHART AREA (kompakt, Footer-freundlich) ----------
    chart_area = THEME.make_frame(win, bg=THEME.BG_MAIN)
    chart_area.pack(fill="both", expand=True, padx=20, pady=(10, 10))

    # Fester Container, verhindert Überdehnung
    chart_container = tk.Frame(chart_area, bg=THEME.BG_MAIN, height=480)
    chart_container.pack(fill="x", pady=(10, 10))
    chart_container.pack_propagate(False)  # verhindert unendliche Expansion

    # Chart erstellen
    chart_frame, reset_chart, stop_chart = create_chart_widget(chart_container, theme=THEME)
    chart_frame.pack(fill="both", expand=True)

    # Reset-Button-Funktion jetzt setzen
    reset_btn.config(command=reset_chart)

    # ---------- FOOTER ----------
    footer = THEME.make_frame(win, bg=THEME.CARD_BG)
    footer.pack(fill="x", side="bottom", pady=(6, 10))

    set_status, mark_data_update, set_sensor_status = create_footer(win, config)
    try:
        set_status(False)
        set_sensor_status(False, False)
    except Exception:
        pass

    # ---------- STATUS POLLING ----------
    def poll_status():
        """Aktualisiert Footer-Anzeige regelmäßig."""
        try:
            data = utils.safe_read_json(config.STATUS_FILE) or {}
            connected = data.get("connected", False)
            main_ok = data.get("sensor_ok_main", False)
            ext_ok = data.get("sensor_ok_ext", False)
            set_status(connected)
            set_sensor_status(main_ok, ext_ok)
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
