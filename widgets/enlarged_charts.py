#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enlarged_charts.py – Vollbild-Chart-Fenster mit echtem Footer-Status-Sync
und GUI-Design passend zur Hauptansicht
"""

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patheffects as path_effects
from PIL import Image, ImageTk
import datetime
import os
from widgets.footer_widget import create_footer


def open_window(parent, config, utils,
                key, title, color, ylabel,
                data_buffers, time_buffer, unit_celsius):

    # ---------- Fenster ----------
    win = tk.Toplevel(parent)
    win.title(f"🔍 {title} – Enlarged View")
    win.geometry("1400x900")
    win.configure(bg=config.BG)

    # ---------- HEADER ----------
    header = tk.Frame(win, bg=config.CARD)
    header.pack(side="top", fill="x", padx=10, pady=8)

    left = tk.Frame(header, bg=config.CARD)
    left.pack(side="left", padx=6)

    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    logo_path = os.path.join(assets_dir, "Logo.png")
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path).resize((90, 90), Image.LANCZOS)
            logo_img = ImageTk.PhotoImage(img)
            lbl = tk.Label(left, image=logo_img, bg=config.CARD)
            lbl.image = logo_img
            lbl.pack(side="left", padx=(0, 10))
        except Exception as e:
            print(f"⚠️ Logo konnte nicht geladen werden: {e}")

    tk.Label(
        left,
        text=f"🌱 Enlarged – {title}",
        bg=config.CARD,
        fg=config.TEXT,
        font=("Segoe UI", 18, "bold"),
        anchor="w",
    ).pack(side="left", anchor="center")

    # ---------- MATPLOTLIB ----------
    fig, ax = plt.subplots(figsize=(10, 5), facecolor=config.BG)
    ax.set_facecolor("#121a24")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.tick_params(axis="y", labelcolor=config.TEXT)
    ax.tick_params(axis="x", labelcolor=config.TEXT, rotation=0)
    ax.set_ylabel(ylabel, color=config.TEXT, fontsize=11, weight="bold")

    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))

    # Titel & Wert im Plot
    ax.set_title(title, color=color, fontsize=20, weight="bold", pad=8, loc="left")

    value_label = ax.text(
        0.02, 0.955, "--",
        transform=ax.transAxes,
        color=color,
        fontsize=42,
        weight="bold",
        va="top", ha="left",
        path_effects=[path_effects.withStroke(linewidth=6, foreground="black")],
        zorder=5,
    )

    line, = ax.plot([], [], color=color, linewidth=2.3, alpha=0.95)

    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    # ---------- UNTERER BEREICH ----------
    bottom = tk.Frame(win, bg=config.BG)
    bottom.pack(side="bottom", fill="x")

    ctrl = tk.Frame(bottom, bg=config.CARD)
    ctrl.pack(side="top", fill="x", pady=4)

    paused = tk.BooleanVar(value=False)
    xs = []

    SPANS_DAYS = {
        "1m": 1 / 1440,
        "15m": 15 / 1440,
        "30m": 30 / 1440,
        "1h": 1 / 24,
        "3h": 3 / 24,
        "12h": 12 / 24,
        "24h": 1,
        "1w": 7,
    }
    span_choice = tk.StringVar(value="1h")

    def apply_locator(span_days: float):
        if span_days <= 1 / 24:
            ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        elif span_days <= 1:
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        else:
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))

    tk.Label(ctrl, text="⏱ Window:", bg=config.CARD, fg=config.TEXT).pack(side="left", padx=6)
    opt = tk.OptionMenu(ctrl, span_choice, *SPANS_DAYS.keys())
    opt.config(bg="lime", fg="black", font=("Segoe UI", 10, "bold"), activebackground="lime")
    opt["highlightthickness"] = 0
    opt.pack(side="left", padx=6)

    def toggle_pause():
        paused.set(not paused.get())
        btn_pause.config(text="▶ Resume" if paused.get() else "⏸ Pause")

    def reset_view():
        if xs:
            ax.set_xlim(xs[0], xs[-1])
            ax.relim()
            ax.autoscale_view(scalex=False, scaley=True)
            canvas.draw_idle()

    btn_pause = tk.Button(ctrl, text="⏸ Pause", command=toggle_pause,
                          bg="orange", fg="black", font=("Segoe UI", 10, "bold"))
    btn_pause.pack(side="left", padx=6)

    tk.Button(ctrl, text="🔄 Reset View", command=reset_view,
              bg="lime", fg="black", font=("Segoe UI", 10, "bold")).pack(side="left", padx=6)

    # ---------- FOOTER ----------
    set_status, mark_data_update = create_footer(bottom, config)

    # ---------- UPDATE ----------
    _prev_span = [span_choice.get()]

    def update():
        if paused.get():
            win.after(1000, update)
            return

        nonlocal xs
        xs = [mdates.date2num(t) for t in time_buffer]
        ys = []
        for v in data_buffers[key]:
            if v is None:
                ys.append(float("nan"))
            elif key in ("t_main", "t_ext"):
                ys.append(v if unit_celsius.get() else utils.c_to_f(v))
            else:
                ys.append(v)

        if xs and ys:
            line.set_data(xs, ys)
            span_days = SPANS_DAYS.get(span_choice.get(), 1 / 24)
            right, left = xs[-1], xs[-1] - span_days
            ax.set_xlim(left, right)
            ax.relim()
            ax.autoscale_view(scalex=False, scaley=True)

            if span_choice.get() != _prev_span[0]:
                apply_locator(span_days)
                _prev_span[0] = span_choice.get()

            latest = ys[-1]
            if latest is not None and not (latest != latest):
                if key in ("t_main", "t_ext"):
                    unit = "°C" if unit_celsius.get() else "°F"
                    value_label.set_text(f"{latest:.1f} {unit}")
                elif "h_" in key:
                    value_label.set_text(f"{latest:.1f} %")
                else:
                    value_label.set_text(f"{latest:.2f} kPa")
            else:
                value_label.set_text("--")

        try:
            mark_data_update()
        except Exception:
            pass

        canvas.draw_idle()
        win.after(1000, update)

    apply_locator(SPANS_DAYS[span_choice.get()])
    update()
    return win
