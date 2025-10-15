#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_chart_widget.py – 🌿 VIVOSUN Pro Chart mit 6 Live-Kurven & Info-Box.
Zeigt echte Werte aus data.json (Temp Main/Ext, Hum Main/Ext, VPD Int/Ext)
mit klarer 3-Achsen-Darstellung, schöner Auflösung & Echtzeit-Infobox.
"""

import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import utils, config, math

# --- Matplotlib Optik ---
plt.rcParams["lines.antialiased"] = True
plt.rcParams["axes.titlepad"] = 12
plt.rcParams["font.sans-serif"] = ["Segoe UI", "DejaVu Sans", "Arial"]
plt.rcParams["figure.dpi"] = 160  # schärfer


def _c_to_f(x):
    return x * 9.0 / 5.0 + 32.0


def create_chart_widget(parent, theme=None, config=config, utils=utils):
    """Erzeugt einen Live-Chart mit 6 Kurven & Info-Box."""
    theme = theme or getattr(config, "THEME", config)
    frame = theme.make_frame(parent, bg=theme.BG_MAIN, padx=10, pady=10)

    # --- Figure Setup ---
    fig, ax_temp = plt.subplots(figsize=(11, 5.8), dpi=140)
    fig.patch.set_facecolor(theme.CARD_BG)
    ax_temp.set_facecolor(theme.CARD_BG)
    ax_hum = ax_temp.twinx()
    ax_vpd = ax_temp.twinx()
    ax_vpd.spines["right"].set_position(("axes", 1.10))

    def style_axis(ax):
        ax.tick_params(colors=theme.TEXT, labelsize=9)
        for s in ax.spines.values():
            s.set_linewidth(1.0)
            s.set_color(theme.BORDER)
        ax.grid(True, color=theme.BORDER, linestyle="--", alpha=0.25)

    for ax in (ax_temp, ax_hum, ax_vpd):
        style_axis(ax)

    ax_temp.set_title("🌡️ VIVOSUN Live Environment", color=theme.TEXT, fontsize=14, weight="bold", pad=12)
    ax_temp.set_xlabel("Samples", color=theme.TEXT)
    ax_temp.set_ylabel("Temperature", color=theme.TEXT)
    ax_hum.set_ylabel("Humidity (%)", color=theme.TEXT)
    ax_vpd.set_ylabel("VPD (kPa)", color=theme.TEXT)

    # --- Canvas ---
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=6)

    # --- Datenpuffer ---
    data = {k: [] for k in ["t_main", "t_ext", "h_main", "h_ext", "vpd_int", "vpd_ext"]}
    _running = [True]

    # --- Info Box (unten rechts) ---
    info_box = ax_temp.text(
        0.995, 0.02,
        "—",
        transform=ax_temp.transAxes,
        fontsize=9,
        color=theme.TEXT,
        ha="right",
        va="bottom",
        bbox=dict(
            facecolor=theme.CARD_BG,
            edgecolor=theme.BORDER,
            boxstyle="round,pad=0.4",
            alpha=0.9
        )
    )

    # --- Status Label (unterhalb Chart) ---
    lbl_status = tk.Label(
        frame,
        text="⏳ Waiting for data ...",
        bg=theme.BG_MAIN,
        fg=theme.TEXT_DIM,
        font=("Consolas", 11)
    )
    lbl_status.pack(pady=4)

    # --- Helper ---
    def add(lst, val):
        if val is not None and not (isinstance(val, float) and math.isnan(val)):
            lst.append(val)
            if len(lst) > 250:
                del lst[:-250]

    def last(lst): return lst[-1] if lst else None

    # =========================================================
    # 🔄 RESET
    # =========================================================
    def reset_chart():
        for k in data:
            data[k].clear()
        for ax in (ax_temp, ax_hum, ax_vpd):
            ax.clear()
            ax.set_facecolor(theme.CARD_BG)
            style_axis(ax)
        ax_temp.set_title("🌡️ VIVOSUN Live Environment", color=theme.TEXT, fontsize=14, weight="bold", pad=12)
        info_box.set_text("🧹 Chart reset – waiting for data …")
        canvas.draw_idle()
        lbl_status.config(text="🧹 Chart reset.", fg=theme.TEXT_DIM)

    # =========================================================
    # 📡 POLL LOOP
    # =========================================================
    def poll_chart():
        if not _running[0]:
            return
        try:
            status = utils.safe_read_json(config.STATUS_FILE) or {}
            connected = status.get("connected", False)
            if not connected:
                lbl_status.config(text="[🔴] Disconnected", fg="red")
                frame.after(2000, poll_chart)
                return

            cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
            use_celsius = cfg.get("unit_celsius", True)
            leaf_off = float(cfg.get("leaf_offset", 0.0))
            hum_off = float(cfg.get("humidity_offset", 0.0))

            d = utils.safe_read_json(config.DATA_FILE) or {}
            t_main, h_main, t_ext, h_ext = d.get("t_main"), d.get("h_main"), d.get("t_ext"), d.get("h_ext")

            # Daten puffern
            add(data["t_main"], t_main + leaf_off if t_main is not None else None)
            add(data["t_ext"], t_ext + leaf_off if t_ext is not None else None)
            add(data["h_main"], h_main + hum_off if h_main is not None else None)
            add(data["h_ext"], h_ext + hum_off if h_ext is not None else None)

            # VPD berechnen
            vi = utils.calc_vpd(last(data["t_main"]), last(data["h_main"]))
            ve = utils.calc_vpd(last(data["t_ext"]), last(data["h_ext"]))
            add(data["vpd_int"], vi)
            add(data["vpd_ext"], ve)

            # --- Plot ---
            ax_temp.clear(); ax_hum.clear(); ax_vpd.clear()
            for ax in (ax_temp, ax_hum, ax_vpd):
                ax.set_facecolor(theme.CARD_BG)
                style_axis(ax)

            ax_temp.set_title("🌡️ VIVOSUN Live Environment", color=theme.TEXT, fontsize=14, weight="bold")
            ax_temp.set_xlabel("Samples", color=theme.TEXT)
            ax_temp.set_ylabel(f"Temperature ({'°C' if use_celsius else '°F'})", color=theme.TEXT)
            ax_hum.set_ylabel("Humidity (%)", color=theme.TEXT)
            ax_vpd.set_ylabel("VPD (kPa)", color=theme.TEXT)

            # Umrechnung °F falls nötig
            def disp_t(series):
                return series if use_celsius else [_c_to_f(x) for x in series]

            # Linienfarben
            colors = {
                "t_main": theme.BTN_PRIMARY,
                "t_ext": "#1E90FF",
                "h_main": "#00FF99",
                "h_ext": "#FFA500",
                "vpd_int": "#FF4444",
                "vpd_ext": "#AA66CC"
            }

            # Zeichnen
            if data["t_main"]:
                ax_temp.plot(disp_t(data["t_main"]), color=colors["t_main"], linewidth=2.2, alpha=0.9, label="T Main")
            if data["t_ext"]:
                ax_temp.plot(disp_t(data["t_ext"]), color=colors["t_ext"], linewidth=2.0, alpha=0.85, label="T Ext")

            if data["h_main"]:
                ax_hum.plot(data["h_main"], color=colors["h_main"], linestyle="--", linewidth=2.0, alpha=0.8, label="H Main")
            if data["h_ext"]:
                ax_hum.plot(data["h_ext"], color=colors["h_ext"], linestyle="--", linewidth=2.0, alpha=0.8, label="H Ext")

            if data["vpd_int"]:
                ax_vpd.plot(data["vpd_int"], color=colors["vpd_int"], linestyle=":", linewidth=2.0, alpha=0.9, label="VPD Int")
            if data["vpd_ext"]:
                ax_vpd.plot(data["vpd_ext"], color=colors["vpd_ext"], linestyle=":", linewidth=2.0, alpha=0.9, label="VPD Ext")

            # Legende
            lines, labels = [], []
            for ax in (ax_temp, ax_hum, ax_vpd):
                h, l = ax.get_legend_handles_labels()
                lines += h; labels += l
            if lines:
                leg = ax_temp.legend(
                    lines, labels,
                    facecolor=theme.CARD_BG,
                    edgecolor=theme.BORDER,
                    fontsize=9,
                    framealpha=0.85,
                    fancybox=True,
                    loc="upper left"
                )
                for t in leg.get_texts():
                    t.set_color(theme.TEXT)

            # --- Info Box Update ---
            hm, he, tm, te = last(data["h_main"]), last(data["h_ext"]), last(data["t_main"]), last(data["t_ext"])
            vi, ve = last(data["vpd_int"]), last(data["vpd_ext"])
            def fmt(v, s=""): return "—" if v is None else f"{v:.1f}{s}"
            info_box.set_text(
                f"Int → T:{fmt(tm, '°C' if use_celsius else '°F')}  H:{fmt(hm, '%')}  VPD:{fmt(vi, 'kPa')}\n"
                f"Ext → T:{fmt(te, '°C' if use_celsius else '°F')}  H:{fmt(he, '%')}  VPD:{fmt(ve, 'kPa')}"
            )

            canvas.draw_idle()
            lbl_status.config(
                text=f"[🟢] Connected | "
                     f"T_main:{fmt(tm)}°  H_main:{fmt(hm)}%  VPD_int:{fmt(vi)}kPa",
                fg=theme.LIME if hasattr(theme, "LIME") else "#00FF7F"
            )

        except Exception as e:
            lbl_status.config(text=f"⚠️ Poll error: {e}", fg="orange")

        frame.after(2000, poll_chart)

    # =========================================================
    # 🛑 STOP
    # =========================================================
    def stop_chart():
        _running[0] = False
        lbl_status.config(text="⏹ Chart stopped", fg="orange")

    poll_chart()
    return frame, reset_chart, stop_chart
