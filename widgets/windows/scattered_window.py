#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scattered_window.py – separates Modul-Fenster mit integriertem VPD-Scatter-Chart.
Mit Offset-Steuerung (Tastatur + Pfeile, voll themefähig).
"""

import tkinter as tk
from PIL import Image, ImageTk
import utils, config
from widgets.footer_widget import create_footer
from widgets.scattered_chart_widget import create_scattered_chart

# --- Aktives Theme laden (Fallback: config) ---
THEME = getattr(config, "THEME", None) or config


def open_window(parent, config=config, utils=utils):
    """Öffnet das Scattered-VPD-Fenster (mit Chart + Offsetsteuerung)."""
    # 🔁 Später importieren, um Circular Import zu vermeiden
    try:
        from main_gui.header_gui import set_offsets_from_outside
    except Exception:
        def set_offsets_from_outside(*a, **k): pass

    win = tk.Toplevel(parent)
    win.title("🌡️ VIVOSUN – VPD Scattered Window")
    win.geometry("1000x700")
    win.configure(bg=THEME.BG_MAIN if hasattr(THEME, "BG_MAIN") else THEME.BG)

    # ---------- HEADER ----------
    header = tk.Frame(win, bg=THEME.CARD_BG)
    header.pack(side="top", fill="x", padx=10, pady=6)

    # --- Logo ---
    logo_path = "assets/Logo.png"
    try:
        img = Image.open(logo_path).resize((60, 60))
        logo = ImageTk.PhotoImage(img)
        lbl_logo = tk.Label(header, image=logo, bg=THEME.CARD_BG)
        lbl_logo.image = logo
        lbl_logo.pack(side="left", padx=(5, 10))
    except Exception:
        tk.Label(header, text="🌱", bg=THEME.CARD_BG, fg=THEME.TEXT,
                 font=("Segoe UI", 26, "bold")).pack(side="left", padx=(5, 10))

    # --- Titel ---
    tk.Label(
        header,
        text="VPD Scattered Live View",
        bg=THEME.CARD_BG,
        fg=THEME.TEXT,
        font=("Segoe UI", 22, "bold")
    ).pack(side="left", padx=10)

    # ---------- OFFSET-STEUERUNG ----------
    controls = tk.Frame(header, bg=THEME.CARD_BG)
    controls.pack(side="right", padx=10, pady=6, anchor="e")

    # --- Leaf Offset ---
    tk.Label(controls, text="Leaf Offset (°C):",
             bg=THEME.CARD_BG, fg=THEME.TEXT, font=("Segoe UI", 10, "bold")
             ).grid(row=0, column=0, padx=4, pady=2, sticky="e")

    leaf_offset_var = tk.DoubleVar(value=float(config.leaf_offset_c[0]))

    entry_leaf = tk.Entry(controls, textvariable=leaf_offset_var, width=6,
                          bg=THEME.BG_MAIN, fg=THEME.TEXT, justify="center",
                          relief="flat", font=("Segoe UI", 11, "bold"))
    entry_leaf.grid(row=0, column=1, padx=4)

    def change_leaf_offset(delta):
        new_val = round(leaf_offset_var.get() + delta, 1)
        leaf_offset_var.set(new_val)
        set_offsets_from_outside(leaf=new_val, hum=None, persist=True)

    tk.Button(controls, text="▲", font=("Segoe UI", 11, "bold"),
              bg=THEME.LIME, fg="black", relief="flat",
              command=lambda: change_leaf_offset(+0.1)
              ).grid(row=0, column=2, padx=2)
    tk.Button(controls, text="▼", font=("Segoe UI", 11, "bold"),
              bg=THEME.LIME, fg="black", relief="flat",
              command=lambda: change_leaf_offset(-0.1)
              ).grid(row=0, column=3, padx=2)

    # --- Humidity Offset ---
    tk.Label(controls, text="Humidity Offset (%):",
             bg=THEME.CARD_BG, fg=THEME.TEXT, font=("Segoe UI", 10, "bold")
             ).grid(row=1, column=0, padx=4, pady=2, sticky="e")

    hum_offset_var = tk.DoubleVar(value=float(config.humidity_offset[0]))

    entry_hum = tk.Entry(controls, textvariable=hum_offset_var, width=6,
                         bg=THEME.BG_MAIN, fg=THEME.TEXT, justify="center",
                         relief="flat", font=("Segoe UI", 11, "bold"))
    entry_hum.grid(row=1, column=1, padx=4)

    def change_hum_offset(delta):
        new_val = round(hum_offset_var.get() + delta, 1)
        hum_offset_var.set(new_val)
        set_offsets_from_outside(leaf=None, hum=new_val, persist=True)

    tk.Button(controls, text="▲", font=("Segoe UI", 11, "bold"),
              bg=THEME.LIME, fg="black", relief="flat",
              command=lambda: change_hum_offset(+1.0)
              ).grid(row=1, column=2, padx=2)
    tk.Button(controls, text="▼", font=("Segoe UI", 11, "bold"),
              bg=THEME.LIME, fg="black", relief="flat",
              command=lambda: change_hum_offset(-1.0)
              ).grid(row=1, column=3, padx=2)

    # --- Tastatursteuerung ---
    def on_key(event):
        w = win.focus_get()
        if event.keysym in ("Up", "Down"):
            if w == entry_leaf:
                change_leaf_offset(+0.1 if event.keysym == "Up" else -0.1)
            elif w == entry_hum:
                change_hum_offset(+1.0 if event.keysym == "Up" else -1.0)
        elif event.keysym == "Return":
            try:
                set_offsets_from_outside(
                    leaf=float(leaf_offset_var.get()),
                    hum=float(hum_offset_var.get()),
                    persist=True)
            except Exception:
                pass

    win.bind("<KeyPress>", on_key)

    # --- Reset Button ---
    tk.Button(header,
              text="↺ Reset Offsets",
              bg=getattr(THEME, "ORANGE", "#ff8844"),
              fg="black", relief="flat",
              font=("Segoe UI", 11, "bold"),
              command=lambda: [
                  leaf_offset_var.set(0.0),
                  hum_offset_var.set(0.0),
                  set_offsets_from_outside(leaf=0.0, hum=0.0, persist=True)
              ]
              ).pack(side="right", padx=12)

    # ---------- BODY ----------
    body = tk.Frame(win, bg=THEME.BG_MAIN)
    body.pack(fill="both", expand=True, padx=20, pady=10)

    chart_frame, reset_chart, stop_chart = create_scattered_chart(body, config)
    chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

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

    # ---------- CLEANUP ----------
    def on_close():
        try:
            stop_chart()
        except Exception:
            pass
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", on_close)
    return win
