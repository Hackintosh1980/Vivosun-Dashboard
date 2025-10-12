#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
enlarged_charts.py – stabile VIVOSUN-Version 🌿
Live-Werte direkt im Chart + feine Y-Achsenauflösung für VPD.
"""

import os
import tkinter as tk
from PIL import Image, ImageTk
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

    # ---------- HEADER ----------
    header = tk.Frame(win, bg=config.CARD)
    header.pack(side="top", fill="x", pady=(8, 4))

    left = tk.Frame(header, bg=config.CARD)
    left.pack(side="left", padx=10, pady=5)

    # Logo laden
    here = os.path.dirname(__file__)
    logo_path = os.path.join(os.path.dirname(here), "assets", "Logo.png")
    if os.path.exists(logo_path):
        try:
            logo_img = Image.open(logo_path).resize((80, 80), Image.LANCZOS)
            logo_tk = ImageTk.PhotoImage(logo_img)
            logo_label = tk.Label(left, image=logo_tk, bg=config.CARD)
            logo_label.image = logo_tk
            logo_label.pack(side="left", padx=(0, 10))
        except Exception as e:
            print(f"[WARN] Logo konnte nicht geladen werden: {e}")

    tk.Label(
        header,
        text=f"🌿 {title}",
        bg=config.CARD,
        fg=color,
        font=("Segoe UI", 20, "bold"),
        anchor="w"
    ).pack(side="left", padx=10)

    # ---------- PLOT ----------
    plot_frame = tk.Frame(win, bg=config.BG)
    plot_frame.pack(fill="both", expand=True, padx=8, pady=8)

    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor(config.CARD)
    ax.set_facecolor(config.CARD)
    ax.grid(True, color="#333", linestyle=":", alpha=0.4)
    ax.tick_params(axis="x", colors=config.TEXT)
    ax.tick_params(axis="y", colors=config.TEXT)
    for s in ax.spines.values():
        s.set_visible(False)

    line, = ax.plot([], [], color=color, linewidth=2.2)

    # Großer Wert im Chart selbst (digitaler Stil)
    value_label = ax.text(
        0.02, 0.95, "--",
        transform=ax.transAxes,
        color=color,
        fontsize=46,
        fontweight="bold",
        va="top", ha="left",
    )

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)
    canvas.draw()

    # ---------- FOOTER ----------
    footer = tk.Frame(win, bg=config.CARD)
    footer.pack(side="bottom", fill="x", pady=(2, 6))
    set_status, mark_data_update = create_footer(footer, config)

    # ---------- UPDATE ----------
    def update():
        try:
            xs = [mdates.date2num(t) for t in data_buffers.get("timestamps", [])]
            ys = data_buffers.get(focus_key, [])

            if not xs or not ys:
                set_status(False)
                win.after(1500, update)
                return

            xs, ys = xs[-300:], ys[-300:]

            # Fahrenheit switch
            unit_celsius = getattr(config, "unit_celsius", True)
            if "t_" in focus_key and not unit_celsius:
                ys = [(v * 9 / 5 + 32) if v is not None else None for v in ys]

            ax.clear()
            ax.set_facecolor(config.CARD)
            ax.grid(True, color="#333", linestyle=":", alpha=0.4)
            ax.tick_params(axis="x", colors=config.TEXT)
            ax.tick_params(axis="y", colors=config.TEXT)
            for s in ax.spines.values():
                s.set_visible(False)

            valid = [y for y in ys if y is not None]
            if valid:
                ax.plot(xs, ys, color=color, linewidth=2.2)

                ymin, ymax = min(valid), max(valid)
                if "vpd" in focus_key:
                    pad = 0.1
                elif "t_" in focus_key:
                    pad = 1.0
                elif "h_" in focus_key:
                    pad = 2.0
                else:
                    pad = 0.5
                ax.set_ylim(ymin - pad, ymax + pad)
            else:
                ax.set_ylim(0, 1)

            ax.xaxis.set_major_locator(MaxNLocator(nbins=8))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))

            # Letzter Wert
            latest = ys[-1]
            if latest is not None:
                if "t_" in focus_key:
                    unit = "°C" if unit_celsius else "°F"
                    val = f"{latest:.1f}{unit}"
                elif "h_" in focus_key:
                    val = f"{latest:.1f}%"
                else:
                    val = f"{latest:.2f} kPa"
                value_label = ax.text(
                    0.02, 0.95, val,
                    transform=ax.transAxes,
                    color=color,
                    fontsize=46,
                    fontweight="bold",
                    va="top", ha="left",
                )
            else:
                value_label = ax.text(
                    0.02, 0.95, "--",
                    transform=ax.transAxes,
                    color=color,
                    fontsize=46,
                    fontweight="bold",
                    va="top", ha="left",
                )

            mark_data_update()
            canvas.draw_idle()

        except Exception as e:
            print(f"[ERROR] Enlarged update(): {e}")

        win.after(1500, update)

    update()
    return win


# ---------- TESTMODUS ----------
if __name__ == "__main__":
    import datetime
    import random

    class DummyConfig:
        BG = "#101010"
        CARD = "#202020"
        TEXT = "white"
        LIME = "#7eff9f"
        unit_celsius = True

    config = DummyConfig()

    root = tk.Tk()
    now = datetime.datetime.now()
    buffers = {
        "timestamps": [now - datetime.timedelta(minutes=i) for i in range(300)],
        "vpd_int": [1.1 + random.uniform(-0.08, 0.08) for _ in range(300)],
    }

    open_window(root, buffers, focus_key="vpd_int")
    root.mainloop()
