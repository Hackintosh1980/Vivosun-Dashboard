#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scattered_vpd_chart.py – VPD Comfort Chart Fenster
Zeigt VPD-Zonen (Contour) + interne/externe Sensorpunkte.
Bidirektionaler Offset-Sync mit dem Header (GUI <-> config).
"""

import os
import sys
import tkinter as tk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import ListedColormap
from PIL import Image, ImageTk

# Pfade korrigieren, damit Module im Projekt gefunden werden
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from widgets.footer_widget import create_footer
import config, utils, icon_loader

# --- Header-Sync importieren (bidirektional) ---
try:
    from main_gui.header_gui import set_offsets_from_outside, sync_offsets_to_gui
except Exception:
    def set_offsets_from_outside(*a, **k): pass
    def sync_offsets_to_gui(): pass


def open_window(parent, config=config, utils=utils):
    win = tk.Toplevel(parent)
    icon_loader.link_icon(win, parent)

    win.title("🌱 VPD Comfort Chart")
    win.geometry("1200x900")
    win.configure(bg=config.BG)

    # ---------- HEADER ----------
    header = tk.Frame(win, bg=config.CARD)
    header.pack(side="top", fill="x", padx=10, pady=(10, 6))

    left_frame = tk.Frame(header, bg=config.CARD)
    left_frame.pack(side="left", padx=6)

    # --- Logo laden ---
    assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    logo_path = os.path.join(assets_dir, "Logo.png")
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path).resize((90, 90), Image.LANCZOS)
            logo_img = ImageTk.PhotoImage(img)
            logo_label = tk.Label(left_frame, image=logo_img, bg=config.CARD)
            logo_label.image = logo_img
            logo_label.pack(side="left", padx=(0, 12))
        except Exception as e:
            print(f"⚠️ Logo konnte nicht geladen werden: {e}")
    else:
        print(f"⚠️ Logo nicht gefunden unter: {logo_path}")

    # --- Titel rechts neben Logo ---
    title = tk.Label(
        left_frame,
        text="🌱 VPD Comfort Chart",
        bg=config.CARD,
        fg=config.TEXT,
        font=("Segoe UI", 22, "bold"),
        anchor="w",
        justify="left"
    )
    title.pack(side="left", anchor="center")

    # ---------- HEADER CONTROLS ----------
    controls = tk.Frame(header, bg=config.CARD)
    controls.pack(side="right", pady=2)

    # --- Pfadfix für Config-Datei ---
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    config_path = os.path.join(base_dir, "data", "config.json")
    cfg = utils.safe_read_json(config_path) or {}
    unit_celsius = cfg.get("unit_celsius", True)

    # Leaf Offset (Anzeige in aktueller Einheit)
    tk.Label(
        controls,
        text=f"Leaf Offset ({'°C' if unit_celsius else '°F'}):",
        bg=config.CARD,
        fg=config.TEXT
    ).pack(side="left", padx=6)

    # Startwert (intern °C → Anzeige ggf. °F)
    start_val_leaf = float(config.leaf_offset_c[0])
    if not unit_celsius:
        start_val_leaf *= 9.0 / 5.0  # °C → °F (Offset)

    leaf_offset_var = tk.DoubleVar(value=start_val_leaf)

    def on_leaf_offset_change(*_):
        """Offset-Änderung mit korrekter Einheit (Delta, kein +32!)."""
        try:
            val_display = float(leaf_offset_var.get())
            if unit_celsius:
                val_c = val_display
            else:
                val_c = val_display * 5.0 / 9.0  # °F → °C
            set_offsets_from_outside(leaf=val_c, hum=None, persist=True)
        except Exception:
            set_offsets_from_outside(leaf=0.0, hum=None, persist=True)

    leaf_offset_var.trace_add("write", on_leaf_offset_change)

    tk.Spinbox(
        controls,
        textvariable=leaf_offset_var,
        from_=-10.0,
        to=10.0,
        increment=0.1,
        width=6,
        bg=config.CARD,
        fg=config.TEXT,
        justify="center"
    ).pack(side="left")

    # Humidity Offset
    tk.Label(
        controls, text="Humidity Offset (%):",
        bg=config.CARD, fg=config.TEXT
    ).pack(side="left", padx=6)

    hum_offset_var = tk.DoubleVar(value=float(config.humidity_offset[0]))

    def on_hum_offset_change(*_):
        try:
            set_offsets_from_outside(leaf=None, hum=float(hum_offset_var.get()), persist=True)
        except Exception:
            set_offsets_from_outside(leaf=None, hum=0.0, persist=True)

    hum_offset_var.trace_add("write", on_hum_offset_change)
    tk.Spinbox(
        controls,
        textvariable=hum_offset_var,
        from_=-50.0,
        to=50.0,
        increment=1.0,
        width=6,
        bg=config.CARD,
        fg=config.TEXT,
        justify="center"
    ).pack(side="left")

    # Reset Offsets
    def reset_offsets():
        leaf_offset_var.set(0.0)
        hum_offset_var.set(0.0)

    tk.Button(
        controls,
        text="↺ Reset Offsets",
        command=reset_offsets,
        bg="orange",
        fg="black",
        font=("Segoe UI", 10, "bold")
    ).pack(side="left", padx=8)

    # Nach Aufbau: aktuelle Werte synchronisieren
    try:
        sync_offsets_to_gui()
    except Exception:
        pass

    # ---------- MATPLOTLIB ----------
    fig, ax = plt.subplots(figsize=(9, 7), facecolor=config.BG)
    ax.set_facecolor(config.BG)
    ax.set_title("VPD Comfort Zones (All Grow Stages)",
                 color=config.TEXT, fontsize=13, pad=12)

    ax.set_xlabel(f"Temperature ({'°C' if unit_celsius else '°F'})", color=config.TEXT)
    ax.set_ylabel("Relative Humidity (%)", color=config.TEXT)
    ax.tick_params(colors=config.TEXT)

    temps = np.linspace(10, 40, 300)
    hums = np.linspace(0, 100, 300)
    T, H = np.meshgrid(temps, hums)

    def calc_vpd(temp_c, rh):
        svp = 0.6108 * np.exp((17.27 * temp_c) / (temp_c + 237.3))
        return svp * (1.0 - (rh / 100.0))

    VPD = calc_vpd(T, H)

    cmap = ListedColormap([
        "#00441b", "#1b7837", "#5aae61", "#a6dba0",
        "#fddbc7", "#f4a582", "#d6604d", "#b2182b"
    ])

    cs = ax.contourf(T, H, VPD, levels=np.linspace(0, 4, 100), cmap=cmap, alpha=0.9)
    cbar = fig.colorbar(cs, ax=ax)
    cbar.set_label("VPD (kPa)", color=config.TEXT)
    cbar.ax.yaxis.set_tick_params(color=config.TEXT)
    plt.setp(plt.getp(cbar.ax.axes, "yticklabels"), color=config.TEXT)

    internal_dot = ax.scatter([], [], color="lime", edgecolor="black", s=120, label="Internal Sensor")
    external_dot = ax.scatter([], [], color="red", edgecolor="black", s=120, label="External Sensor")

    legend = ax.legend(facecolor=config.CARD, edgecolor="gray", fontsize=10)
    for text in legend.get_texts():
        text.set_color(config.TEXT)

    info_box = ax.text(
        0.99, 0.01, "",
        transform=ax.transAxes,
        fontsize=10,
        color=config.TEXT,
        ha="right", va="bottom",
        bbox=dict(facecolor=config.CARD, edgecolor="gray", boxstyle="round,pad=0.4")
    )

    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=6)

    # ---------- FOOTER ----------
    try:
        set_status, mark_data_update = create_footer(win, config)
    except Exception as e:
        print(f"⚠️ Footer konnte nicht geladen werden: {e}")
        set_status = mark_data_update = lambda *a, **k: None

# ---------- UPDATE LOOP ----------
    def update():
        # --- Sanftes Status-Glätten (3 Polls Toleranz) ---
        if not hasattr(update, "_disconnect_counter"):
            update._disconnect_counter = 0
            update._last_connected = True
            update._hotstart_counter = 0
            update._was_connected = True

        status = utils.safe_read_json(config.STATUS_FILE) or {}
        connected = status.get("connected", False)
        sensor_ok_main = status.get("sensor_ok_main", False)
        sensor_ok_ext = status.get("sensor_ok_ext", False)

        # --- Glättung (verhindert Flackern) ---
        if connected:
            update._disconnect_counter = 0
            update._last_connected = True
        else:
            update._disconnect_counter += 1
            if update._disconnect_counter >= 3:
                update._last_connected = False

        connected = update._last_connected

        # --- Hotstart: nach Reconnect 2 Polls abwarten, bevor Sensorwerte ausgewertet werden ---
        if connected and not update._was_connected:
            print("🔄 Reconnect erkannt – warte auf stabile Sensordaten …")
            update._hotstart_counter = 2

        update._was_connected = connected

        if update._hotstart_counter > 0:
            update._hotstart_counter -= 1
            internal_dot.set_offsets(np.empty((0, 2)))
            external_dot.set_offsets(np.empty((0, 2)))
            info_box.set_text("[🟢] Connected (initializing...)\n🌡️ Internal: —   🌡️ External: —")
            canvas.draw_idle()
            win.after(3000, update)
            return

        # --- Daten prüfen ---
        d = utils.safe_read_json(config.DATA_FILE) or {}
        leaf_off = float(config.leaf_offset_c[0])
        hum_off = float(config.humidity_offset[0])

        ti, hi = d.get("t_main"), d.get("h_main")
        te, he = d.get("t_ext"), d.get("h_ext")
        vpd_int = vpd_ext = None

        # --- Verbindung prüfen ---
        if not connected:
            # Alte Daten löschen, falls noch vorhanden
            if any(d.get(k) for k in ("t_main", "h_main", "t_ext", "h_ext")):
                utils.safe_write_json(config.DATA_FILE, {
                    "timestamp": None,
                    "t_main": None,
                    "h_main": None,
                    "t_ext": None,
                    "h_ext": None,
                })
                print("🧹 Alte Werte beim Disconnect entfernt (Widget-Sync).")

            internal_dot.set_offsets(np.empty((0, 2)))
            external_dot.set_offsets(np.empty((0, 2)))
            info_box.set_text("[🔴] Disconnected\n🌡️ Internal: ⚠️   🌡️ External: ⚠️")
            canvas.draw_idle()
            win.after(3000, update)
            return

        # --- Interner Sensor ---
        if sensor_ok_main and ti is not None and hi is not None:
            ti_eff, hi_eff = ti + leaf_off, hi + hum_off
            internal_dot.set_offsets([[ti_eff, hi_eff]])
            vpd_int = utils.calc_vpd(ti_eff, hi_eff)
        else:
            internal_dot.set_offsets(np.empty((0, 2)))

        # --- Externer Sensor ---
        if sensor_ok_ext and te is not None and he is not None:
            te_eff, he_eff = te + leaf_off, he + hum_off
            external_dot.set_offsets([[te_eff, he_eff]])
            vpd_ext = utils.calc_vpd(te_eff, he_eff)
        else:
            external_dot.set_offsets(np.empty((0, 2)))

        # --- Anzeige aufbauen ---
        unit = "°C" if unit_celsius else "°F"

        def disp_temp(val_c):
            return None if val_c is None else (val_c if unit_celsius else utils.c_to_f(val_c))

        lines = []
        lines.append("[🟢] Connected")

        if vpd_int is not None:
            lines.append(f"🌡️ Internal: ✅ {disp_temp(ti):.1f}{unit} | {hi:.1f}% | VPD={vpd_int:.2f} kPa")
        else:
            lines.append("🌡️ Internal: ⚠️ — no data —")

        if vpd_ext is not None:
            lines.append(f"🌡️ External: ✅ {disp_temp(te):.1f}{unit} | {he:.1f}% | VPD={vpd_ext:.2f} kPa")
        else:
            lines.append("🌡️ External: ⚠️ — sensor off —")

        info_box.set_text("\n".join(lines))
        canvas.draw_idle()

        try:
            mark_data_update()
        except Exception:
            pass

        win.after(3000, update)

    update()
    return win
