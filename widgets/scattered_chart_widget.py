#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scattered_chart_widget.py – VPD Comfort Chart Widget (modern VIVOSUN Edition)
- nutzt zentrale utils.calc_vpd()
- sauberes Contour-Design (Theme-basiert)
- Live-Punkte mit sanfter Animation
- Header-Sync & Offsets
- Info-Panel unten rechts
"""

import os
import tkinter as tk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import ListedColormap

import utils, config


# --- Optionaler Header-Sync ---
try:
    from main_gui.header_gui import set_offsets_from_outside, sync_offsets_to_gui
except Exception:
    def set_offsets_from_outside(*a, **k): pass
    def sync_offsets_to_gui(): pass


def _read_unit_flag():
    """Liest unit_celsius aus config.json."""
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cfg = utils.safe_read_json(os.path.join(base_dir, "data", "config.json")) or {}
        return bool(cfg.get("unit_celsius", True))
    except Exception:
        return True


def _c_to_f(c): return c * 9.0 / 5.0 + 32.0


def create_scattered_chart(parent, config=config):
    """Erstellt das Scatter-VPD-Diagramm und gibt (frame, reset, stop) zurück."""
    frame = tk.Frame(parent, bg=config.BG)

    # --- Einheiten + Offsets ---
    unit_celsius = _read_unit_flag()
    leaf_off_c = float(getattr(config, "leaf_offset_c", [0.0])[0])
    hum_off = float(getattr(config, "humidity_offset", [0.0])[0])

    # --- Figure Setup ---
    fig, ax = plt.subplots(figsize=(9, 7), facecolor=config.BG)
    ax.set_facecolor(config.BG)
    ax.tick_params(colors=config.TEXT)
    unit_label = "°C" if unit_celsius else "°F"

    ax.set_title("VPD Comfort Zones", color=config.TEXT, fontsize=14, weight="bold", pad=10)
    ax.set_xlabel(f"Temperature ({unit_label})", color=config.TEXT)
    ax.set_ylabel("Relative Humidity (%)", color=config.TEXT)

    # --- Contour vorbereiten ---
    temps_c = np.linspace(10, 40, 300)
    temps_disp = temps_c if unit_celsius else _c_to_f(temps_c)
    hums = np.linspace(0, 100, 300)
    T_c, H = np.meshgrid(temps_c, hums)

    # zentrale VPD-Berechnung
    VPD = np.vectorize(utils.calc_vpd)(T_c, H)

    cmap = ListedColormap([
        "#005522", "#1b7837", "#5aae61", "#a6dba0",
        "#fddbc7", "#f4a582", "#d6604d", "#b2182b"
    ])

    T_disp, H_disp = np.meshgrid(temps_disp, hums)
    contour = ax.contourf(T_disp, H_disp, VPD, levels=np.linspace(0, 4, 60), cmap=cmap, alpha=0.9)

    cbar = fig.colorbar(contour, ax=ax)
    cbar.set_label("VPD (kPa)", color=config.TEXT)
    plt.setp(plt.getp(cbar.ax, "yticklabels"), color=config.TEXT)

    # --- Punkte ---
    internal_dot = ax.scatter([], [], s=140, color="#00FF7F", edgecolor="black", label="Internal")
    external_dot = ax.scatter([], [], s=140, color="#FF4444", edgecolor="black", label="External")

    legend = ax.legend(
        loc="upper right",
        facecolor=config.CARD,
        edgecolor="#444",
        fontsize=10,
        labelcolor=config.TEXT
    )
    for t in legend.get_texts():
        t.set_color(config.TEXT)

    # --- Info-Box ---
    info_box = ax.text(
        0.99, 0.01, "",
        transform=ax.transAxes,
        fontsize=10,
        color=config.TEXT,
        ha="right", va="bottom",
        bbox=dict(facecolor=config.CARD, edgecolor="#555", boxstyle="round,pad=0.4")
    )

    # --- Canvas ---
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=6)

    # --- Sanftes Status-Glätten ---
    def _smooth_connected(curr):
        if not hasattr(_smooth_connected, "_counter"):
            _smooth_connected._counter, _smooth_connected._state = 0, True
        if curr:
            _smooth_connected._counter, _smooth_connected._state = 0, True
        else:
            _smooth_connected._counter += 1
            if _smooth_connected._counter >= 3:
                _smooth_connected._state = False
        return _smooth_connected._state

    # --- Update ---
    def update_chart():
        try:
            status = utils.safe_read_json(config.STATUS_FILE) or {}
            connected_raw = bool(status.get("connected", False))
            sensor_ok_main = bool(status.get("sensor_ok_main", False))
            sensor_ok_ext = bool(status.get("sensor_ok_ext", False))
            connected = _smooth_connected(connected_raw)

            d = utils.safe_read_json(config.DATA_FILE) or {}
            ti, hi = d.get("t_main"), d.get("h_main")
            te, he = d.get("t_ext"), d.get("h_ext")

            if not connected:
                internal_dot.set_offsets(np.empty((0, 2)))
                external_dot.set_offsets(np.empty((0, 2)))
                info_box.set_text("[🔴] Disconnected\n🌡️ Internal: —   🌡️ External: —")
                fig.canvas.draw_idle()
                frame.after(3000, update_chart)
                return

            # interne/externe Punkte + VPD
            vpd_int = vpd_ext = None

            if sensor_ok_main and ti is not None and hi is not None:
                ti_eff, hi_eff = ti + leaf_off_c, hi + hum_off
                internal_dot.set_offsets([[ti_eff if unit_celsius else _c_to_f(ti_eff), hi_eff]])
                vpd_int = utils.calc_vpd(ti_eff, hi_eff)
            else:
                internal_dot.set_offsets(np.empty((0, 2)))

            if sensor_ok_ext and te is not None and he is not None:
                te_eff, he_eff = te + leaf_off_c, he + hum_off
                external_dot.set_offsets([[te_eff if unit_celsius else _c_to_f(te_eff), he_eff]])
                vpd_ext = utils.calc_vpd(te_eff, he_eff)
            else:
                external_dot.set_offsets(np.empty((0, 2)))

            # --- Info ---
            unit = "°C" if unit_celsius else "°F"
            lines = ["[🟢] Connected"]
            if vpd_int is not None:
                lines.append(f"🌡️ Internal: ✅ {ti:.1f}{unit} | {hi:.1f}% | {vpd_int:.2f} kPa")
            else:
                lines.append("🌡️ Internal: ⚠️ no data")
            if vpd_ext is not None:
                lines.append(f"🌡️ External: ✅ {te:.1f}{unit} | {he:.1f}% | {vpd_ext:.2f} kPa")
            else:
                lines.append("🌡️ External: ⚠️ no sensor")

            info_box.set_text("\n".join(lines))
            fig.canvas.draw_idle()

        except Exception as e:
            print(f"⚠️ ScatterChart Error: {e}")

        frame.after(3000, update_chart)

    # --- Reset & Stop ---
    def reset_chart():
        internal_dot.set_offsets(np.empty((0, 2)))
        external_dot.set_offsets(np.empty((0, 2)))
        info_box.set_text("[🟢] Connected\n— reset —")
        fig.canvas.draw_idle()

    def stop_chart():
        try:
            frame.after_cancel(update_chart)
        except Exception:
            pass

    update_chart()
    return frame, reset_chart, stop_chart
