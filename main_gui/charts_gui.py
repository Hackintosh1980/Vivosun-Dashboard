#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
charts_gui.py – Dashboard mit Auto-Sensorerkennung
Zeigt interne / externe Temperatur, Luftfeuchte & VPD
und schaltet automatisch Compact ↔ Full, ohne die Charts zu verlieren.
"""

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import datetime, utils, config


# -------------------------------------------------------------------
# Kartenfarben & Titel
# -------------------------------------------------------------------
CARD_LAYOUT = [
    ("Internal Temp",  "t_main",  "#ff6633"),
    ("Humidity",       "h_main",  "#4ac1ff"),
    ("Internal VPD",   "vpd_int", "#00ff99"),
    ("External Temp",  "t_ext",   "#ff00aa"),
    ("External Hum.",  "h_ext",   "#ffaa00"),
    ("External VPD",   "vpd_ext", "#ff4444"),
]

def create_charts(root, config, log):
    """Erzeugt 6-Karten Dashboard mit Auto-Switch Compact ↔ Full."""
    log("📊 Chart-Grid initialisiert")

    frame = tk.Frame(root, bg=config.BG)
    frame.pack(fill="both", expand=True, padx=10, pady=(4, 6))

    data_buffers = {k: [] for _, k, _ in CARD_LAYOUT}
    data_buffers["timestamps"] = []

    mode = {"compact": True}
    log("[AUTO] Initial mode → Compact")

    cards, figs, axes, labels = [], [], [], []
    rows, cols = 2, 3

    for idx, (title, key, color) in enumerate(CARD_LAYOUT):
        r, c = divmod(idx, cols)
        card = tk.Frame(frame, bg=config.CARD, highlightthickness=1, highlightbackground="#333")
        card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
        frame.grid_rowconfigure(r, weight=1)
        frame.grid_columnconfigure(c, weight=1)

        fig, ax = plt.subplots(figsize=(3.8, 1.8))
        fig.patch.set_facecolor(config.CARD)
        ax.set_facecolor(config.CARD)
        ax.tick_params(colors=config.TEXT, labelsize=8)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.grid(True, color="#222", linestyle=":", alpha=0.4)
        ax.set_xticks([]); ax.set_yticks([])

        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=(4, 2))

        # --- Titel & Wert optisch aufwerten ---
        lbl_value = tk.Label(
            card,
            text="--",
            fg=color,
            bg=config.CARD,
            font=("Segoe UI", 40, "bold")  # größerer Wert
        )
        lbl_value.place(relx=0.04, rely=0.10, anchor="w")

        lbl_title = tk.Label(
            card,
            text=title.upper(),  # Großbuchstaben für mehr "Dashboard-Look"
            fg="#AAA",
            bg=config.CARD,
            font=("Segoe UI Semibold", 18, "bold")
        )
        lbl_title.place(relx=0.04, rely=0.25, anchor="w")

        # Klick öffnet enlarged
        def make_open(key=key):
            def _open(event=None):
                try:
                    from widgets.enlarged_charts import open_window
                    open_window(root, data_buffers, focus_key=key)
                except Exception as e:
                    log(f"⚠️ Fehler beim Öffnen enlarged_charts.py: {e}")
            return _open
        canvas.mpl_connect("button_press_event", make_open())

        cards.append((card, key))
        figs.append(fig)
        axes.append(ax)
        labels.append(lbl_value)

    for i, (_, key) in enumerate(cards):
        if key.startswith("t_ext") or key.startswith("h_ext") or key.startswith("vpd_ext"):
            cards[i][0].grid_remove()

    def update():
        try:
            d = utils.safe_read_json(config.DATA_FILE)
            if not d:
                root.after(3000, update)
                return

            ts = datetime.datetime.now()
            data_buffers["timestamps"].append(ts)

            ext_ok = d.get("t_ext") not in (None, 0.0) or d.get("h_ext") not in (None, 0.0)

            if ext_ok and mode["compact"]:
                log("[AUTO] switched → Full (external back)")
                mode["compact"] = False
                for i, (_, key) in enumerate(cards):
                    if key.startswith("t_ext") or key.startswith("h_ext") or key.startswith("vpd_ext"):
                        cards[i][0].grid()
            elif not ext_ok and not mode["compact"]:
                log("[AUTO] switched → Compact (no external sensor)")
                mode["compact"] = True
                for i, (_, key) in enumerate(cards):
                    if key.startswith("t_ext") or key.startswith("h_ext") or key.startswith("vpd_ext"):
                        cards[i][0].grid_remove()

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

# --- Charts schöner zeichnen ---
            for i, (title, key, color) in enumerate(CARD_LAYOUT):
                if mode["compact"] and key.startswith("t_ext"):
                    continue
                val = data_buffers[key][-1] if data_buffers[key] else None
                ax = axes[i]
                lbl = labels[i]

                ax.clear()
                yvals = data_buffers[key]
                xvals = data_buffers["timestamps"]

                # Linie + Fülleffekt
                ax.plot(
                    xvals,
                    yvals,
                    color=color,
                    linewidth=2.8,
                    alpha=0.9
                )
                # dezenter Fülleffekt unter der Linie
                if len(yvals) > 1:
                    ax.fill_between(
                        xvals,
                        yvals,
                        color=color,
                        alpha=0.12  # halbtransparent
                    )

                # Grundgestaltung
                ax.set_facecolor(config.CARD)
                ax.grid(True, color="#333", linestyle=":", alpha=0.35)
                for s in ax.spines.values():
                    s.set_visible(False)

                # dezente Achsenbeschriftung
                ax.tick_params(colors="#666", labelsize=7)
                ax.yaxis.set_label_position("right")
                ax.yaxis.tick_right()
                if key.startswith("t_"):
                    ax.set_ylabel("°C", color="#666", fontsize=8, labelpad=4)
                elif key.startswith("h_"):
                    ax.set_ylabel("%", color="#666", fontsize=8, labelpad=4)
                elif key.startswith("vpd_"):
                    ax.set_ylabel("kPa", color="#666", fontsize=8, labelpad=4)

                # Achsenlimits automatisch, aber etwas gepuffert
                if yvals and any(v is not None for v in yvals):
                    valid = [v for v in yvals if v is not None]
                    ymin, ymax = min(valid), max(valid)
                    pad = (ymax - ymin) * 0.1 if ymax != ymin else 1
                    ax.set_ylim(ymin - pad, ymax + pad)

                # Wertlabel im GUI aktualisieren
                unit = "°C" if key.startswith("t_") else "%" if key.startswith("h_") else " kPa"
                lbl.config(text=f"{val:.1f}{unit}" if val is not None else "--")

                figs[i].tight_layout(pad=0.4)
                figs[i].canvas.draw_idle()

        except Exception as e:
            log(f"⚠️ Chart-Update-Fehler: {e}")

        root.after(3000, update)

    update()
    return frame
