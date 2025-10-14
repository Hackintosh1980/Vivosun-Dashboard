#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dummy_buttons_green.py – VIVOSUN-Look mit viel Grün 💚
"""

import tkinter as tk

# -----------------------------------------------------
# Farben & Fonts – „full green mode“
# -----------------------------------------------------
BG_MAIN   = "#06110f"       # noch dunkleres Grün-Schwarz
CARD_BG   = "#0d231d"       # weiches Dunkelgrün für Karten
LIME      = "#a8ff60"       # Hauptakzent
LIME_DARK = "#66cc33"
TEXT      = "#e5ffe5"
FONT_TITLE = ("Segoe UI", 22, "bold")
FONT_LABEL = ("Segoe UI", 12, "bold")
FONT_BTN   = ("Segoe UI", 12, "bold")

# -----------------------------------------------------
# Helper – Buttons & Stepper
# -----------------------------------------------------
def styled_button(master, text, cmd=None, color=LIME):
    return tk.Button(
        master, text=text, command=cmd,
        bg=color, fg="black", font=FONT_BTN,
        activebackground=LIME_DARK, activeforeground="black",
        relief="flat", padx=14, pady=9, cursor="hand2",
        highlightbackground=LIME_DARK, highlightcolor=LIME_DARK, highlightthickness=2
    )


def add_stepper_field(parent, label, var, step, unit=""):
    frame = tk.Frame(parent, bg=CARD_BG, highlightbackground=LIME_DARK, highlightthickness=1, padx=6, pady=6)

    tk.Label(frame, text=label, bg=CARD_BG, fg=LIME, font=FONT_LABEL).grid(row=0, column=0, rowspan=2, sticky="w")

    entry = tk.Entry(
        frame, textvariable=var, width=7, justify="center",
        bg="#072017", fg=TEXT, insertbackground=TEXT,
        relief="flat", highlightthickness=2, highlightcolor=LIME
    )
    entry.grid(row=0, column=1, rowspan=2, padx=(10, 6))

    def step_val(delta):
        try:
            v = float(var.get()) + delta
        except Exception:
            v = 0.0
        var.set(round(v, 2))

    # große übereinander angeordnete Pfeile mit leuchtendem Grün
    tk.Button(frame, text="▲", bg=LIME, fg="black",
              font=("Segoe UI", 12, "bold"), width=3,
              relief="flat", command=lambda: step_val(+step)
             ).grid(row=0, column=2, padx=4, pady=1)

    tk.Button(frame, text="▼", bg=LIME, fg="black",
              font=("Segoe UI", 12, "bold"), width=3,
              relief="flat", command=lambda: step_val(-step)
             ).grid(row=1, column=2, padx=4, pady=1)

    if unit:
        tk.Label(frame, text=unit, bg=CARD_BG, fg=LIME,
                 font=("Segoe UI", 10, "bold")).grid(row=0, column=3, rowspan=2, padx=(6, 0))

    return frame


# -----------------------------------------------------
# Haupt-App
# -----------------------------------------------------
def run_dummy():
    root = tk.Tk()
    root.title("🌱 VIVOSUN Button & Offset Dummy – Full Green Edition")
    root.geometry("820x520")
    root.configure(bg=BG_MAIN)

    # Header
    tk.Label(root, text="🌱 VIVOSUN Green Theme Playground",
             bg=BG_MAIN, fg=LIME, font=FONT_TITLE).pack(pady=(25, 10))

    main_frame = tk.Frame(root, bg=CARD_BG, highlightbackground=LIME_DARK, highlightthickness=2)
    main_frame.pack(padx=20, pady=20, fill="both", expand=True)

    # Offsets
    left = tk.Frame(main_frame, bg=CARD_BG)
    left.pack(side="left", fill="y", padx=25, pady=20)

    leaf_offset = tk.DoubleVar(value=0.0)
    hum_offset  = tk.DoubleVar(value=0.0)

    add_stepper_field(left, "Leaf Offset (°C)", leaf_offset, 0.1, "°C").pack(pady=10)
    add_stepper_field(left, "Humidity Offset (%)", hum_offset, 0.5, "%").pack(pady=10)

    # Buttons
    right = tk.Frame(main_frame, bg=CARD_BG)
    right.pack(side="left", fill="both", expand=True, padx=40, pady=20)

    styled_button(right, "📈 Start Measurement").pack(fill="x", pady=8)
    styled_button(right, "💾 Export Data").pack(fill="x", pady=8)
    styled_button(right, "🧹 Reset Charts", color=LIME_DARK).pack(fill="x", pady=8)
    styled_button(right, "🗑 Delete Config", color="#88ff44").pack(fill="x", pady=8)
    styled_button(right, "🔄 Restart System", color="#c4ff80").pack(fill="x", pady=8)

    # Fußzeile
    footer = tk.Frame(root, bg=BG_MAIN)
    footer.pack(side="bottom", pady=12)
    tk.Label(footer, text="VIVOSUN Theme Prototype v2.4 – Green Overdrive 🌿",
             bg=BG_MAIN, fg=LIME, font=("Segoe UI", 10, "bold")).pack()

    root.mainloop()


if __name__ == "__main__":
    run_dummy()
