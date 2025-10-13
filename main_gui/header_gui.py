#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
header_gui.py – Theme-Enabled Header mit stabilem Offset-Sync (Celsius/Fahrenheit)
"""

import tkinter as tk
import config
import utils
import os, sys
from PIL import Image, ImageTk

THEME = config.THEME  # 🌈 Aktives Theme laden

# --- Pfad-Fix ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

leaf_offset_var = None
hum_offset_var = None


# ===============================================================
#   🔧 Offset-Synchronisation
# ===============================================================
def sync_offsets_to_gui():
    try:
        cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
        use_celsius = cfg.get("unit_celsius", True)

        if isinstance(leaf_offset_var, tk.DoubleVar):
            val_c = float(config.leaf_offset_c[0])
            display_val = val_c if use_celsius else val_c * 9.0 / 5.0
            leaf_offset_var.set(round(display_val, 2))

        if isinstance(hum_offset_var, tk.DoubleVar):
            hum_offset_var.set(float(config.humidity_offset[0]))
    except Exception as e:
        print(f"⚠️ sync_offsets_to_gui Fehler: {e}")


def set_offsets_from_outside(leaf=None, hum=None, persist=True):
    try:
        cfg = utils.safe_read_json(config.CONFIG_FILE) or {}

        if leaf is not None:
            config.leaf_offset_c[0] = float(leaf)
        if hum is not None:
            config.humidity_offset[0] = float(hum)

        if persist:
            cfg["leaf_offset"] = config.leaf_offset_c[0]
            cfg["humidity_offset"] = config.humidity_offset[0]
            utils.safe_write_json(config.CONFIG_FILE, cfg)

        sync_offsets_to_gui()
    except Exception as e:
        print(f"⚠️ set_offsets_from_outside Fehler: {e}")


def update_leaf_offset(*_):
    try:
        cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
        use_celsius = cfg.get("unit_celsius", True)
        val_display = float(leaf_offset_var.get())
        val_c = val_display if use_celsius else val_display * 5.0 / 9.0
        set_offsets_from_outside(leaf=val_c, hum=None, persist=True)
    except Exception as e:
        print(f"⚠️ update_leaf_offset Fehler: {e}")


# ===============================================================
#   🧩 GUI-Header
# ===============================================================
def build_header(root, config, data_buffers, time_buffer, log=lambda *a, **k: None):
    header = tk.Frame(root, bg=THEME.CARD_BG)

    # ---------- LOGO + TITEL ----------
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(base_dir, "assets", "Logo.png")

    left_frame = tk.Frame(header, bg=THEME.CARD_BG)
    left_frame.pack(side="left", padx=10, pady=6)

    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path).resize((120, 100), Image.LANCZOS)
            logo_img = ImageTk.PhotoImage(img)
            logo_label = tk.Label(left_frame, image=logo_img, bg=THEME.CARD_BG)
            logo_label.image = logo_img
            logo_label.pack(side="left", padx=(0, 10))
        except Exception as e:
            print(f"⚠️ Logo konnte nicht geladen werden: {e}")

    title = tk.Label(
        left_frame,
        text="🌱 VIVOSUN Thermo Dashboard\n     for THB-1S",
        bg=THEME.CARD_BG,
        fg=THEME.TEXT,
        font=THEME.FONT_TITLE,
        anchor="w",
        justify="left"
    )
    title.pack(side="left", anchor="center")

    # ---------- OFFSET-STEUERUNG ----------
    controls = tk.Frame(header, bg=THEME.CARD_BG)
    controls.pack(side="right", pady=6)

    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    unit_celsius = tk.BooleanVar(value=cfg.get("unit_celsius", True))

    tk.Label(
        controls,
        text=f"Leaf Temp Offset ({'°C' if unit_celsius.get() else '°F'}):",
        bg=THEME.CARD_BG,
        fg=THEME.TEXT
    ).pack(side="left", padx=6)

    global leaf_offset_var, hum_offset_var
    leaf_offset_var = tk.DoubleVar(value=float(config.leaf_offset_c[0]))
    leaf_offset_var.trace_add("write", update_leaf_offset)

    tk.Spinbox(
        controls,
        textvariable=leaf_offset_var,
        from_=-10.0, to=10.0, increment=0.1,
        width=6,
        bg=THEME.CARD_BG,
        fg=THEME.TEXT,
        justify="center",
        highlightbackground=THEME.BORDER,
        highlightthickness=1
    ).pack(side="left")

    tk.Label(
        controls,
        text="Humidity Offset (%):",
        bg=THEME.CARD_BG,
        fg=THEME.TEXT
    ).pack(side="left", padx=6)

    hum_offset_var = tk.DoubleVar(value=float(config.humidity_offset[0]))

    def update_hum_offset(*_):
        try:
            set_offsets_from_outside(leaf=None, hum=float(hum_offset_var.get()), persist=True)
        except Exception:
            set_offsets_from_outside(leaf=None, hum=0.0, persist=True)

    hum_offset_var.trace_add("write", update_hum_offset)

    tk.Spinbox(
        controls,
        textvariable=hum_offset_var,
        from_=-20.0, to=20.0, increment=0.5,
        width=6,
        bg=THEME.CARD_BG,
        fg=THEME.TEXT,
        justify="center",
        highlightbackground=THEME.BORDER,
        highlightthickness=1
    ).pack(side="left")

    # ---------- RESET BUTTON ----------
    def reset_offsets():
        leaf_offset_var.set(0.0)
        hum_offset_var.set(0.0)
        print("Offsets reset (Leaf=0.0°C, Humidity=0.0%)")

    THEME.make_button(
        controls, "↺ Reset Offsets", reset_offsets, color=THEME.ORANGE
    ).pack(side="left", padx=6)

    # ---------- BUTTON ROWS ----------
    button_frame = tk.Frame(header, bg=THEME.CARD_BG)
    button_frame.pack(side="bottom", fill="x", pady=6)

    row1 = tk.Frame(button_frame, bg=THEME.CARD_BG)
    row1.pack(side="top", pady=2)

    row2 = tk.Frame(button_frame, bg=THEME.CARD_BG)
    row2.pack(side="top", pady=2)

    # ---------- BUTTON-FUNKTIONEN ----------
    def reset_charts():
        try:
            import main_gui.charts_gui as charts_gui
            if hasattr(charts_gui, "data_buffers"):
                for key, buf in charts_gui.data_buffers.items():
                    if isinstance(buf, list):
                        buf.clear()
                if "timestamps" in charts_gui.data_buffers:
                    charts_gui.data_buffers["timestamps"].clear()
                print("✅ Charts erfolgreich zurückgesetzt.")
            else:
                print("⚠️ Keine Datenpuffer in charts_gui gefunden.")
        except Exception as e:
            print(f"⚠️ Fehler beim Chart-Reset: {e}")

    def export_chart():
        from tkinter import filedialog
        import csv, datetime
        try:
            export_dir = filedialog.askdirectory(title="Exportziel wählen", mustexist=True)
            if not export_dir:
                print("❌ Export abgebrochen – kein Ordner gewählt")
                return

            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            filename = f"chart_export_{timestamp}.csv"
            path = os.path.join(export_dir, filename)

            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "T_in", "H_in", "VPD_in", "T_out", "H_out", "VPD_out"])
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
            print(f"💾 CSV exportiert → {path}")
        except Exception as e:
            print(f"❌ CSV-Export fehlgeschlagen: {e}")

    def open_settings():
        try:
            import main_gui.settings_gui as settings_gui
            settings_gui.open_settings_window(root, log)
        except Exception as e:
            print(f"⚠️ Fehler beim Öffnen der Settings: {e}")

    open_windows = {}

    def open_scattered_vpd():
        try:
            if "scatter" in open_windows and open_windows["scatter"].winfo_exists():
                open_windows["scatter"].lift()
                return
            import importlib.util
            module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "widgets", "scattered_vpd_chart.py"))
            if not os.path.exists(module_path):
                print(f"❌ scattered_vpd_chart.py nicht gefunden unter: {module_path}")
                return
            spec = importlib.util.spec_from_file_location("scattered_vpd_chart", module_path)
            scattered_vpd_chart = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(scattered_vpd_chart)
            win = scattered_vpd_chart.open_window(root, config, utils)
            open_windows["scatter"] = win
            win.protocol("WM_DELETE_WINDOW", lambda: (open_windows.pop("scatter", None), win.destroy()))
            print("✅ scattered_vpd_chart erfolgreich geöffnet")
        except Exception as e:
            print(f"⚠️ Could not open scattered VPD chart: {e}")

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
            print(f"⚠️ Fehler im GrowHub CSV Viewer: {e}")

    # ---------- BUTTONS ----------
    THEME.make_button(row1, "🧹 Reset Charts", reset_charts, color=THEME.ORANGE).pack(side="left", padx=6)
    THEME.make_button(row1, "💾 Export Chart", export_chart, color=THEME.LIME).pack(side="left", padx=6)
    THEME.make_button(row1, "⚙️ Settings", open_settings, color=THEME.AQUA).pack(side="left", padx=6)
    THEME.make_button(row2, "📈 VPD Scatter", open_scattered_vpd, color=THEME.LIME_DARK).pack(side="left", padx=6)
    THEME.make_button(row2, "📊 GrowHub CSV", open_growhub_csv, color=THEME.FOREST).pack(side="left", padx=6)

    sync_offsets_to_gui()
    return header
