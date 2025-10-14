#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
settings_gui.py – 🌱 VIVOSUN Dashboard Settings (mit Theme-Picker, globaler Dezimalsteuerung & Restart + Debug Logging)
"""

import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import os, sys, config, utils

# ------------------------------------------------------------
# Themes laden
# ------------------------------------------------------------
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
    win.geometry("780x900")
    win.configure(bg=theme.BG_MAIN)

    # ---------- HEADER ----------
    header = theme.make_frame(win, bg=theme.CARD_BG)
    header.pack(fill="x", side="top")

    logo_path = os.path.join(os.path.dirname(__file__), "../assets/logo.png")
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path).resize((64, 64))
            logo = ImageTk.PhotoImage(img)
            logo_label = tk.Label(header, image=logo, bg=theme.CARD_BG)
            logo_label.image = logo
            logo_label.pack(side="left", padx=20, pady=12)
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
    body = theme.make_frame(win, bg=theme.BG_MAIN, padx=40, pady=30)
    body.pack(fill="both", expand=True)

    # --- Theme Picker ---
    tk.Label(body, text="🎨 Theme:", bg=theme.BG_MAIN, fg=theme.TEXT,
             font=theme.FONT_LABEL, anchor="w").grid(row=0, column=0, sticky="w", pady=8)
    theme_var = tk.StringVar(value=theme_name)
    theme_dropdown = ttk.Combobox(
        body, textvariable=theme_var,
        values=list(THEMES.keys()), state="readonly", width=25
    )
    theme_dropdown.grid(row=0, column=1, sticky="w", pady=8)

    style = ttk.Style()
    style.theme_use("default")
    style.configure("TCombobox",
                    fieldbackground=theme.CARD_BG,
                    background=theme.CARD_BG,
                    foreground=theme.TEXT,
                    arrowcolor=theme.TEXT)

    # --- Config Variablen ---
    device_id = cfg.get("device_id", "")
    unit_celsius = cfg.get("unit_celsius", True)
    reconnect = cfg.get("RECONNECT_DELAY", config.RECONNECT_DELAY)
    poll_int = cfg.get("SENSOR_POLL_INTERVAL", config.SENSOR_POLL_INTERVAL)
    temp_dec = cfg.get("TEMP_DECIMALS", getattr(config, "TEMP_DECIMALS", 1))
    hum_dec = cfg.get("HUMID_DECIMALS", getattr(config, "HUMID_DECIMALS", 1))
    vpd_dec = cfg.get("VPD_DECIMALS", getattr(config, "VPD_DECIMALS", 2))
    debug_enabled = cfg.get("debug_logging", True)

    var_unit = tk.BooleanVar(value=unit_celsius)
    var_rec = tk.DoubleVar(value=reconnect)
    var_poll = tk.DoubleVar(value=poll_int)
    var_dev = tk.StringVar(value=device_id)
    var_tdec = tk.IntVar(value=temp_dec)
    var_hdec = tk.IntVar(value=hum_dec)
    var_vdec = tk.IntVar(value=vpd_dec)
    debug_var = tk.BooleanVar(value=debug_enabled)

    # ---------- GRID LAYOUT ----------
    body.columnconfigure(0, weight=1)
    body.columnconfigure(1, weight=1)

    def add_row(row, label, widget):
        tk.Label(body, text=label, bg=theme.BG_MAIN, fg=theme.TEXT,
                 font=theme.FONT_LABEL, anchor="w").grid(row=row, column=0, sticky="w", pady=8)
        widget.grid(row=row, column=1, sticky="w", pady=8)

    # --- Einstellungen ---
    unit_frame = theme.make_frame(body, bg=theme.BG_MAIN)
    tk.Radiobutton(unit_frame, text="Celsius (°C)", variable=var_unit, value=True,
                   bg=theme.BG_MAIN, fg=theme.TEXT, selectcolor=theme.CARD_BG).pack(side="left", padx=8)
    tk.Radiobutton(unit_frame, text="Fahrenheit (°F)", variable=var_unit, value=False,
                   bg=theme.BG_MAIN, fg=theme.TEXT, selectcolor=theme.CARD_BG).pack(side="left", padx=8)
    add_row(1, "Temperature Unit:", unit_frame)

    add_row(2, "Reconnect Delay (s):",
            tk.Spinbox(body, textvariable=var_rec, from_=0.001, to=120.000,
                       increment=0.001, format="%.3f", width=10))
    add_row(3, "Sensor Poll (s):",
            tk.Spinbox(body, textvariable=var_poll, from_=0.001, to=60.000,
                       increment=0.001, format="%.3f", width=10))

    sep = tk.Label(body, text="─" * 50, bg=theme.BG_MAIN, fg=theme.TEXT_DIM)
    sep.grid(row=4, column=0, columnspan=2, pady=10)

    add_row(5, "Temperature Decimals:", tk.Spinbox(body, textvariable=var_tdec, from_=0, to=3, width=10))
    add_row(6, "Humidity Decimals:", tk.Spinbox(body, textvariable=var_hdec, from_=0, to=3, width=10))
    add_row(7, "VPD Decimals:", tk.Spinbox(body, textvariable=var_vdec, from_=0, to=3, width=10))

    sep2 = tk.Label(body, text="─" * 50, bg=theme.BG_MAIN, fg=theme.TEXT_DIM)
    sep2.grid(row=8, column=0, columnspan=2, pady=10)

    add_row(9, "Device ID:",
            tk.Entry(body, textvariable=var_dev, width=28,
                     bg=theme.CARD_BG, fg=theme.TEXT))

    # ---------- DEBUG LOGGING ----------
    debug_frame = theme.make_frame(body, bg=theme.BG_MAIN)
    tk.Checkbutton(
        debug_frame,
        text="🪲 Debug-Logging aktivieren",
        variable=debug_var,
        bg=theme.BG_MAIN,
        fg=theme.TEXT,
        selectcolor=theme.CARD_BG,
        activebackground=theme.BG_MAIN,
        font=theme.FONT_LABEL,
        anchor="w"
    ).pack(side="left", padx=6)
    add_row(10, "Debug Mode:", debug_frame)

    # ---------- FOOTER ----------
    footer = theme.make_frame(win, bg=theme.CARD_BG)
    footer.pack(fill="x", side="bottom", pady=(10, 0))

    def save_settings():
        """Speichert alle Änderungen (inkl. Theme & Dezimalpräzision)."""
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
                "debug_logging": debug_var.get(),  # ✅ neu
            })
            utils.safe_write_json(config.CONFIG_FILE, cfg)
            messagebox.showinfo("Gespeichert", "💾 Einstellungen gespeichert.")
            if log:
                log("💾 config.json aktualisiert (Settings gespeichert).")
        except Exception as e:
            messagebox.showerror("Fehler", f"❌ Fehler beim Speichern: {e}")

    def reset_device_id():
        try:
            cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
            cfg["device_id"] = ""
            utils.safe_write_json(config.CONFIG_FILE, cfg)
            var_dev.set("")
            messagebox.showinfo("Reset", "🧩 Device-ID gelöscht.")
        except Exception as e:
            messagebox.showerror("Fehler", f"⚠️ Device-ID Reset fehlgeschlagen: {e}")

    def restart_program():
        try:
            messagebox.showinfo("Restart", "🔄 Das Dashboard wird jetzt neu gestartet.")
            python = sys.executable
            os.execl(python, python, *sys.argv)
        except Exception as e:
            messagebox.showerror("Fehler", f"⚠️ Neustart fehlgeschlagen: {e}")

    # --- Buttons mit Theme-Farben ---
    theme.make_button(footer, "💾 Save", save_settings, color=theme.BTN_PRIMARY).pack(side="left", padx=20, pady=15)
    theme.make_button(footer, "🧩 Reset Device ID", reset_device_id, color=theme.BTN_SECONDARY).pack(side="left", padx=10, pady=15)
    theme.make_button(footer, "🔄 Restart Program", restart_program, color=theme.BTN_RESET).pack(side="left", padx=10, pady=15)
    theme.make_button(footer, "❌ Close", win.destroy, color=theme.ORANGE if hasattr(theme, "ORANGE") else "#FF4444").pack(side="right", padx=20, pady=15)

    def apply_selected_theme(event=None):
        new_theme = THEMES.get(theme_var.get(), theme)
        win.configure(bg=new_theme.BG_MAIN)
        header.configure(bg=new_theme.CARD_BG)
        body.configure(bg=new_theme.BG_MAIN)
        footer.configure(bg=new_theme.CARD_BG)

    theme_dropdown.bind("<<ComboboxSelected>>", apply_selected_theme)
    return win
