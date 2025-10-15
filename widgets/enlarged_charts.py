#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enlarged_charts.py – Vollbild-Chart-Fenster (kompatibel zu charts_gui)
Zeigt den Verlauf eines Sensors (Temp, Hum, VPD) im Live-Update mit
Zoom, Pause/Resume, Reset und echtem Footer-Sync (debounced).
"""

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patheffects as path_effects
from PIL import Image, ImageTk
import datetime
import os
import math

from widgets.footer_widget import create_footer


# -------------------------------------------------------------------
# Kompatibilitäts-Wrapper für charts_gui.py
# -------------------------------------------------------------------
def open_window(parent, data_buffers, focus_key="t_main"):
    """Wrapper, um enlarged_charts aus charts_gui aufzurufen."""
    mapping = {
        "t_main":  ("Internal Temp",  "#ff6633", "°C"),
        "h_main":  ("Humidity",       "#4ac1ff", "%"),
        "vpd_int": ("Internal VPD",   "#00ff99", "kPa"),
        "t_ext":   ("External Temp",  "#ff00aa", "°C"),
        "h_ext":   ("External Hum.",  "#ffaa00", "%"),
        "vpd_ext": ("External VPD",   "#ff4444", "kPa"),
    }
    title, color, ylabel = mapping.get(focus_key, ("Unknown", "white", ""))

    # Lokale Imports (halten Modul unabhängig)
    import config, utils

    time_buffer = data_buffers.get("timestamps", [])
    unit_celsius = tk.BooleanVar(value=True)  # Anzeigeumschaltung möglich

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
        "1m":  1 / 1440,
        "15m": 15 / 1440,
        "30m": 30 / 1440,
        "1h":  1 / 24,
        "3h":  3 / 24,
        "12h": 12 / 24,
        "24h": 1,
        "1w":  7,
    }
    span_choice = tk.StringVar(value="1m")

    # Achsenformatierung abhängig vom Zeitfenster
    def apply_locator(span_days: float):
        if span_days <= 1 / 24:  # <= 1 Stunde
            ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        elif span_days <= 1:     # <= 24 Stunden
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        else:                    # Tage
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
        # Nur sichtbare X-Limits anpassen, Y wird automatisch skaliert
        if xs:
            ax.set_xlim(xs[0], xs[-1])
            ax.relim()
            ax.autoscale_view(scalex=True, scaley=True)
            canvas.draw_idle()

    btn_pause = tk.Button(ctrl, text="⏸ Pause", command=toggle_pause,
                          bg="orange", fg="black", font=("Segoe UI", 10, "bold"))
    btn_pause.pack(side="left", padx=6)

    tk.Button(ctrl, text="🔄 Reset View", command=reset_view,
              bg="lime", fg="black", font=("Segoe UI", 10, "bold")).pack(side="left", padx=6)

    # ---------- FOOTER ----------
    # NEU: aktuelles Footer-Interface (3 Rückgaben)
    set_status, mark_data_update, set_sensor_status = create_footer(bottom, config)

    # ---------- STATUS-POLL (debounced wie Test-Window) ----------
    def poll_status():
        if not hasattr(poll_status, "_fail_counter"):
            poll_status._fail_counter = 0
            poll_status._last_connected = None

        try:
            status = utils.safe_read_json(config.STATUS_FILE) or {}
            connected = bool(status.get("connected", False))
            main_ok  = bool(status.get("sensor_ok_main", False))
            ext_ok   = bool(status.get("sensor_ok_ext", False))

            if connected:
                poll_status._fail_counter = 0
                smooth = True
            else:
                poll_status._fail_counter += 1
                smooth = poll_status._fail_counter >= 3 and False or poll_status._last_connected

            poll_status._last_connected = smooth
            set_status(smooth)
            set_sensor_status(main_ok, ext_ok)
        except Exception:
            # leise bleiben
            pass

        win.after(1500, poll_status)

    poll_status()

    # ---------- UPDATE ----------
    _prev_span = [span_choice.get()]

    def _c_to_f(c): return c * 9.0 / 5.0 + 32.0

    def update():
        if paused.get():
            win.after(1000, update)
            return

        # time_buffer regelmäßig aktualisieren (Referenz aus charts_gui)
        time_buffer[:] = data_buffers.get("timestamps", [])
        xs_num = mdates.date2num(time_buffer)
        xs.clear()
        xs.extend(xs_num)

        # Y-Werte erstellen (NaNs sauber behandeln)
        ys = []
        for v in data_buffers.get(key, []):
            if v is None or (isinstance(v, float) and math.isnan(v)):
                ys.append(float("nan"))
            elif key in ("t_main", "t_ext"):
                # Temp ggf. in °F darstellen
                val = v if unit_celsius.get() else _c_to_f(v)
                ys.append(val)
            else:
                ys.append(v)

        # Plot aktualisieren
        if xs and ys:
            line.set_data(xs, ys)
            span_days = SPANS_DAYS.get(span_choice.get(), 1 / 24)
            right, left = xs[-1], xs[-1] - span_days
            ax.set_xlim(left, right)

            # Y-Skalierung auf sichtbare Daten
            # (ignoriere NaNs)
            y_valid = [y for y in ys if y is not None and not (isinstance(y, float) and math.isnan(y))]
            if y_valid:
                y_min, y_max = min(y_valid), max(y_valid)
                pad = (y_max - y_min) * 0.2 if y_max != y_min else 0.5
                ax.set_ylim(y_min - pad, y_max + pad)

            # Zeitformatierung neu anwenden, wenn Fenster gewechselt
            if span_choice.get() != _prev_span[0]:
                apply_locator(span_days)
                _prev_span[0] = span_choice.get()

            # Wertlabel
            latest = ys[-1]
            if latest is not None and not (isinstance(latest, float) and math.isnan(latest)):
                if key in ("t_main", "t_ext"):
                    unit = "°C" if unit_celsius.get() else "°F"
                    value_label.set_text(f"{latest:.1f} {unit}")
                elif key.startswith("h_"):
                    value_label.set_text(f"{latest:.1f} %")
                else:
                    value_label.set_text(f"{latest:.2f} kPa")
            else:
                value_label.set_text("--")
        else:
            # Keine Daten → Achse stehen lassen, Label leeren
            value_label.set_text("--")

        try:
            mark_data_update()
        except Exception:
            pass

        canvas.draw_idle()
        win.after(1000, update)

    # Initiale Formatierung & Start
    apply_locator(SPANS_DAYS[span_choice.get()])
    update()
    return win
