#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_chart_widget.py – 🌿 Theme-fähiger Live-Chart für alle 6 Sensordaten
Zeigt t_main, t_ext, t_leaf, h_main, h_ext, vpd aus data.json.
"""

import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import utils, config


def create_chart_widget(parent, theme=None, config=config, utils=utils):
    """Erzeugt den Live-Chart für alle 6 Sensorwerte."""
    theme = theme or getattr(config, "THEME", config)

    # Frame erstellen
    frame = theme.make_frame(parent, bg=theme.BG_MAIN, padx=10, pady=10)

    # Figure/Achsen
    fig, ax_temp = plt.subplots(figsize=(10, 5), dpi=100)
    fig.patch.set_facecolor(theme.CARD_BG)
    ax_temp.set_facecolor(theme.CARD_BG)
    ax_hum = ax_temp.twinx()

    # Achsen & Stil
    ax_temp.set_title("🌡️ Live Environmental Data", color=theme.TEXT, fontsize=13, weight="bold")
    ax_temp.set_xlabel("Samples", color=theme.TEXT)
    ax_temp.set_ylabel("Temperature (°C)", color=theme.TEXT)
    ax_hum.set_ylabel("Humidity (%)", color=theme.TEXT)
    for ax in [ax_temp, ax_hum]:
        ax.grid(True, color=theme.BORDER, linestyle=":", alpha=0.4)
        ax.tick_params(colors=theme.TEXT)
        for spine in ax.spines.values():
            spine.set_color(theme.BORDER)

    # Canvas
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    # Statusanzeige
    lbl_status = tk.Label(
        frame,
        text="⏳ Waiting for sensor data ...",
        bg=theme.BG_MAIN,
        fg=theme.TEXT_DIM,
        font=("Consolas", 11)
    )
    lbl_status.pack(pady=6)

    # Datenpuffer
    data = {k: [] for k in ["t_main", "t_ext", "t_leaf", "h_main", "h_ext", "vpd"]}
    _running = [True]

    # RESET
    def reset_chart():
        for k in data:
            data[k].clear()
        ax_temp.clear()
        ax_hum.clear()
        ax_temp.set_facecolor(theme.CARD_BG)
        ax_hum.set_facecolor(theme.CARD_BG)
        ax_temp.grid(True, color=theme.BORDER, linestyle=":", alpha=0.4)
        ax_temp.set_title("🌡️ Live Environmental Data", color=theme.TEXT)
        lbl_status.config(text="🧹 Chart reset – waiting for data ...", fg=theme.BTN_SECONDARY)
        canvas.draw_idle()

    # POLLING
    def poll_chart():
        if not _running[0]:
            return
        try:
            status = utils.safe_read_json(config.STATUS_FILE) or {}
            if not status.get("connected", False):
                lbl_status.config(text="🔴 Disconnected", fg="red")
                frame.after(2000, poll_chart)
                return

            d = utils.safe_read_json(config.DATA_FILE) or {}
            for k in data:
                val = d.get(k)
                if val is not None:
                    data[k].append(val)
                    data[k] = data[k][-200:]

            # Zeichnen
            ax_temp.clear()
            ax_hum.clear()
            ax_temp.set_facecolor(theme.CARD_BG)
            ax_hum.set_facecolor(theme.CARD_BG)
            ax_temp.grid(True, color=theme.BORDER, linestyle=":", alpha=0.4)

            # Temperaturen
            if data["t_main"]:
                ax_temp.plot(data["t_main"], color=theme.BTN_PRIMARY, linewidth=2, label="T Main")
            if data["t_ext"]:
                ax_temp.plot(data["t_ext"], color="#1E90FF", linewidth=2, label="T Ext")
            if data["t_leaf"]:
                ax_temp.plot(data["t_leaf"], color="#FFD700", linewidth=2, label="T Leaf")

            # Feuchtigkeit
            if data["h_main"]:
                ax_hum.plot(data["h_main"], color="#32CD32", linestyle="--", linewidth=2, label="H Main")
            if data["h_ext"]:
                ax_hum.plot(data["h_ext"], color="#FF8C00", linestyle="--", linewidth=2, label="H Ext")

            # VPD
            if data["vpd"]:
                ax_temp.plot(data["vpd"], color="#FF4444", linestyle=":", linewidth=2, label="VPD")

            # Legende
            h_temp, l_temp = ax_temp.get_legend_handles_labels()
            h_hum, l_hum = ax_hum.get_legend_handles_labels()
            leg = ax_temp.legend(
                h_temp + h_hum,
                l_temp + l_hum,
                facecolor=theme.CARD_BG,
                edgecolor=theme.BORDER,
                labelcolor=theme.TEXT,
                fontsize=9
            )
            for t in leg.get_texts():
                t.set_color(theme.TEXT)

            plt.setp(ax_temp.get_xticklabels(), color=theme.TEXT)
            plt.setp(ax_temp.get_yticklabels(), color=theme.TEXT)
            plt.setp(ax_hum.get_yticklabels(), color=theme.TEXT)
            canvas.draw_idle()

            lbl_status.config(
                text=f"[🟢] Connected | "
                     f"T_main: {d.get('t_main', 0):.1f}°C | "
                     f"H_main: {d.get('h_main', 0):.1f}% | "
                     f"VPD: {d.get('vpd', 0):.2f} kPa",
                fg=theme.LIME if hasattr(theme, "LIME") else "#00FF7F"
            )
        except Exception as e:
            lbl_status.config(text=f"⚠️ Poll error: {e}", fg="orange")
        frame.after(2000, poll_chart)

    # STOP
    def stop_chart():
        _running[0] = False
        lbl_status.config(text="⏹ Chart stopped", fg="orange")

    poll_chart()
    return frame, reset_chart, stop_chart
