#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
charts_gui.py – VIVOSUN Dashboard Charts (clean & stable)
6 Charts (Temp/Hum/VPD für intern + extern) mit Auto-Switch Compact ↔ Full
- nutzt utils.calc_vpd
- Offsets (leaf_offset, humidity_offset) live aus config.json
- Umschaltung anhand status.json (sensor_ok_ext)
- Klick öffnet widgets/enlarged_charts.open_window
"""

import tkinter as tk
import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import utils, config

# Titel, Key, Farbe
CARD_LAYOUT = [
    ("🌡️ Internal Temp", "t_main",  "#ff6633"),
    ("💧 Humidity",       "h_main",  "#4ac1ff"),
    ("🫧 Internal VPD",   "vpd_int", "#00ff99"),
    ("🌡️ External Temp", "t_ext",   "#ff00aa"),
    ("💧 External Hum.",  "h_ext",   "#ffaa00"),
    ("🫧 External VPD",   "vpd_ext", "#ff4444"),
]

# Globale Referenz (optional für externe Resets)
global_data_buffers = None


def create_charts(parent, config, log=lambda *a, **k: None):
    """Erzeugt 6-Karten-Dashboard mit Auto-Switch Compact ↔ Full + Click-to-Enlarge."""
    frame = tk.Frame(parent, bg=config.BG)
    frame.pack(fill="both", expand=True)

    # --- Anzeige-Config ---
    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    use_celsius   = cfg.get("unit_celsius", True)
    temp_decimals = cfg.get("TEMP_DECIMALS", getattr(config, "TEMP_DECIMALS", 1))
    hum_decimals  = cfg.get("HUMID_DECIMALS", getattr(config, "HUMID_DECIMALS", 1))
    vpd_decimals  = cfg.get("VPD_DECIMALS", getattr(config, "VPD_DECIMALS", 2))

    # --- Datenpuffer ---
    data_buffers = {k: [] for _, k, _ in CARD_LAYOUT}
    data_buffers["timestamps"] = []

    # globale Referenz aktualisieren
    global global_data_buffers
    global_data_buffers = data_buffers

# --- Chart-Grid ---
    cards, axes, figs, labels = [], [], [], []
    rows, cols = 2, 3

    for idx, (title, key, color) in enumerate(CARD_LAYOUT):
        r, c = divmod(idx, cols)
        card = tk.Frame(
            frame,
            bg=config.CARD,
            highlightthickness=1,
            highlightbackground="#2a2a2a",
            relief="flat"
        )
        card.grid(row=r, column=c, padx=14, pady=14, sticky="nsew")
        frame.grid_rowconfigure(r, weight=1)
        frame.grid_columnconfigure(c, weight=1)

        # --- Hover-Effekt (dezent, kein Blinken) ---
        def on_enter(e, c=card): 
            c.config(highlightbackground="#555")
        def on_leave(e, c=card): 
            c.config(highlightbackground="#2a2a2a")

        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

        # --- Matplotlib Chart ---
        fig, ax = plt.subplots(figsize=(4.1, 2.0))
        fig.patch.set_facecolor(config.CARD)
        ax.set_facecolor("#1a1a1a")
        ax.grid(True, color="#333", linestyle=":", alpha=0.25)
        ax.tick_params(colors="#999", labelsize=7)
        for s in ax.spines.values():
            s.set_visible(False)

        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=(4, 2))

        # --- Großer Wert oben links ---
        lbl_value = tk.Label(
            card,
            text="--",
            fg=color,
            bg=config.CARD,
            font=("Segoe UI", 40, "bold"),
            anchor="w",
            justify="left"
        )
        lbl_value.place(relx=0.08, rely=0.0, anchor="nw")

        # --- Titel darunter (links) ---
        lbl_title = tk.Label(
            card,
            text=title.upper(),
            fg="#b8b8b8",
            bg=config.CARD,
            font=("Segoe UI Semibold", 18, "bold"),
            anchor="w",
            justify="left"
        )
        lbl_title.place(relx=0.08, rely=0.2, anchor="nw")

        # --- Klick → Enlarged View ---
        def make_open(key=key):
            def _open(event=None):
                try:
                    from widgets.enlarged_charts import open_window
                    open_window(parent, data_buffers, focus_key=key)
                    log(f"🔍 Enlarged view opened for {key}")
                except Exception as e:
                    log(f"⚠️ Fehler beim Öffnen enlarged_charts.py: {e}")
            return _open

        canvas.mpl_connect("button_press_event", make_open())

        cards.append((card, key))
        axes.append(ax)
        figs.append(fig)
        labels.append(lbl_value)
        
    # Start im Compact-Mode (nur interne Karten sichtbar)
    mode = {"compact": True}
    for i, (_, key) in enumerate(cards):
        if key.startswith(("t_ext", "h_ext", "vpd_ext")):
            cards[i][0].grid_remove()
    log("📊 Charts gestartet (Compact Mode)")

    # --- Reset-Funktion ---
    def reset_charts():
        try:
            for k, buf in data_buffers.items():
                if isinstance(buf, list):
                    buf.clear()
            for ax in axes:
                ax.clear()
                ax.set_facecolor(config.CARD)
                ax.grid(True, color="#222", linestyle=":", alpha=0.35)
                ax.tick_params(colors="#999", labelsize=7)
                for s in ax.spines.values():
                    s.set_visible(False)
            for fig in figs:
                fig.canvas.draw_idle()
            for lbl in labels:
                lbl.config(text="--")
            log("✅ Charts reset (Buffer + Anzeige).")
        except Exception as e:
            log(f"⚠️ Fehler beim Chart-Reset: {e}")

    frame.reset_charts = reset_charts

    # --- Anzeige-Helfer ---
    def _fmt_temp(val_c):
        return val_c if use_celsius else utils.c_to_f(val_c)

    # --- VPD sicher berechnen (None-tolerant) ---
    def _vpd_safe(temp_c, rh):
        if temp_c is None or rh is None:
            return None
        return utils.calc_vpd(temp_c, rh)

    # --- Update Loop ---
    def update():
        try:
            # Sensorstatus → ext-Karten sichtbar/unsichtbar
            st = utils.safe_read_json(config.STATUS_FILE) or {}
            ext_ok = bool(st.get("sensor_ok_ext", False))
            if ext_ok and mode["compact"]:
                mode["compact"] = False
                for i, (_, key) in enumerate(cards):
                    if key.startswith(("t_ext", "h_ext", "vpd_ext")):
                        cards[i][0].grid()
                log("🔁 Full Mode (external detected)")
            elif not ext_ok and not mode["compact"]:
                mode["compact"] = True
                for i, (_, key) in enumerate(cards):
                    if key.startswith(("t_ext", "h_ext", "vpd_ext")):
                        cards[i][0].grid_remove()
                log("🔁 Compact Mode (no external sensor)")

            # Daten lesen
            d = utils.safe_read_json(config.DATA_FILE) or {}
            if not d or all(v is None for v in d.values()):
                reset_charts()
                frame.after(2000, update)
                return

            ts = datetime.datetime.now()
            data_buffers["timestamps"].append(ts)
            data_buffers["timestamps"] = data_buffers["timestamps"][-200:]

            # Messwerte
            t_main = d.get("t_main")
            h_main = d.get("h_main")
            t_ext  = d.get("t_ext")
            h_ext  = d.get("h_ext")

            # Offsets pro Tick aus config.json lesen
            cfg_live = utils.safe_read_json(config.CONFIG_FILE) or {}
            leaf_off = float(cfg_live.get("leaf_offset", 0.0))
            hum_off  = float(cfg_live.get("humidity_offset", 0.0))

            # VPD (intern + extern) mit Offsets (Temp-Delta in °C, RH-Delta in %)
            vpd_int = _vpd_safe(
                (t_main + leaf_off) if t_main is not None else None,
                (h_main + hum_off)  if h_main is not None else None
            )
            vpd_ext = _vpd_safe(
                (t_ext + leaf_off) if t_ext is not None else None,
                (h_ext + hum_off)  if h_ext is not None else None
            )

            # Snapshot (für Charts: Humidity mit Offset anzeigen, Temp ohne Offset)
            snapshot = {
                "t_main": t_main,
                "h_main": (h_main + hum_off) if h_main is not None else None,
                "vpd_int": vpd_int,
                "t_ext": t_ext,
                "h_ext": (h_ext + hum_off) if h_ext is not None else None,
                "vpd_ext": vpd_ext
            }

            for _, key, _ in CARD_LAYOUT:
                data_buffers[key].append(snapshot.get(key))
            for _, key, _ in CARD_LAYOUT:
                data_buffers[key] = data_buffers[key][-200:]

            # Zeichnen
            for ax, (title, key, color), lbl in zip(axes, CARD_LAYOUT, labels):
                if mode["compact"] and key.startswith(("t_ext", "h_ext", "vpd_ext")):
                    continue

                x = data_buffers["timestamps"]
                y = data_buffers[key]

                ax.clear()
                ax.set_facecolor(config.CARD)
                ax.grid(True, color="#222", linestyle=":", alpha=0.35)
                ax.tick_params(colors="#999", labelsize=7)
                for s in ax.spines.values():
                    s.set_visible(False)

                if len(x) > 1 and any(v is not None for v in y):
                    ax.plot(x, y, color=color, linewidth=2.3, alpha=0.95)
                    try:
                        ymin = min(v for v in y if v is not None)
                        ax.fill_between(x, y, ymin, alpha=0.12, color=color)
                    except ValueError:
                        pass

                if len(x) > 0:
                    step = max(1, len(x) // 6)
                    ax.set_xticks(x[::step])
                    ax.set_xticklabels([t.strftime("%H:%M") for t in x[::step]], fontsize=7, color="#888")

                latest = y[-1] if y else None
                if latest is not None:
                    if key.startswith("t_"):
                        disp = _fmt_temp(latest)
                        unit = "°C" if use_celsius else "°F"
                        lbl.config(text=f"{disp:.{temp_decimals}f}{unit}")
                    elif key.startswith("h_"):
                        lbl.config(text=f"{latest:.{hum_decimals}f}%")
                    else:
                        lbl.config(text=f"{latest:.{vpd_decimals}f} kPa")
                else:
                    lbl.config(text="--")

            for fig in figs:
                fig.tight_layout(pad=0.6)
                fig.canvas.draw_idle()

        except Exception as e:
            log(f"⚠️ Chart-Update-Fehler: {e}")

        frame.after(2000, update)

    update()

    # Referenzen
    try:
        import builtins
        builtins._vivosun_chart_frame = frame
    except Exception:
        pass

    try:
        config.active_charts_frame = frame
    except Exception:
        pass

    return frame, data_buffers, data_buffers["timestamps"]
