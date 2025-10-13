#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
settings_gui.py – 🌱 VIVOSUN Dashboard Settings (mit globaler Dezimalsteuerung & Restart)
"""

import tkinter as tk
from tkinter import messagebox
import os, sys
from PIL import Image, ImageTk
import config, utils


def open_settings_window(root=None, log=None):
    win = tk.Toplevel(root)
    win.title("🌱 VIVOSUN Dashboard – Settings")
    win.geometry("780x600")
    win.configure(bg=config.BG)

    # ---------- HEADER ----------
    header = tk.Frame(win, bg=config.CARD, height=90)
    header.pack(fill="x", side="top")

    logo_path = os.path.join(os.path.dirname(__file__), "../assets/logo.png")
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path).resize((64, 64))
            logo = ImageTk.PhotoImage(img)
            logo_label = tk.Label(header, image=logo, bg=config.CARD)
            logo_label.image = logo
            logo_label.pack(side="left", padx=20, pady=12)
        except Exception:
            pass

    tk.Label(
        header,
        text="⚙️ Dashboard Settings",
        bg=config.CARD,
        fg=config.TEXT,
        font=("Segoe UI Semibold", 22)
    ).pack(side="left", padx=10)

    # ---------- BODY ----------
    body = tk.Frame(win, bg=config.BG, padx=40, pady=30)
    body.pack(fill="both", expand=True)

    # --- Konfigurationsdaten laden ---
    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    device_id = cfg.get("device_id", "")
    unit_celsius = cfg.get("unit_celsius", True)
    reconnect = cfg.get("RECONNECT_DELAY", config.RECONNECT_DELAY)
    poll_int = cfg.get("SENSOR_POLL_INTERVAL", getattr(config, "SENSOR_POLL_INTERVAL", 1))
    temp_dec = cfg.get("TEMP_DECIMALS", getattr(config, "TEMP_DECIMALS", 1))
    hum_dec = cfg.get("HUMID_DECIMALS", getattr(config, "HUMID_DECIMALS", 1))
    vpd_dec = cfg.get("VPD_DECIMALS", getattr(config, "VPD_DECIMALS", 2))

    # --- Variablen ---
    var_unit = tk.BooleanVar(value=unit_celsius)
    var_rec = tk.DoubleVar(value=reconnect)
    var_poll = tk.DoubleVar(value=poll_int)
    var_dev = tk.StringVar(value=device_id)
    var_tdec = tk.IntVar(value=temp_dec)
    var_hdec = tk.IntVar(value=hum_dec)
    var_vdec = tk.IntVar(value=vpd_dec)

    # ---------- GRID LAYOUT ----------
    body.columnconfigure(0, weight=1)
    body.columnconfigure(1, weight=1)

    def add_row(row, label, widget):
        tk.Label(body, text=label, bg=config.BG, fg=config.TEXT,
                 font=("Segoe UI", 11), anchor="w").grid(row=row, column=0, sticky="w", pady=8)
        widget.grid(row=row, column=1, sticky="w", pady=8)

    # --- Einstellungen ---
    unit_frame = tk.Frame(body, bg=config.BG)
    tk.Radiobutton(unit_frame, text="Celsius (°C)", variable=var_unit, value=True,
                   bg=config.BG, fg=config.TEXT, selectcolor=config.CARD).pack(side="left", padx=8)
    tk.Radiobutton(unit_frame, text="Fahrenheit (°F)", variable=var_unit, value=False,
                   bg=config.BG, fg=config.TEXT, selectcolor=config.CARD).pack(side="left", padx=8)
    add_row(0, "Temperature Unit:", unit_frame)

    add_row(1, "Reconnect Delay (s):",
            tk.Spinbox(body, textvariable=var_rec, from_=0.001, to=120.000,
                       increment=0.001, format="%.3f", width=10))
    add_row(2, "Sensor Poll (s):",
            tk.Spinbox(body, textvariable=var_poll, from_=0.001, to=60.000,
                       increment=0.001, format="%.3f", width=10))

    # --- Neue Sektion: Dezimalpräzision ---
    sep = tk.Label(body, text="─" * 50, bg=config.BG, fg="#555")
    sep.grid(row=3, column=0, columnspan=2, pady=10)

    add_row(4, "Temperature Decimals:", tk.Spinbox(body, textvariable=var_tdec, from_=0, to=3, width=10))
    add_row(5, "Humidity Decimals:", tk.Spinbox(body, textvariable=var_hdec, from_=0, to=3, width=10))
    add_row(6, "VPD Decimals:", tk.Spinbox(body, textvariable=var_vdec, from_=0, to=3, width=10))

    sep2 = tk.Label(body, text="─" * 50, bg=config.BG, fg="#555")
    sep2.grid(row=7, column=0, columnspan=2, pady=10)

    add_row(8, "Device ID:",
            tk.Entry(body, textvariable=var_dev, width=28,
                     bg="#2c3e50", fg=config.TEXT))

    # ---------- BUTTONS ----------
    footer = tk.Frame(win, bg=config.CARD)
    footer.pack(fill="x", side="bottom", pady=(10, 0))

    def save_settings():
        """Speichert alle Änderungen (inkl. Dezimalpräzision & Device-ID)."""
        try:
            cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
            new_cfg = {
                "device_id": var_dev.get(),
                "unit_celsius": var_unit.get(),
                "RECONNECT_DELAY": float(var_rec.get()),
                "SENSOR_POLL_INTERVAL": float(var_poll.get()),
                "TEMP_DECIMALS": int(var_tdec.get()),
                "HUMID_DECIMALS": int(var_hdec.get()),
                "VPD_DECIMALS": int(var_vdec.get()),
            }
            cfg.update(new_cfg)
            utils.safe_write_json(config.CONFIG_FILE, cfg)
            messagebox.showinfo("Gespeichert", "💾 Einstellungen gespeichert.")
            if log:
                log("💾 config.json aktualisiert (Settings gespeichert).")
        except Exception as e:
            messagebox.showerror("Fehler", f"❌ Fehler beim Speichern: {e}")

    def reset_device_id():
        """Setzt Device-ID auf leer zurück."""
        try:
            cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
            cfg["device_id"] = ""
            utils.safe_write_json(config.CONFIG_FILE, cfg)
            var_dev.set("")
            messagebox.showinfo("Reset", "🧩 Device-ID gelöscht.")
        except Exception as e:
            messagebox.showerror("Fehler", f"⚠️ Device-ID Reset fehlgeschlagen: {e}")

    def restart_program():
        """Startet das Dashboard neu."""
        try:
            messagebox.showinfo("Restart", "🔄 Das Dashboard wird jetzt neu gestartet.")
            python = sys.executable
            os.execl(python, python, *sys.argv)
        except Exception as e:
            messagebox.showerror("Fehler", f"⚠️ Neustart fehlgeschlagen: {e}")

    # Buttons
    tk.Button(footer, text="💾 Save", width=12, bg="#4CAF50", fg="white", relief="flat",
              font=("Segoe UI", 10, "bold"), command=save_settings).pack(side="left", padx=20, pady=15)
    tk.Button(footer, text="🧩 Reset Device ID", width=16, bg="#607D8B", fg="white", relief="flat",
              font=("Segoe UI", 10, "bold"), command=reset_device_id).pack(side="left", padx=10, pady=15)
    tk.Button(footer, text="🔄 Restart Program", width=16, bg="#2196F3", fg="white", relief="flat",
              font=("Segoe UI", 10, "bold"), command=restart_program).pack(side="left", padx=10, pady=15)
    tk.Button(footer, text="❌ Close", width=12, bg="#F44336", fg="white", relief="flat",
              font=("Segoe UI", 10, "bold"), command=win.destroy).pack(side="right", padx=20, pady=15)

    return win
