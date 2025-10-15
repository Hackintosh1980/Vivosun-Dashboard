#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scattered_window.py – separates Modul-Fenster mit integriertem VPD-Scatter-Chart.
Mit Offset-Steuerung (Tastatur + Pfeile, global synchronisiert via utils.OffsetManager)
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
    win = tk.Toplevel(parent)
    win.title("🌡️ VIVOSUN – VPD Scattered Window")
    win.geometry("1400x900")
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

    # --- Config lesen ---
    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    use_celsius = cfg.get("unit_celsius", True)
    unit_label = "°C" if use_celsius else "°F"

    # --- Leaf Offset ---
    tk.Label(
        controls,
        text=f"Leaf Offset ({unit_label}):",
        bg=THEME.CARD_BG,
        fg=THEME.TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=0, padx=4, pady=2, sticky="e")

    leaf_offset_var = tk.StringVar(
        value=utils.format_offset_display(config.leaf_offset_c[0], use_celsius)
    )

    entry_leaf = tk.Entry(
        controls,
        textvariable=leaf_offset_var,
        width=6,
        bg=THEME.BG_MAIN,
        fg=THEME.TEXT,
        justify="center",
        relief="flat",
        font=("Segoe UI", 11, "bold")
    )
    entry_leaf.grid(row=0, column=1, padx=4)

    def apply_leaf_offset():
        """Manuelle Eingabe übernehmen (Return/Fokusverlust)."""
        try:
            new_val_c = utils.parse_offset_input(leaf_offset_var.get(), use_celsius)
            utils.set_offsets_from_outside(leaf=new_val_c, persist=True)
            leaf_offset_var.set(utils.format_offset_display(new_val_c, use_celsius))
        except Exception:
            pass

    def change_leaf_offset(delta):
        """Offset ändern – stabil für °C und °F (keine Button-Limitierung mehr)."""
        try:
            current_c = float(config.leaf_offset_c[0])  # immer echte °C
            step_c = delta if use_celsius else delta * 5.0 / 9.0
            new_val_c = round(current_c + step_c, 3)
            utils.set_offsets_from_outside(leaf=new_val_c, persist=True)
            leaf_offset_var.set(utils.format_offset_display(new_val_c, use_celsius))
        except Exception:
            pass

    tk.Button(
        controls, text="▲", font=("Segoe UI", 11, "bold"),
        bg=THEME.LIME, fg="black", relief="flat",
        command=lambda: change_leaf_offset(+0.1)
    ).grid(row=0, column=2, padx=2)

    tk.Button(
        controls, text="▼", font=("Segoe UI", 11, "bold"),
        bg=THEME.LIME, fg="black", relief="flat",
        command=lambda: change_leaf_offset(-0.1)
    ).grid(row=0, column=3, padx=2)

    entry_leaf.bind("<Return>", lambda e: apply_leaf_offset())
    entry_leaf.bind("<FocusOut>", lambda e: apply_leaf_offset())

    # --- Humidity Offset ---
    tk.Label(
        controls,
        text="Humidity Offset (%):",
        bg=THEME.CARD_BG,
        fg=THEME.TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=1, column=0, padx=4, pady=2, sticky="e")

    hum_offset_var = tk.StringVar(value=f"{float(config.humidity_offset[0]):.1f}")

    entry_hum = tk.Entry(
        controls,
        textvariable=hum_offset_var,
        width=6,
        bg=THEME.BG_MAIN,
        fg=THEME.TEXT,
        justify="center",
        relief="flat",
        font=("Segoe UI", 11, "bold")
    )
    entry_hum.grid(row=1, column=1, padx=4)

    def apply_hum_offset():
        try:
            new_val = round(float(hum_offset_var.get()), 1)
            utils.set_offsets_from_outside(hum=new_val, persist=True)
            hum_offset_var.set(f"{new_val:.1f}")
        except Exception:
            pass

    def change_hum_offset(delta):
        try:
            current = float(config.humidity_offset[0])
            new_val = round(current + delta, 1)
            utils.set_offsets_from_outside(hum=new_val, persist=True)
            hum_offset_var.set(f"{new_val:.1f}")
        except Exception:
            pass

    tk.Button(
        controls, text="▲", font=("Segoe UI", 11, "bold"),
        bg=THEME.LIME, fg="black", relief="flat",
        command=lambda: change_hum_offset(+1.0)
    ).grid(row=1, column=2, padx=2)

    tk.Button(
        controls, text="▼", font=("Segoe UI", 11, "bold"),
        bg=THEME.LIME, fg="black", relief="flat",
        command=lambda: change_hum_offset(-1.0)
    ).grid(row=1, column=3, padx=2)

    entry_hum.bind("<Return>", lambda e: apply_hum_offset())
    entry_hum.bind("<FocusOut>", lambda e: apply_hum_offset())

    # --- Tastatursteuerung ---
    def on_key(event):
        w = win.focus_get()
        if event.keysym in ("Up", "Down"):
            if w == entry_leaf:
                change_leaf_offset(+0.1 if event.keysym == "Up" else -0.1)
            elif w == entry_hum:
                change_hum_offset(+1.0 if event.keysym == "Up" else -1.0)
        elif event.keysym == "Return":
            apply_leaf_offset()
            apply_hum_offset()

    win.bind("<KeyPress>", on_key)
    
    # --- Reset Button ---
    THEME.make_button(
        header,
        "↺ Reset Offsets",
        lambda: utils.set_offsets_from_outside(leaf=0.0, hum=0.0, persist=True),
        color=getattr(THEME, "LIME", "#00FF88")
    ).pack(side="right", padx=12, pady=4)

    # --- 🔗 Globale Callback-Verbindung (Header -> Scatter) ---
    def on_global_offset_change(leaf_c, hum):
        leaf_offset_var.set(utils.format_offset_display(leaf_c, use_celsius))
        hum_offset_var.set(round(hum, 1))

    utils.register_offset_callback(on_global_offset_change)

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
