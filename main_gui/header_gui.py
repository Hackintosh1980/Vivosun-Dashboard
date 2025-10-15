#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
header_gui.py – Theme-Enabled Header mit stabilem Offset-Sync (Celsius/Fahrenheit)
"""

import tkinter as tk
import os, sys
import config
import utils
from PIL import Image, ImageTk

# --- Pfad-Fix (muss vor Widget-Imports stehen!) ---
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Jetzt funktioniert dieser Import:
from widgets.windows import scattered_window

THEME = config.THEME  # 🌈 Aktives Theme laden

leaf_offset_var = None
hum_offset_var = None



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
    controls.pack(side="right", padx=12, pady=6, anchor="e")

    # --- Config lesen ---
    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    use_celsius = cfg.get("unit_celsius", True)
    unit_label = "°C" if use_celsius else "°F"

    # --- Leaf Offset ---
    tk.Label(
        controls,
        text=f"🌿 Leaf Offset ({unit_label}):",
        bg=THEME.CARD_BG,
        fg=THEME.TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=0, padx=4, pady=2, sticky="e")

    leaf_offset_var = tk.StringVar(
        value=utils.format_offset_display(config.leaf_offset_c[0], use_celsius)
    )

    entry_leaf = tk.Entry(
        controls,
        textvariable=leaf_offset_var,
        width=6,
        bg=THEME.BG_MAIN,
        fg=THEME.TEXT,
        justify="center",
        relief="flat",
        font=("Segoe UI", 11, "bold")
    )
    entry_leaf.grid(row=0, column=1, padx=4)

    def change_leaf_offset(delta):
        """Offset ändern – stabil für °C und °F."""
        try:
            # Wir holen IMMER den letzten echten °C-Wert aus config
            current_c = float(config.leaf_offset_c[0])
            step_c = delta if use_celsius else delta * 5.0 / 9.0
            new_val_c = round(current_c + step_c, 3)

            utils.set_offsets_from_outside(leaf=new_val_c, persist=True)
            leaf_offset_var.set(utils.format_offset_display(new_val_c, use_celsius))
        except Exception:
            pass
        
    def apply_leaf_offset():
        """Manuelle Eingabe übernehmen (Return/Fokusverlust)."""
        try:
            new_val_c = utils.parse_offset_input(leaf_offset_var.get(), use_celsius)
            utils.set_offsets_from_outside(leaf=new_val_c, persist=True)
            leaf_offset_var.set(utils.format_offset_display(new_val_c, use_celsius))
        except Exception:
            pass
        
    tk.Button(
        controls, text="▲", font=("Segoe UI", 11, "bold"),
        bg=THEME.LIME, fg="black", relief="flat",
        command=lambda: change_leaf_offset(+0.1)
    ).grid(row=0, column=2, padx=2)

    tk.Button(
        controls, text="▼", font=("Segoe UI", 11, "bold"),
        bg=THEME.LIME, fg="black", relief="flat",
        command=lambda: change_leaf_offset(-0.1)
    ).grid(row=0, column=3, padx=2)

    entry_leaf.bind("<Return>", lambda e: apply_leaf_offset())
    entry_leaf.bind("<FocusOut>", lambda e: apply_leaf_offset())

    # --- Humidity Offset ---
    tk.Label(
        controls,
        text="💧 Humidity Offset (%):",
        bg=THEME.CARD_BG,
        fg=THEME.TEXT,
        font=("Segoe UI", 10, "bold")
    ).grid(row=1, column=0, padx=4, pady=2, sticky="e")

    hum_offset_var = tk.StringVar(value=f"{float(config.humidity_offset[0]):.1f}")

    entry_hum = tk.Entry(
        controls,
        textvariable=hum_offset_var,
        width=6,
        bg=THEME.BG_MAIN,
        fg=THEME.TEXT,
        justify="center",
        relief="flat",
        font=("Segoe UI", 11, "bold")
    )
    entry_hum.grid(row=1, column=1, padx=4)

    def apply_hum_offset():
        try:
            new_val = round(float(hum_offset_var.get()), 1)
            utils.set_offsets_from_outside(hum=new_val, persist=True)
            hum_offset_var.set(f"{new_val:.1f}")
        except Exception:
            pass

    def change_hum_offset(delta):
        new_val = round(float(hum_offset_var.get()) + delta, 1)
        utils.set_offsets_from_outside(hum=new_val, persist=True)
        hum_offset_var.set(f"{new_val:.1f}")

    tk.Button(
        controls, text="▲", font=("Segoe UI", 11, "bold"),
        bg=THEME.LIME, fg="black", relief="flat",
        command=lambda: change_hum_offset(+1.0)
    ).grid(row=1, column=2, padx=2)

    tk.Button(
        controls, text="▼", font=("Segoe UI", 11, "bold"),
        bg=THEME.LIME, fg="black", relief="flat",
        command=lambda: change_hum_offset(-1.0)
    ).grid(row=1, column=3, padx=2)

    entry_hum.bind("<Return>", lambda e: apply_hum_offset())
    entry_hum.bind("<FocusOut>", lambda e: apply_hum_offset())

    # --- Reset Button ---
    THEME.make_button(
        header,
        "↺ Reset Offsets",
        lambda: utils.set_offsets_from_outside(leaf=0.0, hum=0.0, persist=True),
        color=getattr(THEME, "LIME", "#00FF88")
    ).pack(side="right", padx=12, pady=4)

    # --- Global Sync ---
    def on_global_offset_change(leaf, hum):
        cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
        use_celsius = cfg.get("unit_celsius", True)
        leaf_offset_var.set(utils.format_offset_display(leaf, use_celsius))
        hum_offset_var.set(f"{hum:.1f}")

    utils.register_offset_callback(on_global_offset_change)
    
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

            if hasattr(charts_gui, "global_data_buffers") and charts_gui.global_data_buffers:
                for key, buf in charts_gui.global_data_buffers.items():
                    if isinstance(buf, list):
                        buf.clear()
                if "timestamps" in charts_gui.global_data_buffers:
                    charts_gui.global_data_buffers["timestamps"].clear()
                print("✅ Charts erfolgreich zurückgesetzt.")
            else:
                print("⚠️ Keine aktiven Datenpuffer gefunden.")

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

            # 🔧 FIX: Import aus widgets statt Hauptordner
            from widgets import growhub_csv_viewer

            win = growhub_csv_viewer.open_window(root, config=config)
            open_windows["csv"] = win
            win.protocol("WM_DELETE_WINDOW", lambda: (open_windows.pop("csv", None), win.destroy()))

        except Exception as e:
            print(f"⚠️ Fehler im GrowHub CSV Viewer: {e}")

    def open_test_window():
        try:
            if "test" in open_windows and open_windows["test"].winfo_exists():
                open_windows["test"].lift()
                return
            from widgets.test_window import open_window
            win = open_window(root, config=config)
            open_windows["test"] = win
            win.protocol("WM_DELETE_WINDOW", lambda: (open_windows.pop("test", None), win.destroy()))
        except Exception as e:
            print(f"⚠️ Fehler beim Öffnen des Test Windows: {e}")

    def open_scattered_window():
        """Öffnet das neue modulare Scattered-VPD-Fenster."""
        try:
            if "scattered_window" in open_windows and open_windows["scattered_window"].winfo_exists():
                open_windows["scattered_window"].lift()
                return

            from widgets.windows import scattered_window

            win = scattered_window.open_window(root, config=config)
            open_windows["scattered_window"] = win

            win.protocol(
                "WM_DELETE_WINDOW",
                lambda: (open_windows.pop("scattered_window", None), win.destroy())
            )

        except Exception as e:
            print(f"⚠️ Fehler beim Öffnen des Scattered-Windows: {e}")





      
    # ---------- BUTTONS ----------
    THEME.make_button(row1, "🧹 Reset Charts", reset_charts, color=THEME.LIME).pack(side="left", padx=6)
    THEME.make_button(row1, "💾 Export Chart", export_chart, color=THEME.LIME).pack(side="left", padx=6)
    THEME.make_button(row1, "⚙️ Settings", open_settings, color=THEME.LIME).pack(side="left", padx=6)
    THEME.make_button(row2, "📈 VPD Scatter old", open_scattered_vpd, color=THEME.LIME).pack(side="left", padx=6)
    THEME.make_button(row2, "📊 GrowHub CSV", open_growhub_csv, color=THEME.LIME).pack(side="left", padx=6)
    THEME.make_button(row2, "🧪 Test Window", open_test_window, color=THEME.LIME).pack(side="left", padx=6)
    THEME.make_button(row2, "🧪 New Scatter", open_scattered_window, color=THEME.LIME).pack(side="left", padx=6)

    return header
