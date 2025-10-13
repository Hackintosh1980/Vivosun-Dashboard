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


CARD_LAYOUT = [
    ("Internal Temp",  "t_main",  "#ff6633"),
    ("Humidity",       "h_main",  "#4ac1ff"),
    ("Internal VPD",   "vpd_int", "#00ff99"),
    ("External Temp",  "t_ext",   "#ff00aa"),
    ("External Hum.",  "h_ext",   "#ffaa00"),
    ("External VPD",   "vpd_ext", "#ff4444"),
]


def create_charts(root, config, log):
    """Erzeugt 6-Karten Dashboard mit Auto-Switch Compact ↔ Full + dynamischer Y-Skalierung"""
    global data_buffers, time_buffer

    log("📊 Chart-Grid initialisiert")

    frame = tk.Frame(root, bg=config.BG)
    frame.pack(fill="both", expand=True, padx=10, pady=(4, 6))

    data_buffers = {k: [] for _, k, _ in CARD_LAYOUT}
    data_buffers["timestamps"] = []

    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    use_celsius = cfg.get("unit_celsius", True)
    temp_decimals = cfg.get("TEMP_DECIMALS", getattr(config, "TEMP_DECIMALS", 1))
    hum_decimals  = cfg.get("HUMID_DECIMALS", getattr(config, "HUMID_DECIMALS", 1))
    vpd_decimals  = cfg.get("VPD_DECIMALS", getattr(config, "VPD_DECIMALS", 2))





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
        for s in ax.spines.values():
            s.set_visible(False)
        ax.tick_params(colors="#666", labelsize=7)
        ax.grid(True, color="#222", linestyle=":", alpha=0.35)

        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=(4, 2))

        lbl_value = tk.Label(card, text="--", fg=color, bg=config.CARD, font=("Segoe UI", 40, "bold"))
        lbl_value.place(relx=0.04, rely=0.10, anchor="w")

        lbl_title = tk.Label(card, text=title.upper(), fg="#AAA", bg=config.CARD,
                             font=("Segoe UI Semibold", 18, "bold"))
        lbl_title.place(relx=0.04, rely=0.25, anchor="w")

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
        if key.startswith(("t_ext", "h_ext", "vpd_ext")):
            cards[i][0].grid_remove()

    def update():
        try:
            d = utils.safe_read_json(config.DATA_FILE)
            if not d:
                root.after(3000, update)
                return

            # Wenn alle Werte None sind → komplette Buffer leeren und Anzeige resetten
            if all(v is None for v in d.values()):
                for key in data_buffers:
                    if isinstance(data_buffers[key], list):
                        data_buffers[key].clear()
                data_buffers["timestamps"].clear()

                for lbl in labels:
                    lbl.config(text="--")
                for ax in axes:
                    ax.clear()
                    ax.set_facecolor(config.CARD)
                    ax.grid(True, color="#333", linestyle=":", alpha=0.35)
                for fig in figs:
                    fig.canvas.draw_idle()

                root.after(3000, update)
                return

            ts = datetime.datetime.now()
            data_buffers["timestamps"].append(ts)

            # --- Externer Sensor erkannt oder entfernt? ---
            ext_ok = d.get("t_ext") not in (None, 0.0) or d.get("h_ext") not in (None, 0.0)
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

            # --- 🧩 Hotplug-Fix: sofortige Werte bei neuem Gerät ---
            try:
                if "device_id" in d and d["device_id"]:
                    # Falls Datenpuffer leer ist → initialisieren
                    if not data_buffers["timestamps"]:
                        ts = datetime.datetime.now()
                        data_buffers["timestamps"].append(ts)
                        for key in ("t_main", "h_main", "vpd_int", "t_ext", "h_ext", "vpd_ext"):
                            if key in d and d[key] is not None:
                                data_buffers[key].append(d[key])

                    # Labels sofort aktualisieren
                    decimals = {
                        "t_main": config.TEMP_DECIMALS,
                        "h_main": config.HUMID_DECIMALS,
                        "vpd_int": config.VPD_DECIMALS,
                    }
                    for lbl, key in zip(labels, ("t_main", "h_main", "vpd_int")):
                        if key in d and d[key] is not None:
                            lbl.config(text=f"{d[key]:.{decimals[key]}f}")
            except Exception as e:
                print(f"⚠️ Hotplug-Update-Fehler: {e}")

            # --- Automatische Wiederaufnahme ---
            for _, key, _ in CARD_LAYOUT:
                val = d.get(key)

                # VPD dynamisch nachrechnen, falls nötig
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

                # Nur gültige Werte hinzufügen
                if val is not None:
                    data_buffers[key].append(val)
                    data_buffers[key] = data_buffers[key][-200:]

            data_buffers["timestamps"] = data_buffers["timestamps"][-200:]

            # --- Zeichnen der Charts ---
            for i, (title, key, color) in enumerate(CARD_LAYOUT):
                if mode["compact"] and key.startswith("t_ext"):
                    continue

                val = data_buffers[key][-1] if data_buffers[key] else None
                ax = axes[i]
                lbl = labels[i]
                ax.clear()

                x = data_buffers["timestamps"]
                y = data_buffers[key]

                if len(x) > 1 and any(v is not None for v in y):
                    ax.plot(x, y, color=color, linewidth=2.0, alpha=0.9)
                    ax.fill_between(x, y, min(y), color=color, alpha=0.15)

                    y_min, y_max = min(y), max(y)
                    if y_min == y_max:
                        y_min -= 0.5
                        y_max += 0.5
                    else:
                        pad = (y_max - y_min) * 0.2
                        y_min -= pad
                        y_max += pad
                    ax.set_ylim(y_min, y_max)

                ax.set_facecolor(config.CARD)
                ax.grid(True, color="#333", linestyle=":", alpha=0.35)
                ax.tick_params(colors="#666", labelsize=7)

                if len(x) > 0:
                    step = max(1, len(x) // 6)
                    ax.set_xticks(x[::step])
                    ax.set_xticklabels(
                        [t.strftime("%H:%M") for t in x[::step]],
                        fontsize=7, color="#777"
                    )

                for s in ax.spines.values():
                    s.set_visible(False)

                ax.set_xlabel("", color="#777", fontsize=7)
                ax.set_ylabel("", color="#777", fontsize=7)

                # --- Dynamische Nachkommastellen ---
                if val is not None:
                    if key.startswith("t_"):
                        disp_val = val if use_celsius else utils.c_to_f(val)
                        unit = "°C" if use_celsius else "°F"
                        lbl.config(text=f"{disp_val:.{temp_decimals}f}{unit}")
                    elif key.startswith("h_"):
                        lbl.config(text=f"{val:.{hum_decimals}f}%")
                    else:
                        lbl.config(text=f"{val:.{vpd_decimals}f} kPa")
                else:
                    lbl.config(text="--")

                figs[i].tight_layout(pad=0.4)
                figs[i].canvas.draw_idle()

        except Exception as e:
            log(f"⚠️ Chart-Update-Fehler: {e}")

        root.after(3000, update)

    update()
    return frame, data_buffers, data_buffers["timestamps"]
