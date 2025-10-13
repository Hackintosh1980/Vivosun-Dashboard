#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
header_gui.py – Header mit stabilem, bidirektionalem Offset-Sync (Celsius/Fahrenheit-fix)
"""

import tkinter as tk
import config
import utils
import os, sys

# --- Pfad-Fix: stellt sicher, dass "widgets" & "main_gui" immer importierbar sind ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# --- Globale Tk-Variablen für externen Sync ---
leaf_offset_var = None
hum_offset_var = None


# ===============================================================
#   🔧 Offset-Synchronisation (Config ↔ GUI)
# ===============================================================

def sync_offsets_to_gui():
    """Aktualisiert die GUI-Spinboxen anhand der gespeicherten Werte in config."""
    try:
        cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
        use_celsius = cfg.get("unit_celsius", True)

        # Leaf Offset: intern in °C, Anzeige in der gewählten Einheit
        if isinstance(leaf_offset_var, tk.DoubleVar):
            val_c = float(config.leaf_offset_c[0])
            display_val = val_c if use_celsius else val_c * 9.0 / 5.0  # Delta-Umrechnung ohne +32
            leaf_offset_var.set(round(display_val, 2))

        # Humidity Offset bleibt gleich
        if isinstance(hum_offset_var, tk.DoubleVar):
            hum_offset_var.set(float(config.humidity_offset[0]))
    except Exception as e:
        print(f"⚠️ sync_offsets_to_gui Fehler: {e}")


def set_offsets_from_outside(leaf=None, hum=None, persist=True):
    """Setzt Offsets in config (intern immer °C)."""
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
    """Wenn User den Offset im GUI ändert → Umrechnung zurück in °C, dann speichern."""
    try:
        cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
        use_celsius = cfg.get("unit_celsius", True)
        val_display = float(leaf_offset_var.get())
        val_c = val_display if use_celsius else val_display * 5.0 / 9.0  # Delta-Umrechnung
        set_offsets_from_outside(leaf=val_c, hum=None, persist=True)
    except Exception as e:
        print(f"⚠️ update_leaf_offset Fehler: {e}")


# ===============================================================
#   🧩 GUI-Header-Aufbau
# ===============================================================

def build_header(root, config, data_buffers, time_buffer, log=lambda *a, **k: None):
    """Erzeugt den GUI-Header."""
    header = tk.Frame(root, bg=config.CARD)

    # ---------- LOGO + TITEL ----------
    from PIL import Image, ImageTk
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(base_dir, "assets", "Logo.png")

    left_frame = tk.Frame(header, bg=config.CARD)
    left_frame.pack(side="left", padx=6, pady=4)

    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path).resize((120, 100), Image.LANCZOS)
            logo_img = ImageTk.PhotoImage(img)
            logo_label = tk.Label(left_frame, image=logo_img, bg=config.CARD)
            logo_label.image = logo_img
            logo_label.pack(side="left", padx=(0, 10))
        except Exception as e:
            print(f"⚠️ Logo konnte nicht geladen werden: {e}")

    title = tk.Label(
        left_frame,
        text="🌱 VIVOSUN Thermo Dashboard\n     for THB-1S",
        bg=config.CARD,
        fg=config.TEXT,
        font=("Segoe UI", 20, "bold"),
        anchor="w",
        justify="left"
    )
    title.pack(side="left", anchor="center")

    # ---------- OFFSETS ----------
    controls = tk.Frame(header, bg=config.CARD)
    controls.pack(side="right", pady=2)

    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    unit_celsius = tk.BooleanVar(value=cfg.get("unit_celsius", True))

    tk.Label(
        controls,
        text=f"Leaf Temp Offset ({'°C' if unit_celsius.get() else '°F'}):",
        bg=config.CARD,
        fg=config.TEXT
    ).pack(side="left", padx=6)

    # Globale Tk-Variablen für externen Sync
    global leaf_offset_var, hum_offset_var
    leaf_offset_var = tk.DoubleVar(value=float(config.leaf_offset_c[0]))
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

    tk.Label(
        controls,
        text="Humidity Offset (%):",
        bg=config.CARD,
        fg=config.TEXT
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
        bg=config.CARD,
        fg=config.TEXT,
        justify="center"
    ).pack(side="left")

    # ---------- RESET BUTTON ----------
    def reset_offsets():
        leaf_offset_var.set(0.0)
        hum_offset_var.set(0.0)
        print("Offsets reset (Leaf=0.0°C, Humidity=0.0%)")

    tk.Button(
        controls,
        text="↺ Reset Offsets",
        command=reset_offsets,
        bg="orange",
        fg="black"
    ).pack(side="left", padx=6)

    # ---------- BUTTON-ROWS ----------
    button_frame = tk.Frame(header, bg=config.CARD)
    button_frame.pack(side="bottom", fill="x", pady=4)

    row1 = tk.Frame(button_frame, bg=config.CARD)
    row1.pack(side="top", pady=2)

    row2 = tk.Frame(button_frame, bg=config.CARD)
    row2.pack(side="top", pady=2)

    # ---------- BUTTON-FUNKTIONEN ----------

    def reset_charts():
        """Leert alle Datenpuffer aus charts_gui, ohne das Dashboard neu zu laden."""
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

    def delete_config():
        from tkinter import messagebox
        if os.path.exists(config.CONFIG_FILE):
            if messagebox.askyesno("Confirm", "Delete config.json?"):
                try:
                    os.remove(config.CONFIG_FILE)
                    print("config.json deleted ✅")
                except Exception as e:
                    print(f"❌ Error deleting config.json: {e}")
        else:
            print("⚠️ config.json not found")

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

            print(f"💾 CSV exportiert → {path}")
        except Exception as e:
            print(f"❌ CSV-Export fehlgeschlagen: {e}")

    def restart_program():
        print("🔄 Restarting program...")
        python = sys.executable
        os.execl(python, python, *sys.argv)

    # ---------- FENSTER-FUNKTIONEN ----------
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
    tk.Button(row1, text="🧹 Reset Charts", command=reset_charts).pack(side="left", padx=6)
    tk.Button(row1, text="🗑 Delete Config", command=delete_config).pack(side="left", padx=6)
    tk.Button(row1, text="💾 Export Chart", command=export_chart).pack(side="left", padx=6)

    tk.Button(row2, text="📈 VPD Scatter", command=open_scattered_vpd).pack(side="left", padx=6)
    tk.Button(row2, text="📊 GrowHub CSV", command=open_growhub_csv).pack(side="left", padx=6)
    tk.Button(row2, text="🔄 Restart Program", command=restart_program).pack(side="left", padx=6)

    # Nach Aufbau einmal sicherstellen, dass GUI-Spinboxen exakt config zeigen
    sync_offsets_to_gui()

    return header
