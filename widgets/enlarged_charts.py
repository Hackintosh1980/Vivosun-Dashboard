#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enlarged_charts.py – Minimal, stabil, funktioniert immer
Zeigt Daten aus charts_gui (data_buffers, focus_key)
mit Footer-LED und Live-Werten.
"""

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
from widgets.footer_widget import create_footer


COLOR_MAP = {
    "t_main":  ("Internal Temp",  "#7eff9f", "°C"),
    "h_main":  ("Humidity",       "#00ffcc", "%"),
    "vpd_int": ("Internal VPD",   "#00ffaa", "kPa"),
    "t_ext":   ("External Temp",  "#66ccff", "°C"),
    "h_ext":   ("External Hum.",  "#ffaa00", "%"),
    "vpd_ext": ("External VPD",   "#ff6666", "kPa"),
}


def open_window(parent, data_buffers, focus_key="t_main"):
    import config

    title, color, ylabel = COLOR_MAP.get(focus_key, ("Unknown", "#ffffff", ""))

    win = tk.Toplevel(parent)
    win.title(f"{title} – Enlarged View")
    win.geometry("1200x800")
    win.configure(bg=config.BG)

    # ---------- Titel ----------
    tk.Label(
        win,
        text=f"🌱 {title}",
        bg=config.BG,
        fg=color,
        font=("Segoe UI", 20, "bold")
    ).pack(pady=(10, 0))

    # ---------- Plot ----------
    plot_frame = tk.Frame(win, bg=config.BG)
    plot_frame.pack(fill="both", expand=True, padx=8, pady=8)

    fig, ax = plt.subplots(figsize=(9, 4))
    fig.patch.set_facecolor(config.CARD)
    ax.set_facecolor(config.CARD)
    ax.grid(True, color="#333", linestyle=":", alpha=0.4)
    ax.tick_params(axis="x", colors=config.TEXT)
    ax.tick_params(axis="y", colors=config.TEXT)
    for s in ax.spines.values():
        s.set_visible(False)

    line, = ax.plot([], [], color=color, linewidth=2)
    value_label = ax.text(
        0.02, 0.95, "--",
        transform=ax.transAxes,
        color=color,
        fontsize=38,
        weight="bold",
        va="top", ha="left"
    )

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    # ---------- Footer ----------
    footer = tk.Frame(win, bg=config.CARD)
    footer.pack(side="bottom", fill="x")
    set_status, mark_data_update = create_footer(footer, config)

    # ---------- Update ----------
    def update():
        try:
            xs = [mdates.date2num(t) for t in data_buffers.get("timestamps", [])]
            ys = data_buffers.get(focus_key, [])

            if not xs or not ys:
                set_status("⚪ Waiting for data", "gray")
                win.after(1000, update)
                return

            xs = xs[-300:]
            ys = ys[-300:]

            line.set_data(xs, ys)
            ax.relim()
            ax.autoscale_view()
            ax.xaxis.set_major_locator(MaxNLocator(nbins=8))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

            latest = ys[-1]
            if latest is not None:
                if "t_" in focus_key:
                    val = f"{latest:.1f}°C"
                elif "h_" in focus_key:
                    val = f"{latest:.1f}%"
                else:
                    val = f"{latest:.2f} kPa"
                value_label.set_text(val)
                set_status("🟢 Live", "#7eff9f")
            else:
                value_label.set_text("--")
                set_status("🟡 No value", "orange")

            mark_data_update()
            canvas.draw_idle()

        except Exception as e:
            set_status(f"🔴 Error: {e}", "red")

        win.after(1500, update)

    update()
    return win
