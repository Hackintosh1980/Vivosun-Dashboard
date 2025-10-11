#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vivosun_dummy_charts.py – Stil-Dummy für das VIVOSUN Dashboard 🌿
"""

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import random

# ---------- Theme ----------
BG = "#081512"
CARD = "#10281f"
TEXT = "#e6ffe6"
ACCENT = "#7eff9f"

COLORS = {
    "t_main":  "#7eff9f",
    "h_main":  "#00ffcc",
    "vpd_int": "#00ffaa",
    "t_ext":   "#66ccff",
    "h_ext":   "#ffaa00",
    "vpd_ext": "#ff6666",
}

TITLES = {
    "t_main": "Internal Temp",
    "h_main": "Humidity",
    "vpd_int": "Internal VPD",
    "t_ext": "External Temp",
    "h_ext": "External Humidity",
    "vpd_ext": "External VPD",
}

# ---------- Fake Data ----------
def generate_data():
    base = datetime.datetime.now()
    times = [base - datetime.timedelta(seconds=60-i) for i in range(60)]
    data = {k: [random.uniform(19, 22) if "t_" in k else random.uniform(40, 70)] * 60 for k in COLORS}
    for k in data:
        data[k] = [v + random.uniform(-0.3, 0.3) for v in data[k]]
    return times, data

# ---------- GUI ----------
root = tk.Tk()
root.title("🌱 VIVOSUN Chart Dummy")
root.configure(bg=BG)
root.geometry("1400x800")

frame = tk.Frame(root, bg=BG)
frame.pack(fill="both", expand=True, padx=12, pady=12)

times, data = generate_data()

figs, axes = [], []
for idx, key in enumerate(COLORS.keys()):
    r, c = divmod(idx, 3)
    card = tk.Frame(frame, bg=CARD, highlightthickness=1, highlightbackground=ACCENT)
    card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
    frame.grid_rowconfigure(r, weight=1)
    frame.grid_columnconfigure(c, weight=1)

    fig, ax = plt.subplots(figsize=(3.8, 1.8))
    fig.patch.set_facecolor(CARD)
    ax.set_facecolor(CARD)
    ax.tick_params(axis="x", colors=TEXT, labelsize=8)
    ax.tick_params(axis="y", colors=TEXT, labelsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
    ax.grid(True, color="#224433", linestyle=":", alpha=0.3)
    for s in ax.spines.values():
        s.set_visible(False)

    # Werte simulieren
    xs = mdates.date2num(times)
    ys = data[key]
    ax.plot(xs, ys, color=COLORS[key], linewidth=1.8)
    ax.fill_between(xs, ys, min(ys), color=COLORS[key], alpha=0.12)

    # Titel & Wert
    ax.set_title(TITLES[key], color=TEXT, fontsize=12, weight="bold", loc="left", pad=20)
    ax.text(0.02, 0.92, f"{ys[-1]:.2f}", transform=ax.transAxes,
            color=COLORS[key], fontsize=26, weight="bold", va="top", ha="left")

    canvas = FigureCanvasTkAgg(fig, master=card)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)
    figs.append(fig)

root.mainloop()
