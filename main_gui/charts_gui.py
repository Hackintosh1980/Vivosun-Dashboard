#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
charts_gui.py – Dashboard mit Auto-Sensorerkennung
VIVOSUN Stable Green Edition 🌿
"""

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime, utils, config


# ---------------------------------------------------------
# Kartenfarben & Titel
# ---------------------------------------------------------
CARD_LAYOUT = [
    ("Internal Temp",  "t_main",  "#7eff9f"),
    ("Humidity",       "h_main",  "#00ffcc"),
    ("Internal VPD",   "vpd_int", "#00ffaa"),
    ("External Temp",  "t_ext",   "#66ccff"),
    ("External Hum.",  "h_ext",   "#ffaa00"),
    ("External VPD",   "vpd_ext", "#ff6666"),
]


def create_charts(root, config, log):
    """Erzeugt 6-Karten Dashboard mit Auto-Switch Compact ↔ Full."""
    log("📊 Chart-Grid initialisiert")

    frame = tk.Frame(root, bg=config.BG)
    frame.pack(fill="both", expand=True, padx=12, pady=(8, 10))

    data_buffers = {k: [] for _, k, _ in CARD_LAYOUT}
    data_buffers["timestamps"] = []

    mode = {"compact": True}
    log("[AUTO] Initial mode → Compact")

    cards, figs, axes, labels = [], [], [], []
    rows, cols = 2, 3

    for idx, (title, key, color) in enumerate(CARD_LAYOUT):
        r, c = divmod(idx, cols)
        card = tk.Frame(frame, bg=config.CARD, highlightthickness=1, highlightbackground=config.ACCENT)
        card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
        frame.grid_rowconfigure(r, weight=1)
        frame.grid_columnconfigure(c, weight=1)

        # ---------- Matplotlib ----------
        fig, ax = plt.subplots(figsize=(3.8, 1.8))
        fig.patch.set_facecolor(config.CARD)
        ax.set_facecolor(config.CARD)
        ax.tick_params(axis="x", colors=config.TEXT, labelsize=7)
        ax.tick_params(axis="y", colors=config.TEXT, labelsize=7)
        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.grid(True, color="#333", linestyle=":", alpha=0.4)
        for s in ax.spines.values():
            s.set_visible(False)

        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=(2, 2))

        # ---------- Wert ----------
        lbl_value = tk.Label(card, text="--", fg=color, bg=config.CARD,
                             font=("Segoe UI", 36, "bold"), anchor="w")
        lbl_value.place(relx=0.05, rely=0.10, anchor="w")

        # ---------- Titel ----------
        lbl_title = tk.Label(card, text=title, fg=config.TEXT, bg=config.CARD,
                             font=("Segoe UI", 13, "bold"), anchor="w")
        lbl_title.place(relx=0.05, rely=0.33, anchor="w")

        # ---------- Klick öffnet enlarged ----------
        def make_open(k=key):
            def _open(_=None):
                try:
                    from widgets.enlarged_charts import open_window
                    open_window(root, data_buffers, focus_key=k)
                except Exception as e:
                    log(f"⚠️ Fehler beim Öffnen enlarged_charts.py: {e}")
            return _open

        canvas.mpl_connect("button_press_event", make_open())
        cards.append((card, key))
        figs.append(fig)
        axes.append(ax)
        labels.append(lbl_value)

    # ---------- Nur interne am Anfang ----------
    for i, (_, key) in enumerate(cards):
        if key.startswith(("t_ext", "h_ext", "vpd_ext")):
            cards[i][0].grid_remove()

    # ---------------------------------------------------------
    # Update-Loop
    # ---------------------------------------------------------
    def update():
        try:
            d = utils.safe_read_json(config.DATA_FILE)
            if not d:
                root.after(3000, update)
                return

            ts = datetime.datetime.now()
            data_buffers["timestamps"].append(ts)

            # Prüfen, ob externer Sensor aktiv
            ext_ok = (d.get("t_ext") not in (None, 0.0)) or (d.get("h_ext") not in (None, 0.0))

            if ext_ok and mode["compact"]:
                log("[AUTO] switched → Full (external back)")
                mode["compact"] = False
                for i, (_, key) in enumerate(cards):
                    if key.startswith(("t_ext", "h_ext", "vpd_ext")):
                        cards[i][0].grid()
            elif not ext_ok and not mode["compact"]:
                log("[AUTO] switched → Compact (no external sensor)")
                mode["compact"] = True
                for i, (_, key) in enumerate(cards):
                    if key.startswith(("t_ext", "h_ext", "vpd_ext")):
                        cards[i][0].grid_remove()

            # Werte einlesen + VPD ggf. berechnen
            for _, key, _ in CARD_LAYOUT:
                val = d.get(key)
                if key.startswith("vpd_") and val is None:
                    if key == "vpd_int" and d.get("t_main") and d.get("h_main"):
                        val = utils.calc_vpd(
                            d["t_main"] + config.leaf_offset_c[0],
                            d["h_main"] + config.humidity_offset[0]
                        )
                    elif key == "vpd_ext" and d.get("t_ext") and d.get("h_ext"):
                        val = utils.calc_vpd(
                            d["t_ext"] + config.leaf_offset_c[0],
                            d["h_ext"] + config.humidity_offset[0]
                        )
                data_buffers[key].append(val if val is not None else None)
                data_buffers[key] = data_buffers[key][-60:]
            data_buffers["timestamps"] = data_buffers["timestamps"][-60:]

            # Charts rendern
            for i, (title, key, color) in enumerate(CARD_LAYOUT):
                if mode["compact"] and key.startswith("t_ext"):
                    continue
                val = data_buffers[key][-1] if data_buffers[key] else None
                ax = axes[i]
                lbl = labels[i]
                ax.clear()
                ax.set_facecolor(config.CARD)
                ax.grid(True, color="#222", linestyle=":", alpha=0.3)
                ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
                ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                for s in ax.spines.values():
                    s.set_visible(False)

                xs = mdates.date2num(data_buffers["timestamps"])
                ys = data_buffers[key]

                if len(xs) > 1:
                    ax.plot(xs, ys, color=color, linewidth=1.8)
                    ymin = min([y for y in ys if y is not None], default=0)
                    ax.fill_between(xs, ys, [ymin]*len(ys), color=color, alpha=0.12)

                # Einheit
                unit = "°C" if key.startswith("t_") else "%" if key.startswith("h_") else "kPa"
                if not config.unit_celsius and key.startswith("t_") and val is not None:
                    val = (val * 9/5) + 32
                    unit = "°F"

                lbl.config(text=f"{val:.2f}{unit}" if val is not None else "--")
                figs[i].tight_layout(pad=0.3)
                figs[i].canvas.draw_idle()

        except Exception as e:
            log(f"⚠️ Chart-Update-Fehler: {e}")

        root.after(3000, update)

    update()
    return frame, data_buffers, data_buffers["timestamps"]
