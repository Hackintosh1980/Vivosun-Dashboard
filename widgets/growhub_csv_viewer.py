#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
growhub_csv_viewer.py – GUI-angepasste Version
Fenster zum Anzeigen von GrowHub-CSV-Daten im gleichen Style wie das Dashboard
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import os
from PIL import Image, ImageTk
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from widgets.footer_widget import create_footer_light

# ---------- Globale Helper ----------
def _find_time_col(cols):
    candidates = []
    for c in cols:
        lc = str(c).lower().strip()
        if ("timestamp" in lc) or ("time" in lc) or ("date" in lc):
            prio = 0 if "timestamp" in lc else 1
            candidates.append((prio, len(lc), c))
    if not candidates:
        return None
    candidates.sort()
    return candidates[0][2]


def _parse_ts_series(s):
    s = s.astype(str).str.strip()
    out = pd.to_datetime(s, errors="coerce", infer_datetime_format=True)
    if out.notna().any():
        return out
    fmts = [
        "%Y/%m/%d %H:%M:%S", "%Y/%m/%d %H:%M",
        "%d/%m/%Y %H:%M:%S", "%d/%m/%Y %H:%M",
        "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M",
        "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %H:%M",
    ]
    best = None
    best_count = -1
    for fmt in fmts:
        parsed = pd.to_datetime(s, format=fmt, errors="coerce")
        count = parsed.notna().sum()
        if count > best_count:
            best = parsed
            best_count = count
    if best is not None and best_count > 0:
        return best
    return pd.to_datetime(s, errors="coerce", dayfirst=True)


# ---------- Main Window ----------
_current_csv_window = None


def open_window(parent, config=None):
    global _current_csv_window
    if _current_csv_window is not None and _current_csv_window.winfo_exists():
        _current_csv_window.lift()
        return _current_csv_window

    win = tk.Toplevel(parent)
    _current_csv_window = win
    win.title("🌱 GrowHub CSV Viewer")
    win.geometry("1400x900")
    bg_color = getattr(config, "BG", "#0f161f")
    card_color = getattr(config, "CARD", "#1e2a38")
    text_color = getattr(config, "TEXT", "white")
    win.configure(bg=bg_color)

    def on_close():
        global _current_csv_window
        _current_csv_window = None
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", on_close)

    # ---------- Header ----------
    header = tk.Frame(win, bg=card_color)
    header.pack(side="top", fill="x", padx=10, pady=6)

    left_frame = tk.Frame(header, bg=card_color)
    left_frame.pack(side="left", padx=6)

    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    logo_path = os.path.join(assets_dir, "Logo.png")
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path).resize((100, 100), Image.LANCZOS)
            logo_img = ImageTk.PhotoImage(img)
            logo_label = tk.Label(left_frame, image=logo_img, bg=card_color)
            logo_label.image = logo_img
            logo_label.pack(side="left", padx=(0, 10))
        except Exception as e:
            print(f"⚠️ Logo konnte nicht geladen werden: {e}")

    title = tk.Label(
        left_frame,
        text="🌱 GrowHub CSV Viewer",
        bg=card_color,
        fg=text_color,
        font=("Segoe UI", 18, "bold"),
        anchor="w"
    )
    title.pack(side="left", anchor="center")

    # ---------- Controls ----------
    controls = tk.Frame(header, bg=card_color)
    controls.pack(side="right", pady=2)

    btn_load = tk.Button(
        controls,
        text="📂 CSV laden",
        command=lambda: load_csv(),
        bg="lime", fg="black", font=("Segoe UI", 13, "bold")
    )
    btn_load.pack(side="left", padx=6)

    btn_reset = tk.Button(
        controls,
        text="🔄 Reset Ansicht",
        command=lambda: reset_view(),
        bg="orange", fg="black", font=("Segoe UI", 13, "bold")
    )
    btn_reset.pack(side="left", padx=6)

    view_var = tk.StringVar(value="both")
    for label, value in [("🌡 Inside", "inside"), ("🌍 Outside", "outside"), ("🔀 Both", "both")]:
        tk.Radiobutton(
            controls,
            text=label,
            variable=view_var,
            value=value,
            indicatoron=False,
            width=12,
            bg=card_color,
            fg=text_color,
            selectcolor="lime",
            font=("Segoe UI", 13, "bold"),
            command=lambda: update_chart()
        ).pack(side="left", padx=4)

    # ---------- Chart ----------
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor("#121a24")
    ax.tick_params(colors=text_color)
    ax.xaxis.label.set_color(text_color)
    ax.yaxis.label.set_color(text_color)
    ax.title.set_color(text_color)
    ax.grid(True, linestyle="--", alpha=0.4)

    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    df = None
    x_full_range = None

    # ---------- CSV Funktionen ----------
    def load_csv():
        nonlocal df, x_full_range
        path = filedialog.askopenfilename(
            title="CSV-Datei auswählen",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if not path:
            return
        try:
            df = pd.read_csv(path)
            df.columns = [str(c).strip().lower() for c in df.columns]

            time_col = _find_time_col(df.columns)
            if not time_col:
                raise ValueError("Keine Zeitspalte gefunden.")
            ts = _parse_ts_series(df[time_col])
            if ts.isna().all():
                raise ValueError("Konnte keine gültigen Zeitstempel parsen.")

            df[time_col] = ts
            df = df.dropna(subset=[time_col]).sort_values(time_col)
            df = df.rename(columns={time_col: "timestamp"})

            for c in df.columns:
                if c != "timestamp":
                    df[c] = pd.to_numeric(df[c], errors="coerce")

            x_full_range = (df["timestamp"].min(), df["timestamp"].max())
            messagebox.showinfo("CSV geladen", f"{len(df)} Zeilen geladen.")
            reset_view()
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte CSV nicht laden:\n{e}")

    def _get_col(subs):
        for col in df.columns:
            if col == "timestamp":
                continue
            name = col.lower()
            if all(s in name for s in subs):
                return col
        return None

    def update_chart():
        nonlocal df
        ax.clear()
        if df is None or df.empty:
            ax.set_title("Keine Daten geladen", color=text_color)
            canvas.draw_idle()
            return

        times = df["timestamp"]
        inside_temp = _get_col(["inside", "temp"])
        inside_hum = _get_col(["inside", "hum"])
        inside_vpd = _get_col(["inside", "vpd"])
        outside_temp = _get_col(["outside", "temp"])
        outside_hum = _get_col(["outside", "hum"])
        outside_vpd = _get_col(["outside", "vpd"])

        mode = view_var.get()
        if mode in ("inside", "both"):
            if inside_temp: ax.plot(times, df[inside_temp], color="tomato", label="Inside Temp (°C)")
            if inside_hum: ax.plot(times, df[inside_hum], color="deepskyblue", label="Inside Humidity (%)")
            if inside_vpd: ax.plot(times, df[inside_vpd], color="lime", label="Inside VPD (kPa)")
        if mode in ("outside", "both"):
            if outside_temp: ax.plot(times, df[outside_temp], color="violet", label="Outside Temp (°C)")
            if outside_hum: ax.plot(times, df[outside_hum], color="cyan", label="Outside Humidity (%)")
            if outside_vpd: ax.plot(times, df[outside_vpd], color="gold", label="Outside VPD (kPa)")

        ax.set_title("GrowHub CSV Data", color=text_color)
        ax.legend(facecolor=bg_color, edgecolor="gray", labelcolor=text_color)
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
        ax.grid(True, linestyle="--", alpha=0.4)
        fig.autofmt_xdate()
        canvas.draw_idle()

    def reset_view():
        nonlocal x_full_range
        if df is not None and not df.empty and x_full_range:
            ax.set_xlim(x_full_range)
        update_chart()

    # ---------- Maussteuerung ----------
    def on_scroll(event):
        if df is None or df.empty:
            return
        cur_xlim = ax.get_xlim()
        if event.xdata is None:
            return
        xdata = event.xdata
        scale = 1.2 if event.button == "up" else 0.8
        new_width = (cur_xlim[1] - cur_xlim[0]) * scale
        left = xdata - new_width / 2
        right = xdata + new_width / 2
        xmin, xmax = mdates.date2num([df["timestamp"].min(), df["timestamp"].max()])
        if left < xmin:
            left = xmin
            right = left + new_width
        if right > xmax:
            right = xmax
            left = right - new_width
        ax.set_xlim([left, right])
        canvas.draw_idle()

    def on_press(event):
        if event.button == 1 and event.xdata is not None:
            ax._pan_start = (event.xdata, ax.get_xlim())

    def on_motion(event):
        if hasattr(ax, "_pan_start") and event.xdata is not None and event.button == 1:
            x_start, (xlim0, xlim1) = ax._pan_start
            dx = x_start - event.xdata
            left, right = xlim0 + dx, xlim1 + dx
            xmin, xmax = mdates.date2num([df["timestamp"].min(), df["timestamp"].max()])
            width = right - left
            if left < xmin:
                left = xmin
                right = xmin + width
            if right > xmax:
                right = xmax
                left = xmax - width
            ax.set_xlim(left, right)
            canvas.draw_idle()

    def on_release(event):
        if hasattr(ax, "_pan_start"):
            del ax._pan_start

    fig.canvas.mpl_connect("scroll_event", on_scroll)
    fig.canvas.mpl_connect("button_press_event", on_press)
    fig.canvas.mpl_connect("motion_notify_event", on_motion)
    fig.canvas.mpl_connect("button_release_event", on_release)

    # ---------- FOOTER ----------
    create_footer_light(win, config)

    update_chart()
    return win
