#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
settings_gui.py – 🌱 VIVOSUN Dashboard Settings (voll theme-fähig)
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os, sys, config, utils
from main_gui import theme_picker
from themes import theme_vivosun, theme_oceanic

try:
    from themes import theme_sunset
    THEMES = {
        "🌿 VIVOSUN Green": theme_vivosun,
        "🌊 Oceanic Blue": theme_oceanic,
        "🔥 VIVOSUN Sunset": theme_sunset,
    }
except ImportError:
    THEMES = {
        "🌿 VIVOSUN Green": theme_vivosun,
        "🌊 Oceanic Blue": theme_oceanic,
    }


def open_settings_window(root=None, log=None):
    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    theme_name = cfg.get("theme", "🌿 VIVOSUN Green")
    theme = THEMES.get(theme_name, theme_vivosun)

    win = tk.Toplevel(root)
    win.title("🌱 VIVOSUN Dashboard – Settings")
    win.geometry("820x920")
    win.configure(bg=theme.BG_MAIN)

    # ---------- HEADER ----------
    header = theme.make_frame(win, bg=theme.CARD_BG)
    header.pack(fill="x", pady=(6, 10))

    try:
        img = Image.open(os.path.join("assets", "logo.png")).resize((64, 64))
        logo = ImageTk.PhotoImage(img)
        tk.Label(header, image=logo, bg=theme.CARD_BG).pack(side="left", padx=20, pady=10)
        header.image = logo
    except Exception:
        pass

    tk.Label(
        header,
        text="⚙️ Dashboard Settings",
        bg=theme.CARD_BG,
        fg=theme.BTN_PRIMARY,
        font=theme.FONT_TITLE
    ).pack(side="left", padx=10)

    # ---------- BODY ----------
    body = theme.make_frame(win, bg=theme.BG_MAIN, padx=40, pady=25)
    body.pack(fill="both", expand=True)

    # === Theme Picker ===
    tk.Label(
        body, text="🎨 Theme:",
        bg=theme.BG_MAIN, fg=theme.TEXT,
        font=theme.FONT_LABEL
    ).grid(row=0, column=0, sticky="w", pady=8)

    def on_theme_change(new_name):
        new_theme = theme_picker.get_available_themes().get(new_name)
        if new_theme:
            theme_picker.save_theme_to_config(new_name)
            win.destroy()
            open_settings_window(root, log)

    theme_dropdown, theme_var = theme_picker.create_theme_picker(
        body, current_theme=theme_name, on_change=on_theme_change
    )
    theme_dropdown.grid(row=0, column=1, sticky="w", pady=8)

    # --- CONFIG VARIABLEN ---
    device_id = cfg.get("device_id", "")
    var_unit = tk.BooleanVar(value=cfg.get("unit_celsius", True))
    var_rec = tk.DoubleVar(value=cfg.get("RECONNECT_DELAY", config.RECONNECT_DELAY))
    var_poll = tk.DoubleVar(value=cfg.get("SENSOR_POLL_INTERVAL", config.SENSOR_POLL_INTERVAL))
    var_tdec = tk.IntVar(value=cfg.get("TEMP_DECIMALS", 1))
    var_hdec = tk.IntVar(value=cfg.get("HUMID_DECIMALS", 1))
    var_vdec = tk.IntVar(value=cfg.get("VPD_DECIMALS", 2))
    var_dev = tk.StringVar(value=device_id)
    debug_var = tk.BooleanVar(value=cfg.get("debug_logging", True))

    def add_row(row, label, widget):
        tk.Label(body, text=label, bg=theme.BG_MAIN, fg=theme.TEXT,
                 font=theme.FONT_LABEL, anchor="w").grid(row=row, column=0, sticky="w", pady=8)
        widget.grid(row=row, column=1, sticky="w", pady=8)

    # === Rows ===
    unit_frame = theme.make_frame(body, bg=theme.BG_MAIN)
    for text, val in [("Celsius (°C)", True), ("Fahrenheit (°F)", False)]:
        tk.Radiobutton(unit_frame, text=text, variable=var_unit, value=val,
                       bg=theme.BG_MAIN, fg=theme.TEXT,
                       selectcolor=theme.CARD_BG, activebackground=theme.BG_MAIN).pack(side="left", padx=8)
    add_row(1, "Temperature Unit:", unit_frame)

    # Spinboxes mit Themefarben
    def make_spinbox(var, to, inc=0.001):
        return tk.Spinbox(
            body, textvariable=var, from_=0.001, to=to, increment=inc,
            width=10, bg=theme.CARD_BG, fg=theme.TEXT,
            relief="flat", justify="center"
        )

    add_row(2, "Reconnect Delay (s):", make_spinbox(var_rec, 120.000))
    add_row(3, "Sensor Poll (s):", make_spinbox(var_poll, 60.000))

    tk.Label(body, text="─" * 50, bg=theme.BG_MAIN, fg=theme.TEXT_DIM).grid(row=4, column=0, columnspan=2, pady=10)

    add_row(5, "Temperature Decimals:", make_spinbox(var_tdec, 3, 1))
    add_row(6, "Humidity Decimals:", make_spinbox(var_hdec, 3, 1))
    add_row(7, "VPD Decimals:", make_spinbox(var_vdec, 3, 1))

    tk.Label(body, text="─" * 50, bg=theme.BG_MAIN, fg=theme.TEXT_DIM).grid(row=8, column=0, columnspan=2, pady=10)

    entry_dev = tk.Entry(body, textvariable=var_dev, width=28, bg=theme.CARD_BG, fg=theme.TEXT, relief="flat")
    add_row(9, "Device ID:", entry_dev)

    debug_frame = theme.make_frame(body, bg=theme.BG_MAIN)
    tk.Checkbutton(debug_frame, text="🪲 Debug-Logging aktivieren", variable=debug_var,
                   bg=theme.BG_MAIN, fg=theme.TEXT, selectcolor=theme.CARD_BG,
                   activebackground=theme.BG_MAIN, font=theme.FONT_LABEL).pack(side="left", padx=6)
    add_row(10, "Debug Mode:", debug_frame)

    # ---------- FOOTER ----------
    footer = theme.make_frame(win, bg=theme.CARD_BG)
    footer.pack(fill="x", pady=(10, 0))

    def save_settings():
        try:
            cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
            cfg.update({
                "device_id": var_dev.get(),
                "unit_celsius": var_unit.get(),
                "RECONNECT_DELAY": float(var_rec.get()),
                "SENSOR_POLL_INTERVAL": float(var_poll.get()),
                "TEMP_DECIMALS": int(var_tdec.get()),
                "HUMID_DECIMALS": int(var_hdec.get()),
                "VPD_DECIMALS": int(var_vdec.get()),
                "theme": theme_var.get(),
                "debug_logging": debug_var.get(),
            })
            utils.safe_write_json(config.CONFIG_FILE, cfg)
            messagebox.showinfo("Gespeichert", "💾 Einstellungen gespeichert.")
        except Exception as e:
            messagebox.showerror("Fehler", f"❌ Fehler beim Speichern: {e}")

    def reset_device_id():
        cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
        cfg["device_id"] = ""
        utils.safe_write_json(config.CONFIG_FILE, cfg)
        var_dev.set("")
        messagebox.showinfo("Reset", "🧩 Device-ID gelöscht.")

    def restart_program():
        messagebox.showinfo("Restart", "🔄 Das Dashboard wird neu gestartet.")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    # Theme-Buttons nutzen Theme-Farben
    theme.make_button(footer, "💾 Save", save_settings, color=theme.BTN_PRIMARY).pack(side="left", padx=20, pady=15)
    theme.make_button(footer, "🧩 Reset Device ID", reset_device_id, color=theme.BTN_SECONDARY).pack(side="left", padx=10, pady=15)
    theme.make_button(footer, "🔄 Restart", restart_program, color=theme.BTN_RESET).pack(side="left", padx=10, pady=15)
    theme.make_button(footer, "❌ Close", win.destroy, color=theme.ORANGE if hasattr(theme, "ORANGE") else "#FF4444").pack(side="right", padx=20, pady=15)

    return win
