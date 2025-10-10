#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import datetime
from collections import deque
import tkinter as tk
from tkinter import scrolledtext, TclError, filedialog   # <--- filedialog hier ergänzt

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk,
)
from matplotlib.animation import FuncAnimation
import matplotlib.patheffects as path_effects
from matplotlib.backend_bases import cursors

# Robust: Direktstart & Paketstart
try:
    from . import config, utils, async_reader, icon_loader
except ImportError:
    import config, utils, async_reader, icon_loader
# Footer-Widget einbinden
try:
    from .footer_widget import create_footer
except ImportError:
    from footer_widget import create_footer


def run_app(device_id=None):
    root = tk.Tk()
    root.title(config.APP_DISPLAY if hasattr(config, "APP_DISPLAY") else "🌱 VIVOSUN Thermo Dashboard")
    root.geometry("1600x900")
    root.configure(bg=getattr(config, "BG", "#0b1620"))

    # Icon für Fenster + Dock setzen
    try:
        icon_loader.set_app_icon(root)
    except Exception:
        pass

    # ---------- HEADER ----------
    from PIL import Image, ImageTk
    header = tk.Frame(root, bg=config.CARD)
    header.pack(side="top", fill="x", padx=10, pady=8)

    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    logo_path = os.path.join(assets_dir, "Logo.png")

    left_frame = tk.Frame(header, bg=config.CARD)
    left_frame.pack(side="left", padx=6)

    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path).resize((120, 120), Image.LANCZOS)
            logo_img = ImageTk.PhotoImage(img)
            logo_label = tk.Label(left_frame, image=logo_img, bg=config.CARD)
            logo_label.image = logo_img
            logo_label.pack(side="left", padx=(0, 10))
        except Exception as e:
            print(f"⚠️ Logo konnte nicht geladen werden: {e}")

    title = tk.Label(
        left_frame,
        text="🌱 VIVOSUN Thermo Dashboard \n     for THB-1S",
        bg=config.CARD,
        fg=config.TEXT,
        font=("Segoe UI", 20, "bold"),
        anchor="w",
        justify="left"
    )
    title.pack(side="left", anchor="center")

    # --- Controls rechts ---
    controls = tk.Frame(header, bg=config.CARD)
    controls.pack(side="right", pady=2)

    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    unit_celsius = tk.BooleanVar(value=cfg.get("unit_celsius", True))

    # Leaf Offset
    tk.Label(
        controls,
        text=f"Leaf Temp Offset ({'°C' if unit_celsius.get() else '°F'}):",
        bg=config.CARD,
        fg=config.TEXT
    ).pack(side="left", padx=6)

    leaf_offset_var = tk.DoubleVar(value=config.leaf_offset_c[0])

    def update_leaf_offset(*_):
        try:
            val = float(leaf_offset_var.get())
            config.leaf_offset_c[0] = val if unit_celsius.get() else val * 5.0 / 9.0
        except Exception:
            config.leaf_offset_c[0] = 0.0

    leaf_offset_var.trace_add("write", update_leaf_offset)

    tk.Spinbox(
        controls,
        textvariable=leaf_offset_var,
        from_=-10.0, to=10.0, increment=0.1,
        width=6,
        bg=config.CARD,
        fg=config.TEXT,
        justify="center"
    ).pack(side="left")

    # Humidity Offset
    tk.Label(
        controls,
        text="Humidity Offset (%):",
        bg=config.CARD,
        fg=config.TEXT
    ).pack(side="left", padx=6)

    hum_offset_var = tk.DoubleVar(value=config.humidity_offset[0])

    def update_hum_offset(*_):
        try:
            config.humidity_offset[0] = float(hum_offset_var.get())
        except Exception:
            config.humidity_offset[0] = 0.0

    hum_offset_var.trace_add("write", update_hum_offset)

    tk.Spinbox(
        controls,
        textvariable=hum_offset_var,
        from_=-20.0, to=20.0, increment=0.5,
        width=6,
        bg=config.CARD,
        fg=config.TEXT,
        justify="center"
    ).pack(side="left")

    # Reset Offsets
    def reset_offsets():
        leaf_offset_var.set(0.0)
        hum_offset_var.set(0.0)
        config.leaf_offset_c[0] = 0.0
        config.humidity_offset[0] = 0.0
        log("Offsets reset (Leaf=0.0°C, Humidity=0.0%)")

    tk.Button(
        controls,
        text="↺ Reset Offsets",
        command=reset_offsets,
        bg="orange",
        fg="black"
    ).pack(side="left", padx=6)

    # --- Sync zurück ins GUI (einmalig; Reschedule macht der Safe-Wrapper unten) ---
    def refresh_offset_fields_once():
        try:
            if unit_celsius.get():
                gui_val = config.leaf_offset_c[0]
            else:
                gui_val = config.leaf_offset_c[0] * 9.0 / 5.0

            if leaf_offset_var.get() != gui_val:
                leaf_offset_var.set(gui_val)

            if hum_offset_var.get() != config.humidity_offset[0]:
                hum_offset_var.set(config.humidity_offset[0])
        except TclError:
            return

    # ---------- HEADER BUTTON ROWS ----------
    button_frame = tk.Frame(header, bg=config.CARD)
    button_frame.pack(side="bottom", fill="x", pady=4)

    row1 = tk.Frame(button_frame, bg=config.CARD)
    row1.pack(side="top", pady=2)

    row2 = tk.Frame(button_frame, bg=config.CARD)
    row2.pack(side="top", pady=2)

    # ---------- LOG ----------
    logframe = tk.Frame(root, bg=config.BG)
    logframe.pack(side="bottom", fill="x", pady=6)
    logbox = scrolledtext.ScrolledText(
        logframe, height=4, bg="#071116", fg="#bff5c9", font=("Consolas", 9)
    )
    logbox.pack(fill="x", padx=8, pady=4)

    _app_closing = [False]   # Flag für sauberes Beenden

    def log(msg):
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Immer in Konsole
        print(f"[{ts}] {msg}")
        # Best-effort GUI
        try:
            if _app_closing[0]:
                return
            if not root or not root.winfo_exists():
                return
            logbox.insert("end", f"[{ts}] {msg}\n")
            logbox.see("end")
        except Exception:
            pass

    # ---------- BUTTON FUNKTIONEN ----------
    def reset_charts():
        for buf in data_buffers.values():
            buf.clear()
        time_buffer.clear()
        log("Charts reset")

    def delete_config():
        from tkinter import messagebox
        if os.path.exists(config.CONFIG_FILE):
            if messagebox.askyesno("Confirm", "Delete config.json?"):
                try:
                    os.remove(config.CONFIG_FILE)
                    log("config.json deleted ✅")
                except Exception as e:
                    log(f"❌ Error deleting config.json: {e}")
        else:
            log("⚠️ config.json not found")




    def export_chart():
        try:
            # --- Zielordner vom Benutzer auswählen ---
            export_dir = filedialog.askdirectory(
                title="Exportziel wählen",
                mustexist=True,
            )
            if not export_dir:
                log("❌ Export abgebrochen – kein Ordner gewählt")
                return

            # --- Dateiname im GrowHub/Vivosun-Format ---
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            filename = f"chart_export_{timestamp}.csv"
            path = os.path.join(export_dir, filename)

            import csv
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp(30 mins)",
                    "Inside Temperature(℃)",
                    "Inside Humidity(%)",
                    "Inside VPD(kPa)",
                    "Outside Temperature(℃)",
                    "Outside Humidity(%)",
                    "Outside VPD(kPa)",
                ])

                for i in range(len(time_buffer)):
                    ts = time_buffer[i].strftime("%Y-%m-%d %H:%M:%S") if i < len(time_buffer) else ""
                    row = [
                        ts,
                        data_buffers["t_main"][i] if i < len(data_buffers["t_main"]) else "",
                        data_buffers["h_main"][i] if i < len(data_buffers["h_main"]) else "",
                        data_buffers["vpd_int"][i] if i < len(data_buffers["vpd_int"]) else "",
                        data_buffers["t_ext"][i] if i < len(data_buffers["t_ext"]) else "",
                        data_buffers["h_ext"][i] if i < len(data_buffers["h_ext"]) else "",
                        data_buffers["vpd_ext"][i] if i < len(data_buffers["vpd_ext"]) else "",
                    ]
                    writer.writerow(row)

            log(f"💾 CSV exportiert → {path}")
            log("📈 Format: GrowHub-kompatibel, direkt im CSV-Viewer ladbar")

        except Exception as e:
            log(f"❌ CSV-Export fehlgeschlagen: {e}")



    def restart_program():
        import sys as _sys
        log("🔄 Restarting program...")
        python = _sys.executable
        os.execl(python, python, *_sys.argv)

    open_windows = {}

    def open_scattered_vpd():
        try:
            if "scatter" in open_windows and open_windows["scatter"].winfo_exists():
                open_windows["scatter"].lift()
                return
            import scattered_vpd_chart
            win = scattered_vpd_chart.open_window(root, config, utils)
            open_windows["scatter"] = win
            win.protocol("WM_DELETE_WINDOW", lambda: (open_windows.pop("scatter", None), win.destroy()))
        except Exception as e:
            log(f"⚠️ Could not open scattered VPD chart: {e}")

    def open_growhub_csv():
        try:
            if "csv" in open_windows and open_windows["csv"].winfo_exists():
                open_windows["csv"].lift()
                return
            import growhub_csv_viewer
            win = growhub_csv_viewer.open_window(root, config=config)
            open_windows["csv"] = win
            win.protocol("WM_DELETE_WINDOW", lambda: (open_windows.pop("csv", None), win.destroy()))
        except Exception as e:
            log(f"⚠️ Fehler im GrowHub CSV Viewer: {e}")

    # ---------- BUTTONS ----------
    tk.Button(row1, text="Reset Charts", command=reset_charts).pack(side="left", padx=6)
    tk.Button(row1, text="🗑 Delete Config", command=delete_config).pack(side="left", padx=6)
    tk.Button(row1, text="💾 Export Chart", command=export_chart).pack(side="left", padx=6)

    tk.Button(row2, text="📈 VPD Scatter", command=open_scattered_vpd).pack(side="left", padx=6)
    tk.Button(row2, text="📊 GrowHub CSV", command=open_growhub_csv).pack(side="left", padx=6)
    tk.Button(row2, text="🔄 Restart Program", command=restart_program).pack(side="left", padx=6)

    # ---------- FOOTER via Widget ----------
    set_status, mark_data_update = create_footer(root, config)

    try:
        set_status(False)  # Initialzustand
    except Exception:
        pass

    # ---------- DATA BUFFERS ----------
    keys = ["t_main", "h_main", "vpd_int", "t_ext", "h_ext", "vpd_ext"]
    data_buffers = {k: deque(maxlen=config.PLOT_BUFFER_LEN) for k in keys}
    time_buffer = deque(maxlen=config.PLOT_BUFFER_LEN)

    # ---------- CHARTS ----------
    fig, axs = plt.subplots(2, 3, figsize=(16, 10), facecolor=config.BG)
    fig.subplots_adjust(hspace=0.6, wspace=0.4, top=0.94, bottom=0.10)
    fig.tight_layout(pad=3.0)

    temp_unit = "°C" if unit_celsius.get() else "°F"

    chart_order_full = [
        ("t_main",  axs[0, 0], "Internal Temp",      "tomato",      temp_unit),
        ("h_main",  axs[0, 1], "Internal Humidity",  "deepskyblue", "%"),
        ("vpd_int", axs[0, 2], "Internal VPD",       "lime",        "kPa"),
        ("t_ext",   axs[1, 0], "External Temp",      "violet",      temp_unit),
        ("h_ext",   axs[1, 1], "External Humidity",  "cyan",        "%"),
        ("vpd_ext", axs[1, 2], "External VPD",       "gold",        "kPa"),
    ]

    chart_order_compact = [
        ("t_main",  axs[0, 0], "Internal Temp",      "tomato",      temp_unit),
        ("h_main",  axs[0, 1], "Internal Humidity",  "deepskyblue", "%"),
        ("vpd_int", axs[0, 2], "Internal VPD",       "lime",        "kPa"),
    ]

    # Zustand: kompakt / voll
    compact_mode = tk.BooleanVar(value=False)

    # Matplotlib Canvas ins Tk-Fenster (vor Setup, damit canvas verfügbar ist)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=12, pady=8)
    NavigationToolbar2Tk(canvas, root).update()

    lines = {}
    ax_map = {}
    value_labels = {}

    def setup_charts(chart_order):
        """Initialisiert Titles, Achsen und Linien für die übergebene Anordnung."""
        try:
            lines.clear()
            ax_map.clear()
            value_labels.clear()

            for ax in axs.flat:
                ax.clear()
                ax.set_visible(False)

            for key, ax, title, color, ylabel in chart_order:
                ax.set_visible(True)
                ax.set_title(
                    title,
                    color=color,
                    fontsize=14,
                    pad=10,
                    weight="bold",
                    loc="left"
                )
                ax.set_ylabel(ylabel, color=config.TEXT, fontsize=11, weight="bold")
                ax.tick_params(axis="y", labelcolor=config.TEXT, labelsize=9)
                ax.set_facecolor("#121a24")
                ax.grid(True, linestyle="--", alpha=0.25, color="gray")

                line, = ax.plot([], [], color=color, linewidth=2.5, alpha=0.95, zorder=1)
                lines[key] = line
                ax_map[ax] = (key, title, color, ylabel)

                val_text = ax.text(
                    0.02, 0.98, "--",
                    transform=ax.transAxes,
                    color=color,
                    fontsize=40,
                    weight="bold",
                    va="top", ha="left",
                    path_effects=[path_effects.withStroke(linewidth=5, foreground="black")],
                    zorder=5
                )
                value_labels[key] = val_text

                locator = mdates.MinuteLocator(interval=15)
                formatter = mdates.DateFormatter("%H:%M")
                ax.xaxis.set_major_locator(locator)
                ax.xaxis.set_major_formatter(formatter)
                ax.tick_params(axis="x", labelcolor=config.TEXT, rotation=0, labelsize=9)

            fig.autofmt_xdate()
            canvas.draw_idle()
        except TclError:
            return

    # Erstmal Full-Layout
    setup_charts(chart_order_full)

    # ---------- Umschalt-Button ----------
    def toggle_charts():
        try:
            compact_mode.set(not compact_mode.get())
            if compact_mode.get():
                setup_charts(chart_order_compact)
                log("Switched to Compact Chart View (Internal only)")
            else:
                setup_charts(chart_order_full)
                log("Switched to Full Chart View (Internal + External)")
        except TclError:
            pass

    toggle_btn = tk.Button(
        root,
        text="🧭 Toggle Charts (3↔6)",
        command=toggle_charts,
        bg="lime",
        fg="black",
        font=("Segoe UI", 10, "bold")
    )
    toggle_btn.pack(side="bottom", pady=6)

    # ---------- Klick auf Chart öffnet Enlarged Window ----------
    def on_click(event):
        if event.inaxes in ax_map and event.button == 1:
            key, title_txt, color, ylabel = ax_map[event.inaxes]
            try:
                import enlarged_charts
                enlarged_charts.open_window(
                    parent=root,
                    config=config,
                    utils=utils,
                    key=key,
                    title=title_txt,
                    color=color,
                    ylabel=ylabel,
                    data_buffers=data_buffers,
                    time_buffer=time_buffer,
                    unit_celsius=unit_celsius
                )
            except Exception as e:
                log(f"⚠️ Fehler beim Öffnen von enlarged_charts: {e}")

    def on_motion(event):
        try:
            if event.inaxes in ax_map:
                fig.canvas.set_cursor(cursors.HAND)
            else:
                fig.canvas.set_cursor(cursors.POINTER)
        except Exception:
            pass

    _mpl_cids = []
    _mpl_cids.append(fig.canvas.mpl_connect("button_press_event", on_click))
    _mpl_cids.append(fig.canvas.mpl_connect("motion_notify_event", on_motion))

    # ---------- UPDATE LOOP (Snapshot lesen, Status setzen, Buffers füllen) ----------
    last_update_time = [None]
    _missing_external_count = [0]
    _missing_threshold = 5  # ~5 Zyklen

    def update_data():
        d = utils.safe_read_json(config.DATA_FILE)
        now = datetime.datetime.now()
        time_buffer.append(now)

        # --- 🟢 Footer-Update: Frische markieren ---
        try:
            mark_data_update()   # signalisiert dem Footer: neue Messung da
        except Exception:
            pass

        # --- Helper zum Bereinigen ---
        def sanitize(val):
            if val is None:
                return None
            try:
                v = float(val)
                if -0.2 <= v <= 0.2:
                    return None
                return v
            except Exception:
                return None

        t_main = h_main = t_ext = h_ext = vpd_int = vpd_ext = None

        if d:
            raw_t_main = sanitize(d.get("t_main"))
            raw_t_ext  = sanitize(d.get("t_ext"))
            h_main     = sanitize(d.get("h_main"))
            h_ext      = sanitize(d.get("h_ext"))

            leaf_off = config.leaf_offset_c[0]
            hum_off  = config.humidity_offset[0]

            if raw_t_main is not None and h_main is not None:
                vpd_int = utils.calc_vpd(raw_t_main + leaf_off, h_main + hum_off)
            if raw_t_ext is not None and h_ext is not None:
                vpd_ext = utils.calc_vpd(raw_t_ext + leaf_off, h_ext + hum_off)

            t_main = raw_t_main
            t_ext  = raw_t_ext

            if any(v is not None for v in [t_main, t_ext, h_main, h_ext]):
                last_update_time[0] = now

        
        
        # --- Auto-Compact je nach externen Daten ---
        external_missing_now = (t_ext is None) and (h_ext is None)
        if external_missing_now:
            _missing_external_count[0] += 1
        else:
            _missing_external_count[0] = 0

        try:
            if _missing_external_count[0] >= _missing_threshold and not compact_mode.get():
                compact_mode.set(True)
                setup_charts(chart_order_compact)
                log("Auto-switch → Compact (external missing)")

            if _missing_external_count[0] == 0 and compact_mode.get() and (t_ext is not None or h_ext is not None):
                compact_mode.set(False)
                setup_charts(chart_order_full)
                log("Auto-switch → Full (external back)")
        except TclError:
            return

        # --- Buffer füllen ---
        data_buffers["t_main"].append(t_main)
        data_buffers["h_main"].append(h_main)
        data_buffers["vpd_int"].append(vpd_int)
        data_buffers["t_ext"].append(t_ext)
        data_buffers["h_ext"].append(h_ext)
        data_buffers["vpd_ext"].append(vpd_ext)

    # ---------- ANIMATION (bei jedem Frame die Plots & Value-Labels aktualisieren) ----------
    def animate(_):
        if not time_buffer:
            return

        x = mdates.date2num(list(time_buffer))
        unit = "°C" if unit_celsius.get() else "°F"
        current_chart_order = chart_order_compact if compact_mode.get() else chart_order_full

        for key, ax, _, _, _ in current_chart_order:
            # Falls bei Layoutwechsel noch keine Line existiert:
            if key not in lines:
                continue

            vals = list(data_buffers[key])
            if not vals:
                lines[key].set_data([], [])
                if key in value_labels:
                    value_labels[key].set_text("--")
                continue

            if key in ("t_main", "t_ext"):
                y = [
                    (v if v is None else (v if unit_celsius.get() else utils.c_to_f(v)))
                    for v in vals
                ]
            else:
                y = [v if v is not None else float("nan") for v in vals]

            lines[key].set_data(x, y)

            # X-Limits
            if len(x) == 1:
                ax.set_xlim(x[0] - 1 / 1440, x[0] + 1 / 1440)  # ±1 Minute
            else:
                ax.set_xlim(x[0], x[-1])

            # Y-Limits dynamisch
            y_clean = [v for v in y if isinstance(v, (int, float)) and not (v != v)]
            if y_clean:
                lo, hi = min(y_clean), max(y_clean)
                if lo == hi:
                    lo -= 0.5
                    hi += 0.5
                margin = (hi - lo) * 0.15
                ax.set_ylim(lo - margin, hi + margin)

            # Wert groß anzeigen
            latest = None
            for vv in reversed(y):
                if vv is not None and not (isinstance(vv, float) and vv != vv):
                    latest = vv
                    break

            if key in value_labels:
                if latest is None:
                    value_labels[key].set_text("--")
                else:
                    if key in ("t_main", "t_ext"):
                        label_text = f"{latest:.1f} {unit}"
                    elif key.startswith("h_"):
                        label_text = f"{latest:.1f} %"
                    else:
                        label_text = f"{latest:.2f} kPa"
                    value_labels[key].set_text(label_text)

        fig.autofmt_xdate()
        try:
            canvas.draw_idle()
        except Exception:
            pass

    # --- Animation starten (nach der Definition von animate!) ---
    root.ani = FuncAnimation(
        fig, animate,
        interval=int(config.UI_POLL_INTERVAL * 1000),
        blit=False,
        cache_frame_data=False
    )

# --- Reader starten (einmalig) ---
    import signal
    from async_reader import start_reader_thread, stop_reader

    if not device_id:
        cfg_local = utils.safe_read_json(config.CONFIG_FILE) or {}
        device_id = cfg_local.get("device_id", "SIM_DEVICE")

    # Startet den Async-Reader (deine originale Version mit Reconnect & Logging)
    start_reader_thread(device_id, log)

    # --- Icon final noch einmal setzen (falls Toolbar es überschrieben hat) ---
    try:
        icon_loader.set_app_icon(root)
    except Exception:
        pass

    # ---------- SAUBERES BEENDEN ----------
    _scheduled_tasks = []

    def schedule_safe(func, delay_ms):
        try:
            if not root.winfo_exists():
                return
            task_id = root.after(delay_ms, func)
            _scheduled_tasks.append(task_id)
            return task_id
        except TclError:
            return

    def safe_update_data():
        if _app_closing[0]:
            return
        try:
            if not root.winfo_exists():
                return
        except TclError:
            return
        update_data()
        schedule_safe(safe_update_data, int(config.UI_POLL_INTERVAL * 1000))

    def safe_refresh_offset_fields():
        if _app_closing[0]:
            return
        try:
            if not root.winfo_exists():
                return
        except TclError:
            return
        refresh_offset_fields_once()
        schedule_safe(safe_refresh_offset_fields, 2000)

    def clean_exit():
        _app_closing[0] = True
        log("🧹 Programm wird beendet ...")

        try:
            if hasattr(root, "ani") and root.ani and getattr(root.ani, "event_source", None):
                root.ani.event_source.stop()
        except Exception:
            pass

        try:
            for cid in list(_mpl_cids):
                try:
                    fig.canvas.mpl_disconnect(cid)
                except Exception:
                    pass
            _mpl_cids.clear()
        except Exception:
            pass

        for task in list(_scheduled_tasks):
            try:
                root.after_cancel(task)
            except Exception:
                pass
        _scheduled_tasks.clear()

        # Reader stoppen
        try:
            stop_reader()
        except Exception as e:
            log(f"Fehler beim Stoppen des Readers: {e}")

        try:
            root.destroy()
        except Exception:
            pass

        sys.exit(0)

    def on_close():
        clean_exit()

    root.protocol("WM_DELETE_WINDOW", on_close)
    signal.signal(signal.SIGINT, lambda sig, frame: clean_exit())

    refresh_offset_fields_once()
    safe_update_data()
    safe_refresh_offset_fields()
    root.mainloop()

