#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enlarged_charts.py – Vollbild-Chart-Fenster (kompatibel zu charts_gui)
VIVOSUN Stable Layout 🌿
"""

import os
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patheffects as path_effects
from PIL import Image, ImageTk
from widgets.footer_widget import create_footer

# ---------- Farb-Mapping: identisch zu charts_gui ----------
COLOR_MAP = {
    "t_main":  ("Internal Temp",  "#7eff9f", "°C"),
    "h_main":  ("Humidity",       "#00ffcc", "%"),
    "vpd_int": ("Internal VPD",   "#00ffaa", "kPa"),
    "t_ext":   ("External Temp",  "#66ccff", "°C"),
    "h_ext":   ("External Hum.",  "#ffaa00", "%"),
    "vpd_ext": ("External VPD",   "#ff6666", "kPa"),
}

def _find_logo_path():
    here = os.path.dirname(__file__)
    cand1 = os.path.join(here, "assets", "Logo.png")
    cand2 = os.path.join(os.path.dirname(here), "assets", "Logo.png")
    return cand1 if os.path.exists(cand1) else cand2

def _bool_unit(unit_celsius):
    try:
        return bool(unit_celsius.get())
    except Exception:
        return bool(unit_celsius)


# -------------------------------------------------------------------
# Öffentliche API – Wrapper, unterstützt beide Aufrufarten
# -------------------------------------------------------------------
def open_window(parent, *args, **kwargs):
    if args and isinstance(args[0], dict):
        data_buffers = args[0]
        focus_key = kwargs.get("focus_key", "t_main")
        import config, utils
        title, color, ylabel = COLOR_MAP.get(focus_key, ("Unknown", "white", ""))
        time_buffer = data_buffers.get("timestamps", [])
        unit_celsius = getattr(config, "unit_celsius", True)
        return _open_enlarged(parent, config, utils, focus_key, title, color, ylabel,
                              data_buffers, time_buffer, unit_celsius)

    if len(args) >= 8:
        config, utils, key, title, color, ylabel, data_buffers, time_buffer = args[:8]
        unit_celsius = args[8] if len(args) >= 9 else getattr(config, "unit_celsius", True)
        return _open_enlarged(parent, config, utils, key, title, color, ylabel,
                              data_buffers, time_buffer, unit_celsius)

    raise TypeError("open_window: Unsupported signature")


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
    header.pack(side="top", fill="x", padx=10, pady=8)

    left = tk.Frame(header, bg=config.CARD)
    left.pack(side="left", padx=6)

    logo_path = _find_logo_path()
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
        left, text=f"🌱 Enlarged – {title}",
        bg=config.CARD, fg=config.TEXT,
        font=("Segoe UI", 18, "bold"), anchor="w"
    ).pack(side="left", anchor="center")

    # ---------- PLOT AREA ----------
    plot_area = tk.Frame(win, bg=config.BG)
    plot_area.pack(fill="both", expand=True, padx=8, pady=(4, 0))

    fig, ax = plt.subplots(figsize=(10, 5), facecolor=config.CARD)
    ax.set_facecolor(config.CARD)
    ax.grid(True, linestyle=":", alpha=0.3, color="#222")
    ax.tick_params(axis="y", labelcolor=config.TEXT)
    ax.tick_params(axis="x", labelcolor=config.TEXT)
    ax.set_ylabel(ylabel, color=config.TEXT, fontsize=11, weight="bold")

    # Anfangs Achse = 15 Minuten
    ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

    ax.set_title(title, color=color, fontsize=22, weight="bold", pad=14, loc="left")

    value_label = ax.text(
        0.02, 0.95, "--", transform=ax.transAxes,
        color=color, fontsize=46, weight="bold",
        va="top", ha="left",
        path_effects=[path_effects.withStroke(linewidth=6, foreground="black")],
        zorder=5,
    )

    line, = ax.plot([], [], color=color, linewidth=2.3, alpha=0.95)

    canvas = FigureCanvasTkAgg(fig, master=plot_area)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    # ---------- UNTERER BEREICH ----------
    bottom = tk.Frame(win, bg=config.CARD)
    bottom.pack(side="bottom", fill="x", pady=(2, 6))

    ctrl = tk.Frame(bottom, bg=config.CARD)
    ctrl.pack(side="top", fill="x", pady=4)

    paused = tk.BooleanVar(value=False)
    xs = []

    # Zeitfenster-Auswahl (in Tagen)
    SPANS_DAYS = {
        "5s": 5 / 86400,
        "15s": 15 / 86400,
        "30s": 30 / 86400,
        "1m": 1 / 1440,
        "5m": 5 / 1440,
        "15m": 15 / 1440,
        "30m": 30 / 1440,
        "1h": 1 / 24,
        "3h": 3 / 24,
        "12h": 12 / 24,
        "24h": 1,
        "1w": 7,
    }
    span_choice = tk.StringVar(value="15m")

    def apply_locator(span_days: float):
        sec = span_days * 86400
        if sec <= 30:
            ax.xaxis.set_major_locator(mdates.SecondLocator(interval=5))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        elif sec <= 3600:
            ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        else:
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

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
            ax.relim(); ax.autoscale_view(scalex=False, scaley=True)
            canvas.draw_idle()

    btn_pause = tk.Button(ctrl, text="⏸ Pause", command=toggle_pause,
                          bg="orange", fg="black", font=("Segoe UI", 10, "bold"))
    btn_pause.pack(side="left", padx=6)

    tk.Button(ctrl, text="🔄 Reset View", command=reset_view,
              bg="lime", fg="black", font=("Segoe UI", 10, "bold")).pack(side="left", padx=6)

    # ---------- FOOTER ----------
    footer_frame = tk.Frame(bottom, bg=config.CARD)
    footer_frame.pack(side="bottom", fill="x")
    set_status, mark_data_update = create_footer(footer_frame, config)

    # ---------- UPDATE ----------
    _prev_span = [span_choice.get()]
    unit_is_celsius = _bool_unit(unit_celsius)

    def update():
        if paused.get():
            win.after(1000, update); return

        nonlocal xs
        xs = [mdates.date2num(t) for t in time_buffer]
        ys = []
        for v in data_buffers.get(key, []):
            if v is None:
                ys.append(float("nan"))
            elif key in ("t_main", "t_ext"):
                ys.append(v if unit_is_celsius else (v * 9 / 5) + 32)
            else:
                ys.append(v)

        if xs and ys:
            line.set_data(xs, ys)
            span_days = SPANS_DAYS.get(span_choice.get(), 15 / 1440)
            apply_locator(span_days)
            right, left = xs[-1], xs[-1] - span_days
            ax.set_xlim(left, right)
            ax.relim(); ax.autoscale_view(scalex=False, scaley=True)
            latest = ys[-1]
            if latest is not None and not (latest != latest):
                if key.startswith("t_"):
                    unit = "°C" if unit_is_celsius else "°F"
                    value_label.set_text(f"{latest:.2f}{unit}")
                elif key.startswith("h_"):
                    value_label.set_text(f"{latest:.2f}%")
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
