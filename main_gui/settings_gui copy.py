#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
settings_gui.py – 🌱 Dark Style Settings für das VIVOSUN Dashboard
Liest & schreibt config.json (device_id bleibt erhalten)
"""

import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import config, utils, os


def open_settings_window(root=None, log=None):
    """Öffnet das Settings-Fenster mit VIVOSUN-Style."""
    win = tk.Toplevel(root)
    win.title("🌱 VIVOSUN Dashboard – Settings")
    win.geometry("1200x900")
    win.configure(bg=config.BG)

    # ---------- HEADER ----------
    header = tk.Frame(win, bg=config.CARD, height=100)
    header.pack(fill="x", side="top")

    # Logo laden (aus /assets/logo.png)
    logo_path = os.path.join(os.path.dirname(__file__), "../assets/logo.png")
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path).resize((64, 64))
            logo = ImageTk.PhotoImage(img)
            logo_label = tk.Label(header, image=logo, bg=config.CARD)
            logo_label.image = logo
            logo_label.pack(side="left", padx=20, pady=15)
        except Exception:
            pass

    tk.Label(
        header,
        text="Dashboard Settings",
        bg=config.CARD,
        fg=config.TEXT,
        font=("Segoe UI Semibold", 22, "bold")
    ).pack(side="left", padx=10, pady=25)

    # ---------- BODY ----------
    body = tk.Frame(win, bg=config.BG, padx=30, pady=25)
    body.pack(fill="both", expand=True)

    tk.Label(
        body,
        text="🛠️ Konfiguration & Sensor-Einstellungen:",
        bg=config.BG,
        fg=config.TEXT,
        font=("Segoe UI", 13, "bold")
    ).pack(anchor="w", pady=(0, 15))

    # --- Werte laden ---
    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    unit_celsius = cfg.get("unit_celsius", True)
    leaf_off = cfg.get("leaf_offset_c", 0.0)
    hum_off = cfg.get("humidity_offset", 0.0)
    reconnect = cfg.get("RECONNECT_DELAY", config.RECONNECT_DELAY)
    poll_int = cfg.get("SENSOR_POLL_INTERVAL", getattr(config, "SENSOR_POLL_INTERVAL", 1))
    device_id = cfg.get("device_id", "")

    # --- Variablen ---
    var_unit = tk.BooleanVar(value=unit_celsius)
    var_leaf = tk.DoubleVar(value=leaf_off)
    var_hum = tk.DoubleVar(value=hum_off)
    var_rec = tk.IntVar(value=reconnect)
    var_poll = tk.DoubleVar(value=poll_int)
    var_dev = tk.StringVar(value=device_id)

    def add_row(label, widget):
        row = tk.Frame(body, bg=config.BG)
        row.pack(fill="x", pady=10)
        tk.Label(row, text=label, bg=config.BG, fg=config.TEXT, width=24, anchor="w", font=("Segoe UI", 11)).pack(side="left")
        widget.pack(side="left", padx=8)
        return row

    # ---- Temperature Unit ----
    unit_row = tk.Frame(body, bg=config.BG)
    tk.Label(unit_row, text="Temperature Unit:", bg=config.BG, fg=config.TEXT, width=24, anchor="w", font=("Segoe UI", 11)).pack(side="left")
    tk.Radiobutton(unit_row, text="Celsius (°C)", variable=var_unit, value=True,
                   bg=config.BG, fg=config.TEXT, selectcolor=config.CARD).pack(side="left", padx=6)
    tk.Radiobutton(unit_row, text="Fahrenheit (°F)", variable=var_unit, value=False,
                   bg=config.BG, fg=config.TEXT, selectcolor=config.CARD).pack(side="left", padx=6)
    unit_row.pack(anchor="w", pady=8)

    add_row("Leaf Offset (°C):", tk.Spinbox(body, textvariable=var_leaf, from_=-20.0, to=20.0, increment=0.1, width=10))
    add_row("Humidity Offset (%):", tk.Spinbox(body, textvariable=var_hum, from_=-50.0, to=50.0, increment=0.5, width=10))
    add_row("Reconnect Delay (s):", tk.Spinbox(body, textvariable=var_rec, from_=1, to=120, increment=1, width=10))
    add_row("Sensor Poll (s):", tk.Spinbox(body, textvariable=var_poll, from_=0.5, to=60.0, increment=0.5, width=10))
    add_row("Device ID (readonly):", tk.Entry(body, textvariable=var_dev, width=25, bg="#2c3e50", fg="#888", state="readonly"))

    # ---------- BUTTONS ----------
    footer = tk.Frame(win, bg=config.CARD, height=70)
    footer.pack(fill="x", side="bottom")

    def save_settings():
        """Speichert Änderungen in config.json, device_id bleibt erhalten."""
        try:
            cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
            dev = cfg.get("device_id", "")
            new_cfg = {
                "device_id": dev,
                "unit_celsius": var_unit.get(),
                "leaf_offset_c": float(var_leaf.get()),
                "humidity_offset": float(var_hum.get()),
                "RECONNECT_DELAY": int(var_rec.get()),
                "SENSOR_POLL_INTERVAL": float(var_poll.get()),
            }
            cfg.update(new_cfg)
            utils.safe_write_json(config.CONFIG_FILE, cfg)
            messagebox.showinfo("Gespeichert", "💾 Einstellungen erfolgreich gespeichert.")
            if log: log("💾 config.json aktualisiert (Settings).")
        except Exception as e:
            messagebox.showerror("Fehler", f"❌ Fehler beim Speichern: {e}")

    def reset_device_id():
        """Löscht nur device_id."""
        try:
            cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
            cfg["device_id"] = ""
            utils.safe_write_json(config.CONFIG_FILE, cfg)
            var_dev.set("")
            messagebox.showinfo("Reset", "🧩 Device-ID wurde gelöscht.")
            if log: log("🧩 Device-ID Reset durchgeführt.")
        except Exception as e:
            messagebox.showerror("Fehler", f"⚠️ Device-ID Reset fehlgeschlagen: {e}")

    def reset_settings():
        """Setzt Settings auf Default-Werte (device_id bleibt erhalten)."""
        try:
            cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
            dev = cfg.get("device_id", "")
            defaults = {
                "device_id": dev,
                "unit_celsius": True,
                "leaf_offset_c": config.leaf_offset_c[0],
                "humidity_offset": config.humidity_offset[0],
                "RECONNECT_DELAY": config.RECONNECT_DELAY,
                "SENSOR_POLL_INTERVAL": getattr(config, "SENSOR_POLL_INTERVAL", 1),
            }
            utils.safe_write_json(config.CONFIG_FILE, defaults)
            var_unit.set(True)
            var_leaf.set(config.leaf_offset_c[0])
            var_hum.set(config.humidity_offset[0])
            var_rec.set(config.RECONNECT_DELAY)
            var_poll.set(getattr(config, "SENSOR_POLL_INTERVAL", 1))
            messagebox.showinfo("Reset", "♻️ Settings auf Default zurückgesetzt.")
            if log: log("♻️ Settings Reset (device_id erhalten).")
        except Exception as e:
            messagebox.showerror("Fehler", f"⚠️ Reset fehlgeschlagen: {e}")

    # Buttons in einer Reihe
    tk.Button(footer, text="💾 Save", width=12, command=save_settings, bg="#4CAF50", fg="white",
              font=("Segoe UI", 10, "bold"), relief="flat").pack(side="left", padx=18, pady=15)

    tk.Button(footer, text="♻️ Reset", width=12, command=reset_settings, bg="#FF9800", fg="black",
              font=("Segoe UI", 10, "bold"), relief="flat").pack(side="left", padx=10, pady=15)

    tk.Button(footer, text="🧩 Reset Device ID", width=16, command=reset_device_id, bg="#607D8B", fg="white",
              font=("Segoe UI", 10, "bold"), relief="flat").pack(side="left", padx=10, pady=15)

    tk.Button(footer, text="❌ Close", width=12, command=win.destroy, bg="#F44336", fg="white",
              font=("Segoe UI", 10, "bold"), relief="flat").pack(side="right", padx=20, pady=15)

    return win
