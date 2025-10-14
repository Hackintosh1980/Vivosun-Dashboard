#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scattered_chart_widget.py – VPD-Comfort Scatter-Chart als wiederverwendbares Widget
- VPD-Contour-Zonen (wie altes Fenster)
- Live-Punkte (internal/external)
- Offset-Spins (Leaf/Humidity) mit Header-Sync (GUI <-> config)
- Einheitssupport (°C/°F), sanftes BT-Debounce
- API: create_scattered_chart(parent) -> (frame, reset_chart, stop_chart)
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

# --- Header-Sync importieren (bidirektional, mit Fallbacks) ---
try:
    from main_gui.header_gui import set_offsets_from_outside, sync_offsets_to_gui
except Exception:
    def set_offsets_from_outside(*a, **k):  # Fallbacks, wenn Header nicht geladen ist
        pass
    def sync_offsets_to_gui():
        pass


def _read_unit_flag():
    """unit_celsius aus data/config.json lesen, sonst True."""
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        cfg_path = os.path.join(base_dir, "data", "config.json")
        cfg = utils.safe_read_json(cfg_path) or {}
        return bool(cfg.get("unit_celsius", True))
    except Exception:
        return True


def _c_to_f(c): return c * 9.0 / 5.0 + 32.0
def _f_to_c(f): return (f - 32.0) * 5.0 / 9.0


def create_scattered_chart(parent, config=config):
    """Erstellt das Scatter-VPD-Diagramm (Frame) und gibt Reset/Stop zurück."""
    frame = tk.Frame(parent, bg=config.BG)

    # --------- Einheiten + Offsets ----------
    unit_celsius = _read_unit_flag()
    leaf_off_c = float(getattr(config, "leaf_offset_c", [0.0])[0])  # intern immer °C
    hum_off = float(getattr(config, "humidity_offset", [0.0])[0])

    # ---------- CONTROL-LEISTE (Spins) ----------
    controls = tk.Frame(frame, bg=config.CARD)
    controls.pack(side="top", fill="x", padx=8, pady=(8, 4))

    # Leaf Offset (Anzeige in akt. Einheit, intern °C-Delta)
    tk.Label(
        controls,
        text=f"Leaf Offset ({'°C' if unit_celsius else '°F'}):",
        bg=config.CARD, fg=config.TEXT
    ).pack(side="left", padx=(8, 6))

    start_leaf_display = leaf_off_c if unit_celsius else (leaf_off_c * 9.0 / 5.0)
    leaf_offset_var = tk.DoubleVar(value=start_leaf_display)

    def on_leaf_offset_change(*_):
        nonlocal leaf_off_c
        try:
            val_display = float(leaf_offset_var.get())
            leaf_off_c = val_display if unit_celsius else _f_to_c(val_display)  # zurück in °C
            set_offsets_from_outside(leaf=leaf_off_c, hum=None, persist=True)
        except Exception:
            pass

    leaf_offset_var.trace_add("write", on_leaf_offset_change)

    tk.Spinbox(
        controls, textvariable=leaf_offset_var,
        from_=-10.0 if unit_celsius else -18.0,
        to=10.0 if unit_celsius else 18.0,
        increment=0.1 if unit_celsius else 0.2,
        width=6, bg=config.CARD, fg=config.TEXT, justify="center"
    ).pack(side="left")

    # Humidity Offset
    tk.Label(
        controls, text="Humidity Offset (%):", bg=config.CARD, fg=config.TEXT
    ).pack(side="left", padx=(12, 6))

    hum_offset_var = tk.DoubleVar(value=hum_off)

    def on_hum_offset_change(*_):
        nonlocal hum_off
        try:
            hum_off = float(hum_offset_var.get())
            set_offsets_from_outside(leaf=None, hum=hum_off, persist=True)
        except Exception:
            pass

    hum_offset_var.trace_add("write", on_hum_offset_change)

    tk.Spinbox(
        controls, textvariable=hum_offset_var,
        from_=-50.0, to=50.0, increment=1.0,
        width=6, bg=config.CARD, fg=config.TEXT, justify="center"
    ).pack(side="left")

    def reset_offsets():
        leaf_offset_var.set(0.0)
        hum_offset_var.set(0.0)

    tk.Button(
        controls, text="↺ Reset Offsets", command=reset_offsets,
        bg="orange", fg="black", font=("Segoe UI", 10, "bold")
    ).pack(side="left", padx=10)

    # Nach Aufbau: aktuelle Werte synchronisieren (falls Header aktiv)
    try:
        sync_offsets_to_gui()
    except Exception:
        pass

    # --------- Figure / Axes ----------
    fig, ax = plt.subplots(figsize=(9, 7), facecolor=config.BG)
    ax.set_facecolor(config.BG)
    ax.set_title("VPD Comfort Zones (All Grow Stages)",
                 color=config.TEXT, fontsize=13, pad=12)

    unit_label = "°C" if unit_celsius else "°F"
    ax.set_xlabel(f"Temperature ({unit_label})", color=config.TEXT)
    ax.set_ylabel("Relative Humidity (%)", color=config.TEXT)
    ax.tick_params(colors=config.TEXT)

    # --------- VPD-Contour ----------
    temps_c = np.linspace(10, 40, 300)               # Rechenbasis °C
    temps_disp = temps_c if unit_celsius else _c_to_f(temps_c)
    hums = np.linspace(0, 100, 300)
    T_c, H = np.meshgrid(temps_c, hums)

    def calc_vpd(temp_c, rh):
        svp = 0.6108 * np.exp((17.27 * temp_c) / (temp_c + 237.3))
        return svp * (1.0 - (rh / 100.0))

    VPD = calc_vpd(T_c, H)
    cmap = ListedColormap([
        "#00441b", "#1b7837", "#5aae61", "#a6dba0",
        "#fddbc7", "#f4a582", "#d6604d", "#b2182b"
    ])

    T_disp, H_disp = np.meshgrid(temps_disp, hums)
    cs = ax.contourf(T_disp, H_disp, VPD, levels=np.linspace(0, 4, 100), cmap=cmap, alpha=0.9)
    cbar = fig.colorbar(cs, ax=ax)
    cbar.set_label("VPD (kPa)", color=config.TEXT)
    cbar.ax.yaxis.set_tick_params(color=config.TEXT)
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color=config.TEXT)

    internal_dot = ax.scatter([], [], color="lime", edgecolor="black", s=120, label="Internal Sensor")
    external_dot = ax.scatter([], [], color="red", edgecolor="black", s=120, label="External Sensor")

    leg = ax.legend(facecolor=config.CARD, edgecolor="gray", fontsize=10)
    for t in leg.get_texts():
        t.set_color(config.TEXT)

    info_box = ax.text(
        0.99, 0.01, "",
        transform=ax.transAxes,
        fontsize=10,
        color=config.TEXT,
        ha="right", va="bottom",
        bbox=dict(facecolor=config.CARD, edgecolor="gray", boxstyle="round,pad=0.4")
    )

    ax.set_xlim(temps_disp.min(), temps_disp.max())
    ax.set_ylim(0, 100)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=6)

    # --------- Status-Glättung ----------
    def _smooth_connected(curr_connected):
        if not hasattr(_smooth_connected, "_dc"):
            _smooth_connected._dc = 0
            _smooth_connected._last = True
        if curr_connected:
            _smooth_connected._dc = 0
            _smooth_connected._last = True
        else:
            _smooth_connected._dc += 1
            if _smooth_connected._dc >= 3:
                _smooth_connected._last = False
        return _smooth_connected._last

    # --------- Live-Update ----------
    def update_chart():
        try:
            # Status lesen
            status = utils.safe_read_json(config.STATUS_FILE) or {}
            connected_raw = bool(status.get("connected", False))
            sensor_ok_main = bool(status.get("sensor_ok_main", False))
            sensor_ok_ext = bool(status.get("sensor_ok_ext", False))
            connected = _smooth_connected(connected_raw)

            # Offsets aus config aktualisieren (Header-Sync)
            nonlocal leaf_off_c, hum_off
            try:
                leaf_off_c = float(getattr(config, "leaf_offset_c", [leaf_off_c])[0])
                hum_off = float(getattr(config, "humidity_offset", [hum_off])[0])
            except Exception:
                pass

            # Daten holen
            d = utils.safe_read_json(config.DATA_FILE) or {}
            ti, hi = d.get("t_main"), d.get("h_main")
            te, he = d.get("t_ext"), d.get("h_ext")

            if not connected:
                internal_dot.set_offsets(np.empty((0, 2)))
                external_dot.set_offsets(np.empty((0, 2)))
                info_box.set_text("[🔴] Disconnected\n🌡️ Internal: ⚠️   🌡️ External: ⚠️")
                fig.canvas.draw_idle()
                frame._job = frame.after(3000, update_chart)
                return

            def disp_temp(c_val):
                if c_val is None:
                    return None
                return c_val if unit_celsius else _c_to_f(c_val)

            vpd_int = vpd_ext = None

            # Internal
            if sensor_ok_main and ti is not None and hi is not None:
                ti_eff_c = ti + leaf_off_c
                hi_eff = hi + hum_off
                internal_dot.set_offsets(np.array([[disp_temp(ti_eff_c), hi_eff]]))
                vpd_int = float(utils.calc_vpd(ti_eff_c, hi_eff))
            else:
                internal_dot.set_offsets(np.empty((0, 2)))

            # External
            if sensor_ok_ext and te is not None and he is not None:
                te_eff_c = te + leaf_off_c
                he_eff = he + hum_off
                external_dot.set_offsets(np.array([[disp_temp(te_eff_c), he_eff]]))
                vpd_ext = float(utils.calc_vpd(te_eff_c, he_eff))
            else:
                external_dot.set_offsets(np.empty((0, 2)))

            # Info
            unit = "°C" if unit_celsius else "°F"
            lines = ["[🟢] Connected"]
            if vpd_int is not None:
                lines.append(f"🌡️ Internal: ✅ {disp_temp(ti):.1f}{unit} | {hi:.1f}% | VPD={vpd_int:.2f} kPa")
            else:
                lines.append("🌡️ Internal: ⚠️ — no data —")
            if vpd_ext is not None:
                lines.append(f"🌡️ External: ✅ {disp_temp(te):.1f}{unit} | {he:.1f}% | VPD={vpd_ext:.2f} kPa")
            else:
                lines.append("🌡️ External: ⚠️ — sensor off —")

            info_box.set_text("\n".join(lines))
            fig.canvas.draw_idle()

        except Exception as e:
            print(f"⚠️ Scatter-Chart Update Error: {e}")

        frame._job = frame.after(3000, update_chart)

    # --------- Reset & Stop ----------
    def reset_chart():
        internal_dot.set_offsets(np.empty((0, 2)))
        external_dot.set_offsets(np.empty((0, 2)))
        info_box.set_text("[🟢] Connected\n— reset —")
        fig.canvas.draw_idle()

    def stop_chart():
        if hasattr(frame, "_job"):
            try:
                frame.after_cancel(frame._job)
            except Exception:
                pass

    # Start
    update_chart()
    return frame, reset_chart, stop_chart
