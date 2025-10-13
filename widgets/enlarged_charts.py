#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enlarged_charts.py – Vollbild-Chart-Fenster (kompatibel zu charts_gui)
Zeigt den Verlauf eines Sensors (Temp, Hum, VPD) im Live-Update mit
Zoom, Pause/Resume, Reset und echtem Footer-Sync.
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


# -------------------------------------------------------------------
# Kompatibilitäts-Wrapper für charts_gui.py
# -------------------------------------------------------------------
def open_window(parent, data_buffers, focus_key="t_main"):
    """Wrapper, um enlarged_charts aus charts_gui aufzurufen."""
    mapping = {
        "t_main": ("Internal Temp",  "#ff6633", "°C"),
        "h_main": ("Humidity",       "#4ac1ff", "%"),
        "vpd_int": ("Internal VPD",  "#00ff99", "kPa"),
        "t_ext": ("External Temp",   "#ff00aa", "°C"),
        "h_ext": ("External Hum.",   "#ffaa00", "%"),
        "vpd_ext": ("External VPD",  "#ff4444", "kPa"),
    }

    title, color, ylabel = mapping.get(focus_key, ("Unknown", "white", ""))
    import config, utils

    time_buffer = data_buffers.get("timestamps", [])
    unit_celsius = tk.BooleanVar(value=True)

    return _open_enlarged(parent, config, utils,
                          key=focus_key, title=title, color=color,
                          ylabel=ylabel, data_buffers=data_buffers,
                          time_buffer=time_buffer, unit_celsius=unit_celsius)


# -------------------------------------------------------------------
# Hauptfenster
# -------------------------------------------------------------------
def _open_enlarged(parent, config, utils,
                   key, title, color, ylabel,
                   data_buffers, time_buffer, unit_celsius):

    win = tk.Toplevel(parent)
    win.title(f"🔍 {title} – Enlarged View")
    win.geometry("1400x900")
    win.configure(bg=config.BG)

    # ---------- HEADER ----------
    header = tk.Frame(win, bg=config.CARD)
    header.pack(side="top", fill="x", padx=10, pady=(10, 6))

    left = tk.Frame(header, bg=config.CARD)
    left.pack(side="left", padx=6)

    # Logo laden aus ../assets
    assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
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
    else:
        print(f"⚠️ Logo nicht gefunden unter: {logo_path}")

    tk.Label(
        left,
        text=f"🌱 Enlarged – {title}",
        bg=config.CARD,
        fg=config.TEXT,
        font=("Segoe UI", 20, "bold"),
        anchor="w",
    ).pack(side="left", anchor="center")

    # ---------- MATPLOTLIB ----------
    fig, ax = plt.subplots(figsize=(10, 5), facecolor=config.BG)
    ax.set_facecolor("#121a24")
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.tick_params(axis="y", labelcolor=config.TEXT)
    ax.tick_params(axis="x", labelcolor=config.TEXT)
    ax.set_ylabel(ylabel, color=config.TEXT, fontsize=11, weight="bold")

    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
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

    # Zeitfenster-Auswahl
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

    # Achsenformatierung abhängig vom Zeitfenster
    def apply_locator(span_days: float):
        if span_days <= 1 / 24:
            ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        elif span_days <= 1:
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        else:
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        canvas.draw_idle()

    # Steuerungsleiste
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

        # time_buffer regelmäßig aktualisieren
        time_buffer[:] = data_buffers.get("timestamps", [])
        xs.clear()
        xs.extend(mdates.date2num(time_buffer))

        ys = []
        for v in data_buffers.get(key, []):
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

            # Wenn Zeitfenster geändert → Locator neu anwenden
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
