#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
settings_gui.py – Neustart: Dummy-Version mit klar sichtbarem Layout.
Dient als stabile Basis für die echten Settings später.
"""

import tkinter as tk


def open_settings_window(root=None, log=None):
    """Öffnet ein sauberes, garantiert sichtbares Dummy-Settings-Fenster."""
    win = tk.Toplevel(root)
    win.title("🌱 VIVOSUN Settings")
    win.geometry("600x500")
    win.configure(bg="#1a1a1a")

    # ----- HEADER -----
    header = tk.Frame(win, bg="#2e2e2e", height=80)
    header.pack(fill="x")

    tk.Label(
        header,
        text="⚙️ VIVOSUN Dashboard Settings",
        bg="#2e2e2e",
        fg="white",
        font=("Segoe UI", 18, "bold"),
        pady=20
    ).pack()

    # ----- BODY -----
    body = tk.Frame(win, bg="#1e1e1e", padx=20, pady=20)
    body.pack(fill="both", expand=True)

    tk.Label(
        body,
        text="Hier erscheinen später deine echten Einstellungen:",
        bg="#1e1e1e",
        fg="#aaaaaa",
        font=("Segoe UI", 12)
    ).pack(anchor="w", pady=(10, 20))

    # Dummy Einstellungen
    dummy_settings = [
        ("Temperature Unit", "°C / °F"),
        ("Leaf Offset", "0.0 °C"),
        ("Humidity Offset", "0.0 %"),
        ("Reconnect Delay", "3 s"),
        ("Sensor Poll Interval", "1.0 s"),
    ]

    for label, val in dummy_settings:
        row = tk.Frame(body, bg="#1e1e1e")
        row.pack(fill="x", pady=8)

        tk.Label(row, text=f"{label}:", bg="#1e1e1e", fg="white", width=20, anchor="w", font=("Segoe UI", 11)).pack(side="left")
        tk.Entry(row, width=20, bg="#333", fg="white", font=("Segoe UI", 11)).pack(side="left", padx=10)
        tk.Label(row, text=val, bg="#1e1e1e", fg="#888", font=("Segoe UI", 10, "italic")).pack(side="left")

    # ----- BUTTONS -----
    footer = tk.Frame(win, bg="#2e2e2e", height=60)
    footer.pack(fill="x", side="bottom")

    def on_save():
        print("💾 Settings saved (dummy)")
        if log:
            log("💾 Settings saved (dummy)")

    def on_defaults():
        print("♻️ Defaults loaded (dummy)")
        if log:
            log("♻️ Defaults loaded (dummy)")

    def on_close():
        print("❌ Settings closed")
        win.destroy()

    tk.Button(footer, text="💾 Save", width=10, command=on_save, bg="#4caf50", fg="white").pack(side="left", padx=20, pady=10)
    tk.Button(footer, text="♻️ Defaults", width=10, command=on_defaults, bg="#ff9800", fg="black").pack(side="left", padx=10, pady=10)
    tk.Button(footer, text="Close", width=10, command=on_close, bg="#f44336", fg="white").pack(side="right", padx=20, pady=10)

    return win
