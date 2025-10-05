#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scattered_vpd_chart.py – VPD Comfort Chart Fenster
Zeigt VPD-Zonen (Contour) + interne/externe Sensorpunkte.
"""

import tkinter as tk
import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.colors import ListedColormap
from PIL import Image, ImageTk
import os

try:
    from . import config, utils, icon_loader
except ImportError:
    import config, utils, icon_loader


def open_window(parent, config=config, utils=utils):
    win = tk.Toplevel(parent)

    # --- Icon & Dock-Gruppierung ---
    icon_loader.link_icon(win, parent)

    win.title("🌱 VPD Comfort Chart")
    win.geometry("1600x900")
    win.configure(bg=config.BG)

    # ---------- HEADER ----------
    header = tk.Frame(win, bg=config.CARD)
    header.pack(side="top", fill="x", padx=10, pady=8)

    # Container für Logo + Titel nebeneinander
    left_frame = tk.Frame(header, bg=config.CARD)
    left_frame.pack(side="left", padx=6)

    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    logo_path = os.path.join(assets_dir, "Logo.png")
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path).resize((90, 90), Image.LANCZOS)
            logo_img = ImageTk.PhotoImage(img)
            logo_label = tk.Label(left_frame, image=logo_img, bg=config.CARD)
            logo_label.image = logo_img
            logo_label.pack(side="left", padx=(0, 10))
        except Exception as e:
            print(f"⚠️ Logo konnte nicht geladen werden: {e}")

    title = tk.Label(
        left_frame,
        text="🌱 VPD Comfort Chart",
        bg=config.CARD,
        fg=config.TEXT,
        font=("Segoe UI", 20, "bold"),
        anchor="w",
        justify="left"
    )
    title.pack(side="left", anchor="center")

    # ---------- HEADER CONTROLS ----------
    controls = tk.Frame(header, bg=config.CARD)
    controls.pack(side="right", pady=2)

    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    unit_celsius = cfg.get("unit_celsius", True)

    # Leaf Offset
    tk.Label(
        controls,
        text=f"Leaf Offset ({'°C' if unit_celsius else '°F'}):",
        bg=config.CARD, fg=config.TEXT
    ).pack(side="left", padx=6)

    start_val = config.leaf_offset_c[0] if unit_celsius else config.leaf_offset_c[0] * 9.0 / 5.0
    leaf_offset_var = tk.DoubleVar(value=start_val)

    def update_leaf_offset(*args):
        try:
            val = float(leaf_offset_var.get())
            config.leaf_offset_c[0] = val if unit_celsius else val * 5.0 / 9.0
        except Exception:
            config.leaf_offset_c[0] = 0.0

    leaf_offset_var.trace_add("write", update_leaf_offset)
    tk.Spinbox(
        controls, textvariable=leaf_offset_var,
        from_=-10.0, to=10.0, increment=0.1,
        width=6, bg=config.CARD, fg=config.TEXT,
        justify="center"
    ).pack(side="left")

    # Humidity Offset
    tk.Label(
        controls, text="Humidity Offset (%):",
        bg=config.CARD, fg=config.TEXT
    ).pack(side="left", padx=6)

    hum_offset_var = tk.DoubleVar(value=config.humidity_offset[0])

    def update_hum_offset(*args):
        try:
            config.humidity_offset[0] = float(hum_offset_var.get())
        except Exception:
            config.humidity_offset[0] = 0.0

    hum_offset_var.trace_add("write", update_hum_offset)
    tk.Spinbox(
        controls, textvariable=hum_offset_var,
        from_=-50.0, to=50.0, increment=1.0,
        width=6, bg=config.CARD, fg=config.TEXT,
        justify="center"
    ).pack(side="left")

    # Reset Offsets
    def reset_offsets():
        leaf_offset_var.set(0.0)
        hum_offset_var.set(0.0)
        config.leaf_offset_c[0] = 0.0
        config.humidity_offset[0] = 0.0

    tk.Button(
        controls, text="↺ Reset Offsets",
        command=reset_offsets,
        bg="orange", fg="black",
        font=("Segoe UI", 10, "bold")
    ).pack(side="left", padx=8)

    # ---------- MATPLOTLIB ----------
    fig, ax = plt.subplots(figsize=(9, 7), facecolor=config.BG)
    ax.set_facecolor(config.BG)
    ax.set_title("VPD Comfort Zones (All Cannabis Grow Stages)", color=config.TEXT, fontsize=13, pad=12)

    ax.set_xlabel(f"Temperature ({'°C' if unit_celsius else '°F'})", color=config.TEXT)
    ax.set_ylabel("Relative Humidity (%)", color=config.TEXT)
    ax.tick_params(colors=config.TEXT)

    # Gitter für VPD
    temps = np.linspace(10, 40, 300)
    hums  = np.linspace(0, 100, 300)
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

    if not unit_celsius:
        xticks_c = np.arange(10, 41, 5)
        xticks_f = [utils.c_to_f(x) for x in xticks_c]
        ax.set_xticks(xticks_c)
        ax.set_xticklabels([f"{f:.0f}" for f in xticks_f], color=config.TEXT)
        ax.set_xlabel("Temperature (°F)", color=config.TEXT)
        ax.set_xlim(10, 40)

    # Sensor-Punkte
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

    # ---------- UPDATE LOOP ----------
    def update():
        d = utils.safe_read_json(config.DATA_FILE)
        if not d:
            win.after(3000, update)
            return

        leaf_off = config.leaf_offset_c[0]
        hum_off  = config.humidity_offset[0]

        ti, hi = d.get("t_main"), d.get("h_main")
        te, he = d.get("t_ext"), d.get("h_ext")
        vpd_int = vpd_ext = None

        if ti is not None and hi is not None:
            ti_eff, hi_eff = ti + leaf_off, hi + hum_off
            internal_dot.set_offsets([[ti_eff, hi_eff]])
            vpd_int = calc_vpd(ti_eff, hi_eff)
        else:
            internal_dot.set_offsets([])

        if te is not None and he is not None:
            te_eff, he_eff = te + leaf_off, he + hum_off
            external_dot.set_offsets([[te_eff, he_eff]])
            vpd_ext = calc_vpd(te_eff, he_eff)
        else:
            external_dot.set_offsets([])

        unit = "°C" if unit_celsius else "°F"

        def disp_temp(val_c):
            return None if val_c is None else (val_c if unit_celsius else utils.c_to_f(val_c))

        lines = []
        if vpd_int is not None:
            lines.append(f"Internal: {disp_temp(ti):.1f}{unit} | {hi:.1f}% | VPD={vpd_int:.2f} kPa")
        if vpd_ext is not None:
            lines.append(f"External: {disp_temp(te):.1f}{unit} | {he:.1f}% | VPD={vpd_ext:.2f} kPa")

        info_box.set_text("\n".join(lines))

        canvas.draw_idle()
        win.after(3000, update)

    update()
    return win
