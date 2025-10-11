#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
header_gui.py – VIVOSUN Full-Green Theme 🌿
mit korrekter °C / °F-Steuerung & Offset-Sync
"""

import tkinter as tk
import config, utils
from PIL import Image, ImageTk
import os

# ---------------------------------------------------------
# Farben & Fonts
# ---------------------------------------------------------
BG_MAIN   = "#06110f"
CARD_BG   = "#0d231d"
LIME      = "#a8ff60"
LIME_DARK = "#66cc33"
ORANGE    = "#ffaa00"
TEXT      = "#e5ffe5"
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_BTN   = ("Segoe UI", 10, "bold")
FONT_LABEL = ("Segoe UI", 10, "bold")

leaf_offset_var = None
hum_offset_var  = None


# ---------------------------------------------------------
# Helper
# ---------------------------------------------------------
def styled_button(master, text, cmd, color=LIME):
    return tk.Button(
        master, text=text, command=cmd,
        bg=color, fg="black", font=FONT_BTN,
        activebackground=LIME_DARK, activeforeground="black",
        relief="flat", padx=12, pady=6, cursor="hand2",
        highlightbackground=LIME_DARK, highlightthickness=2
    )


def add_stepper_field(parent, label, var, step, unit=""):
    frame = tk.Frame(parent, bg=CARD_BG, padx=6, pady=4)
    tk.Label(frame, text=label, bg=CARD_BG, fg=LIME, font=FONT_LABEL).grid(row=0, column=0, rowspan=2, sticky="w")

    entry = tk.Entry(
        frame, textvariable=var, width=6, justify="center",
        bg="#072017", fg=TEXT, insertbackground=TEXT,
        relief="flat", highlightthickness=2, highlightcolor=LIME
    )
    entry.grid(row=0, column=1, rowspan=2, padx=(10, 6))

    def step_val(delta):
        try:
            v = float(var.get()) + delta
        except Exception:
            v = 0.0
        var.set(round(v, 2))

    tk.Button(frame, text="▲", bg=LIME, fg="black",
              font=("Segoe UI", 11, "bold"), width=3,
              relief="flat", command=lambda: step_val(+step)).grid(row=0, column=2)
    tk.Button(frame, text="▼", bg=LIME, fg="black",
              font=("Segoe UI", 11, "bold"), width=3,
              relief="flat", command=lambda: step_val(-step)).grid(row=1, column=2)

    if unit:
        tk.Label(frame, text=unit, bg=CARD_BG, fg="#99ff99", font=("Segoe UI", 9, "bold")
        ).grid(row=0, column=3, rowspan=2, padx=(6, 0))
    return frame


# ---------------------------------------------------------
# Offset-Sync
# ---------------------------------------------------------
def sync_offsets_to_gui(unit_celsius: bool):
    """GUI zeigt Werte in der aktuellen Einheit"""
    try:
        if isinstance(leaf_offset_var, tk.DoubleVar):
            val_c = float(config.leaf_offset_c[0])
            leaf_offset_var.set(val_c if unit_celsius else val_c * 9.0 / 5.0)
        if isinstance(hum_offset_var, tk.DoubleVar):
            hum_offset_var.set(float(config.humidity_offset[0]))
    except Exception:
        pass


def set_offsets_from_outside(leaf=None, hum=None, persist=True):
    """Speichert neue Offsets (immer in °C)"""
    try:
        if leaf is not None:
            config.leaf_offset_c[0] = float(leaf)
        if hum is not None:
            config.humidity_offset[0] = float(hum)
        if persist:
            cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
            cfg["leaf_offset"] = config.leaf_offset_c[0]
            cfg["humidity_offset"] = config.humidity_offset[0]
            utils.safe_write_json(config.CONFIG_FILE, cfg)
    except Exception:
        pass


# ---------------------------------------------------------
# Hauptaufbau
# ---------------------------------------------------------
def build_header(root, config, data_buffers, time_buffer, log=lambda *a, **k: None):
    header = tk.Frame(root, bg=CARD_BG)
    header.pack(side="top", fill="x", padx=12, pady=8)

    # ---------- Logo + Titel ----------
    left = tk.Frame(header, bg=CARD_BG)
    left.pack(side="left", padx=6, pady=4)

    logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "Logo.png")
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path).resize((120, 100))
            logo_img = ImageTk.PhotoImage(img)
            lbl = tk.Label(left, image=logo_img, bg=CARD_BG)
            lbl.image = logo_img
            lbl.pack(side="left", padx=(0, 10))
        except Exception as e:
            print(f"⚠️ Logo konnte nicht geladen werden: {e}")

    tk.Label(left, text="🌱 VIVOSUN Thermo Dashboard\n     for THB-1S",
             bg=CARD_BG, fg=LIME, font=FONT_TITLE, anchor="w", justify="left").pack(side="left")

    # ---------- Offsets ----------
    right = tk.Frame(header, bg=CARD_BG)
    right.pack(side="right", pady=2)

    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    unit_celsius = config.unit_celsius

    global leaf_offset_var, hum_offset_var
    leaf_offset_var = tk.DoubleVar()
    hum_offset_var  = tk.DoubleVar()

    # Startwerte anzeigen
    sync_offsets_to_gui(unit_celsius)

    def update_leaf_offset(*_):
        try:
            val = float(leaf_offset_var.get())
            c_val = val if unit_celsius else val * 5.0 / 9.0
            set_offsets_from_outside(leaf=c_val)
        except Exception:
            pass

    def update_hum_offset(*_):
        try:
            set_offsets_from_outside(hum=float(hum_offset_var.get()))
        except Exception:
            pass

    leaf_offset_var.trace_add("write", update_leaf_offset)
    hum_offset_var.trace_add("write", update_hum_offset)

    add_stepper_field(right, f"Leaf Offset ({'°C' if unit_celsius else '°F'})",
                      leaf_offset_var, 0.1, "°").pack(side="left", padx=6)
    add_stepper_field(right, "Humidity Offset (%)", hum_offset_var, 0.5, "%").pack(side="left", padx=6)

    styled_button(right, "↺ Reset Offsets",
                  lambda: (leaf_offset_var.set(0.0), hum_offset_var.set(0.0)), ORANGE).pack(side="left", padx=8)

    # ---------- Buttons ----------
    btn_row = tk.Frame(header, bg=CARD_BG)
    btn_row.pack(side="bottom", fill="x", pady=4)

    def reset_charts():
        for buf in data_buffers.values():
            buf.clear()
        time_buffer.clear()
        log("📉 Charts reset")

    def delete_config():
        from tkinter import messagebox
        if os.path.exists(config.CONFIG_FILE) and messagebox.askyesno("Confirm", "Delete config.json?"):
            os.remove(config.CONFIG_FILE)
            log("🗑 config.json deleted ✅")

    def export_chart():
        from tkinter import filedialog
        import csv, datetime
        try:
            export_dir = filedialog.askdirectory(title="Exportziel wählen", mustexist=True)
            if not export_dir:
                return
            ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            path = os.path.join(export_dir, f"chart_export_{ts}.csv")
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f)
                w.writerow(["Timestamp", "t_main", "h_main", "vpd_int", "t_ext", "h_ext", "vpd_ext"])
                for i in range(len(time_buffer)):
                    ts_str = time_buffer[i].strftime("%Y-%m-%d %H:%M:%S")
                    w.writerow([ts_str] + [data_buffers[k][i] if i < len(data_buffers[k]) else "" for k in
                                           ["t_main", "h_main", "vpd_int", "t_ext", "h_ext", "vpd_ext"]])
            log(f"💾 CSV exportiert → {path}")
        except Exception as e:
            log(f"❌ CSV-Export-Fehler: {e}")

    def restart_program():
        import sys
        log("🔄 Restarting program…")
        os.execl(sys.executable, sys.executable, *sys.argv)

# ---------- EXTERNE FENSTER ----------
    open_windows = {}

    def open_scattered_vpd():
        """Öffnet das Scatter-Chart-Fenster (widgets/scattered_vpd_chart.py)."""
        try:
            if "scatter" in open_windows and open_windows["scatter"].winfo_exists():
                open_windows["scatter"].lift()
                return
            from widgets import scattered_vpd_chart
            win = scattered_vpd_chart.open_window(root, config, utils)
            open_windows["scatter"] = win
            win.protocol("WM_DELETE_WINDOW", lambda: (open_windows.pop("scatter", None), win.destroy()))
            log("📈 Scatter-Fenster geöffnet")
        except Exception as e:
            log(f"⚠️ Fehler beim Öffnen des Scatter-Fensters: {e}")

    def open_growhub_csv():
        """Öffnet den GrowHub-CSV-Viewer (widgets/growhub_csv_viewer.py)."""
        try:
            if "csv" in open_windows and open_windows["csv"].winfo_exists():
                open_windows["csv"].lift()
                return
            from widgets import growhub_csv_viewer
            win = growhub_csv_viewer.open_window(root, config=config)
            open_windows["csv"] = win
            win.protocol("WM_DELETE_WINDOW", lambda: (open_windows.pop("csv", None), win.destroy()))
            log("📊 GrowHub-Fenster geöffnet")
        except Exception as e:
            log(f"⚠️ Fehler beim Öffnen des GrowHub-Fensters: {e}")


            
    # ---------- Button-Reihen ----------
    row1 = tk.Frame(btn_row, bg=CARD_BG)
    row1.pack(side="top", pady=2)
    row2 = tk.Frame(btn_row, bg=CARD_BG)
    row2.pack(side="top", pady=2)

    styled_button(row1, "📉 Reset Charts", reset_charts).pack(side="left", padx=6)
    styled_button(row1, "🗑 Delete Config", delete_config, ORANGE).pack(side="left", padx=6)
    styled_button(row1, "💾 Export Chart", export_chart).pack(side="left", padx=6)

    styled_button(row2, "📈 VPD Scatter", open_scattered_vpd).pack(side="left", padx=6)
    styled_button(row2, "📊 GrowHub CSV", open_growhub_csv).pack(side="left", padx=6)
    styled_button(row2, "🔄 Restart Program", restart_program, ORANGE).pack(side="left", padx=6)

    return header
