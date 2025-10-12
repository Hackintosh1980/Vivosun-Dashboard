#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
charts_gui.py – Dashboard mit Auto-Sensorerkennung
VIVOSUN Stable Green Edition 🌿 (Matplotlib 3.9-kompatibel, sofortige Anzeige)
"""

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import FormatStrFormatter
from matplotlib.patches import Rectangle
import datetime, utils, config


# ---------------------------------------------------------
# Kartenfarben & Titel (muss zu enlarged_charts.COLOR_MAP passen)
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
    """Erzeugt 6-Karten Dashboard mit Auto-Switch Compact ↔ Full (flackerfrei)."""
    log("📊 Chart-Grid initialisiert")

    frame = tk.Frame(root, bg=config.BG)
    frame.pack(fill="both", expand=True, padx=12, pady=(8, 10))

    # Datenpuffer
    data_buffers = {k: [] for _, k, _ in CARD_LAYOUT}
    data_buffers["timestamps"] = []

    global GLOBAL_DATA_BUFFERS
    GLOBAL_DATA_BUFFERS = data_buffers

    mode = {"compact": True}
    log("[AUTO] Initial mode → Compact")

    cards, figs, axes, labels = [], [], [], []
    rows, cols = 2, 3

    # ---------------------------------------------------------
    # Karten erstellen
    # ---------------------------------------------------------
    for idx, (title, key, color) in enumerate(CARD_LAYOUT):
        r, c = divmod(idx, cols)
        card = tk.Frame(frame, bg=config.CARD, highlightthickness=1,
                        highlightbackground=config.ACCENT, relief="flat")
        card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
        frame.grid_rowconfigure(r, weight=1)
        frame.grid_columnconfigure(c, weight=1)

        # ---------- Matplotlib-Setup ----------
        fig, ax = plt.subplots(figsize=(3.8, 1.8))
        fig.patch.set_facecolor(config.CARD)
        ax.set_facecolor(config.CARD)

        ax.tick_params(axis="x", colors=config.TEXT, labelsize=7)
        ax.tick_params(axis="y", colors=config.TEXT, labelsize=7)
        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=15))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        ax.grid(True, color="#333", linestyle=":", alpha=0.3)
        for s in ax.spines.values():
            s.set_visible(False)

        # dezenter Hintergrund
        gradient_rect = Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                                  color=color, alpha=0.06, zorder=-10)
        ax.add_patch(gradient_rect)

        # Placeholder
        ax.text(0.5, 0.5, "— No Data —", color="#888", fontsize=10,
                fontweight="bold", ha="center", va="center",
                transform=ax.transAxes)

        fig.tight_layout(pad=0.3)
        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True, padx=4, pady=(2, 2))
        canvas.draw_idle()

        # ---------- Werte-Anzeige ----------
        lbl_value = tk.Label(card, text="--", fg=color, bg=config.CARD,
                             font=("Segoe UI", 38, "bold"), anchor="w")
        lbl_value.place(relx=0.05, rely=0.10, anchor="w")

        lbl_title = tk.Label(card, text=title, fg=color, bg=config.CARD,
                             font=("Segoe UI", 18, "bold"), anchor="w")
        lbl_title.place(relx=0.05, rely=0.23, anchor="w")

        # Klick öffnet vergrößertes Chart
        def make_open(k=key):
            def _open(_evt=None):
                try:
                    from widgets.enlarged_charts import open_window
                    open_window(root, data_buffers, focus_key=k)
                    log(f"🟢 Enlarged geöffnet für {k}")
                except Exception as e:
                    log(f"⚠️ Fehler beim Öffnen enlarged_charts.py: {e}")
            return _open

        canvas.mpl_connect("button_press_event", make_open())
        canvas_widget.bind("<Button-1>", make_open())

        cards.append((card, key))
        figs.append(fig)
        axes.append(ax)
        labels.append(lbl_value)

    # Anfangs nur interne anzeigen
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

            # Compact ↔ Full switch
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

            # Werte + VPD berechnen
            for _, key, _ in CARD_LAYOUT:
                val = d.get(key)
                if val is None:
                    if key == "vpd_int" and d.get("t_main") and d.get("h_main"):
                        val = utils.calc_vpd(d["t_main"], d["h_main"])
                    elif key == "vpd_ext" and d.get("t_ext") and d.get("h_ext"):
                        val = utils.calc_vpd(d["t_ext"], d["h_ext"])
                data_buffers[key].append(val)
                del data_buffers[key][:-60]
            del data_buffers["timestamps"][:-60]

            # Charts rendern
            for i, (title, key, color) in enumerate(CARD_LAYOUT):
                if mode["compact"] and key.startswith("t_ext"):
                    continue

                ax = axes[i]
                lbl = labels[i]
                xs = mdates.date2num(data_buffers["timestamps"])
                ys = data_buffers[key]
                val = ys[-1] if ys else None

                # Sicheres Entfernen aller Linien & Flächen (Matplotlib 3.9+ kompatibel)
                for line in list(ax.lines):
                    try:
                        line.remove()
                    except Exception:
                        pass
                for coll in list(ax.collections):
                    try:
                        coll.remove()
                    except Exception:
                        pass

                # Plot sofort zeichnen, auch bei 1 Punkt
                if len(xs) >= 1:
                    ax.plot(xs, ys, color=color, linewidth=1.8, marker="o", markersize=3)
                    ymin = min((y for y in ys if y is not None), default=0)
                    ax.fill_between(xs, ys, [ymin]*len(ys), color=color, alpha=0.15)

                # Formatierung & Einheit
                if key.startswith("vpd_"):
                    ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
                    unit = "kPa"
                elif key.startswith("t_"):
                    ax.yaxis.set_major_formatter(FormatStrFormatter("%.1f"))
                    unit = "°C" if config.unit_celsius else "°F"
                else:
                    ax.yaxis.set_major_formatter(FormatStrFormatter("%.0f"))
                    unit = "%"

                if val is not None:
                    if key.startswith("t_") and not config.unit_celsius:
                        val = (val * 9/5) + 32
                    lbl.config(text=f"{val:.2f}{unit}")
                else:
                    lbl.config(text="--")

                figs[i].canvas.draw_idle()

        except Exception as e:
            log(f"⚠️ Chart-Update-Fehler: {e}")

        root.after(3000, update)

    # Erstes Update leicht verzögert (verhindert Startflackern)
    root.after(250, update)
    return frame, data_buffers, data_buffers["timestamps"]
