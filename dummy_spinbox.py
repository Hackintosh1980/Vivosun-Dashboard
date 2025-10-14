#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dummy_spinbox_window.py – stylischer Dummy mit großen VIVOSUN-Pfeilen
Eigenständig, Theme-aware, ersetzt klassische Spinbox durch eigene Pfeilsteuerung.
"""

import tkinter as tk
import os, sys

# --- Projektpfad hinzufügen ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

try:
    import config
except ImportError as e:
    print(f"⚠️ config.py konnte nicht geladen werden: {e}")
    sys.exit(1)


def open_window():
    win = tk.Tk()
    win.title("🌿 VIVOSUN Offset Control – Custom Arrows")
    win.geometry("720x320")
    win.configure(bg=config.BG)

    # ---------- HEADER ----------
    header = tk.Frame(win, bg=config.CARD)
    header.pack(side="top", fill="x", padx=10, pady=10)

    tk.Label(
        header,
        text="VIVOSUN Offset Dummy",
        bg=config.CARD,
        fg=config.TEXT,
        font=("Segoe UI", 22, "bold")
    ).pack(side="left", padx=10)

    tk.Label(
        header,
        text=f"🎨 Theme: {getattr(config, 'THEME_NAME', 'Default')}",
        bg=config.CARD,
        fg=config.TEXT,
        font=("Segoe UI", 12, "italic")
    ).pack(side="right", padx=10)

    # ---------- BODY ----------
    body = tk.Frame(win, bg=config.BG)
    body.pack(fill="both", expand=True, padx=20, pady=20)

    card = tk.Frame(body, bg=config.CARD, highlightthickness=1, highlightbackground="#333")
    card.pack(fill="x", padx=10, pady=10)

    # Farben für Pfeil-Buttons
    vivosun_green = "#00cc66"
    vivosun_dark = "#00994d"

    def make_arrow_button(parent, text, command):
        """Erzeugt stilisierten Pfeilbutton."""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            bg=vivosun_green,
            activebackground=vivosun_dark,
            fg="black",
            font=("Segoe UI", 18, "bold"),
            relief="flat",
            width=3,
            height=1,
            padx=6,
            pady=2,
            borderwidth=0,
            cursor="hand2"
        )
        btn.pack(side="left", padx=8)
        return btn

    # 🌿 Leaf Offset
    tk.Label(
        card,
        text="🌿 Leaf Offset (°C):",
        bg=config.CARD,
        fg=config.TEXT,
        font=("Segoe UI", 15, "bold")
    ).pack(side="left", padx=(12, 8))

    leaf_var = tk.DoubleVar(value=0.0)
    leaf_display = tk.Label(
        card,
        textvariable=leaf_var,
        bg=config.CARD,
        fg="lime",
        font=("Consolas", 22, "bold"),
        width=6,
        relief="flat",
        anchor="center"
    )
    leaf_display.pack(side="left", padx=4)

    def leaf_up(): leaf_var.set(round(leaf_var.get() + 0.1, 1))
    def leaf_down(): leaf_var.set(round(leaf_var.get() - 0.1, 1))

    make_arrow_button(card, "▲", leaf_up)
    make_arrow_button(card, "▼", leaf_down)

    # 💧 Humidity Offset
    tk.Label(
        card,
        text="💧 Humidity Offset (%):",
        bg=config.CARD,
        fg=config.TEXT,
        font=("Segoe UI", 15, "bold")
    ).pack(side="left", padx=(30, 8))

    hum_var = tk.DoubleVar(value=0.0)
    hum_display = tk.Label(
        card,
        textvariable=hum_var,
        bg=config.CARD,
        fg="#00ffff",
        font=("Consolas", 22, "bold"),
        width=6,
        relief="flat",
        anchor="center"
    )
    hum_display.pack(side="left", padx=4)

    def hum_up(): hum_var.set(round(hum_var.get() + 1.0, 1))
    def hum_down(): hum_var.set(round(hum_var.get() - 1.0, 1))

    make_arrow_button(card, "▲", hum_up)
    make_arrow_button(card, "▼", hum_down)

    # 🔁 Reset Button
    def reset_offsets():
        leaf_var.set(0.0)
        hum_var.set(0.0)

    tk.Button(
        card,
        text="↺ Reset",
        command=reset_offsets,
        bg="orange",
        fg="black",
        font=("Segoe UI", 12, "bold"),
        relief="flat",
        padx=14,
        pady=6
    ).pack(side="left", padx=20)

    win.mainloop()


if __name__ == "__main__":
    open_window()
