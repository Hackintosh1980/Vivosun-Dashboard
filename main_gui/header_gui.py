#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
header_gui.py – Header mit großen Lime-Steppern und VIVOSUN-Buttons
"""

import tkinter as tk
import config, utils

# Farben & Fonts
BG_MAIN   = "#0b1620"
CARD_BG   = "#102430"
LIME      = "#a8ff60"
ORANGE    = "#ffaa00"
TEXT      = "#dfffe0"
FONT_TITLE = ("Segoe UI", 20, "bold")
FONT_BTN   = ("Segoe UI", 10, "bold")

leaf_offset_var = None
hum_offset_var  = None


def sync_offsets_to_gui():
    try:
        if isinstance(leaf_offset_var, tk.DoubleVar):
            leaf_offset_var.set(float(config.leaf_offset_c[0]))
        if isinstance(hum_offset_var, tk.DoubleVar):
            hum_offset_var.set(float(config.humidity_offset[0]))
    except Exception:
        pass


def set_offsets_from_outside(leaf=None, hum=None, persist=True):
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
        sync_offsets_to_gui()
    except Exception:
        pass


def styled_button(master, text, cmd, color=LIME):
    """Einheitlicher Lime-Button"""
    return tk.Button(
        master, text=text, command=cmd,
        bg=color, fg="black", font=FONT_BTN,
        activebackground=color, activeforeground="black",
        relief="flat", padx=10, pady=5, cursor="hand2"
    )


def add_stepper_field(parent, label, var, step, unit=""):
    """Stepper-Feld mit großen übereinanderliegenden Pfeilen"""
    frame = tk.Frame(parent, bg=CARD_BG)

    tk.Label(
        frame, text=label,
        bg=CARD_BG, fg=LIME, font=("Segoe UI", 10, "bold")
    ).grid(row=0, column=0, rowspan=2, sticky="w")

    entry = tk.Entry(
        frame, textvariable=var, width=6, justify="center",
        bg="#071116", fg=TEXT, insertbackground=TEXT,
        relief="flat", highlightthickness=1, highlightcolor=LIME
    )
    entry.grid(row=0, column=1, rowspan=2, padx=(10, 4))

    def step_val(delta):
        try:
            v = float(var.get()) + delta
        except Exception:
            v = 0.0
        var.set(round(v, 2))

    tk.Button(
        frame, text="▲", bg=LIME, fg="black",
        font=("Segoe UI", 11, "bold"), width=3,
        relief="flat", command=lambda: step_val(+step)
    ).grid(row=0, column=2, padx=(4, 4))

    tk.Button(
        frame, text="▼", bg=LIME, fg="black",
        font=("Segoe UI", 11, "bold"), width=3,
        relief="flat", command=lambda: step_val(-step)
    ).grid(row=1, column=2, padx=(4, 4))

    if unit:
        tk.Label(frame, text=unit, bg=CARD_BG, fg="#999",
                 font=("Segoe UI", 9)).grid(row=0, column=3, rowspan=2, padx=(4, 0))

    return frame


def build_header(root, config, data_buffers, time_buffer, log=lambda *a, **k: None):
    header = tk.Frame(root, bg=CARD_BG)
    header.pack(side="top", fill="x", padx=12, pady=8)

    import os
    from PIL import Image, ImageTk
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(base_dir, "assets", "Logo.png")

    # ---------- LINKS: Logo + Titel ----------
    left = tk.Frame(header, bg=CARD_BG)
    left.pack(side="left", padx=6, pady=4)

    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path).resize((120, 100))
            logo_img = ImageTk.PhotoImage(img)
            lbl = tk.Label(left, image=logo_img, bg=CARD_BG)
            lbl.image = logo_img
            lbl.pack(side="left", padx=(0, 10))
        except Exception as e:
            print(f"⚠️ Logo konnte nicht geladen werden: {e}")

    tk.Label(
        left,
        text="🌱 VIVOSUN Thermo Dashboard\n     for THB-1S",
        bg=CARD_BG, fg=LIME, font=FONT_TITLE,
        anchor="w", justify="left"
    ).pack(side="left", anchor="center")

    # ---------- RECHTS: Offsets ----------
    right = tk.Frame(header, bg=CARD_BG)
    right.pack(side="right", pady=2)

    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    unit_celsius = tk.BooleanVar(value=cfg.get("unit_celsius", True))

    global leaf_offset_var, hum_offset_var
    leaf_offset_var = tk.DoubleVar(value=float(config.leaf_offset_c[0]))
    hum_offset_var = tk.DoubleVar(value=float(config.humidity_offset[0]))

    def update_leaf_offset(*_):
        try:
            val = float(leaf_offset_var.get())
            c_val = val if unit_celsius.get() else val * 5.0 / 9.0
            set_offsets_from_outside(leaf=c_val, hum=None)
        except Exception:
            pass

    def update_hum_offset(*_):
        try:
            set_offsets_from_outside(leaf=None, hum=float(hum_offset_var.get()))
        except Exception:
            pass

    leaf_offset_var.trace_add("write", update_leaf_offset)
    hum_offset_var.trace_add("write", update_hum_offset)

    add_stepper_field(
        right,
        f"Leaf Offset ({'°C' if unit_celsius.get() else '°F'})",
        leaf_offset_var, 0.1
    ).pack(side="left", padx=6)

    add_stepper_field(
        right,
        "Humidity Offset (%)",
        hum_offset_var, 0.5
    ).pack(side="left", padx=6)

    styled_button(
        right,
        "↺ Reset Offsets",
        lambda: (leaf_offset_var.set(0.0), hum_offset_var.set(0.0)),
        ORANGE
    ).pack(side="left", padx=8)

    # ---------- BUTTON-REIHEN ----------
    btn_row = tk.Frame(header, bg=CARD_BG)
    btn_row.pack(side="bottom", fill="x", pady=4)

    def reset_charts():
        for buf in data_buffers.values():
            buf.clear()
        time_buffer.clear()
        log("📉 Charts reset")

    def delete_config():
        import os
        from tkinter import messagebox
        if os.path.exists(config.CONFIG_FILE):
            if messagebox.askyesno("Confirm", "Delete config.json?"):
                os.remove(config.CONFIG_FILE)
                log("🗑 config.json deleted ✅")

    def export_chart():
        from tkinter import filedialog
        import csv, datetime, os
        try:
            export_dir = filedialog.askdirectory(title="Exportziel wählen", mustexist=True)
            if not export_dir:
                return
            ts = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
            path = os.path.join(export_dir, f"chart_export_{ts}.csv")
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "t_main", "h_main", "vpd_int", "t_ext", "h_ext", "vpd_ext"])
                for i in range(len(time_buffer)):
                    row = [time_buffer[i].strftime("%Y-%m-%d %H:%M:%S")]
                    for k in ["t_main", "h_main", "vpd_int", "t_ext", "h_ext", "vpd_ext"]:
                        row.append(data_buffers[k][i] if i < len(data_buffers[k]) else "")
                    writer.writerow(row)
            log(f"💾 CSV exportiert → {path}")
        except Exception as e:
            log(f"❌ CSV-Export fehlgeschlagen: {e}")

    def restart_program():
        import os, sys
        log("🔄 Restarting program…")
        os.execl(sys.executable, sys.executable, *sys.argv)

    # ---------- Fenster-Funktionen ----------
    open_windows = {}

    def open_scattered_vpd():
        try:
            if "scatter" in open_windows and open_windows["scatter"].winfo_exists():
                open_windows["scatter"].lift(); return
            import widgets.scattered_vpd_chart as scattered_vpd_chart
            win = scattered_vpd_chart.open_window(root, config, utils)
            open_windows["scatter"] = win
            win.protocol("WM_DELETE_WINDOW",
                         lambda: (open_windows.pop("scatter", None), win.destroy()))
        except Exception as e:
            log(f"⚠️ Fehler beim Öffnen von VPD Scatter: {e}")

    def open_growhub_csv():
        try:
            if "csv" in open_windows and open_windows["csv"].winfo_exists():
                open_windows["csv"].lift(); return
            import widgets.growhub_csv_viewer as growhub_csv_viewer
            win = growhub_csv_viewer.open_window(root, config=config)
            open_windows["csv"] = win
            win.protocol("WM_DELETE_WINDOW",
                         lambda: (open_windows.pop("csv", None), win.destroy()))
        except Exception as e:
            log(f"⚠️ Fehler im GrowHub CSV Viewer: {e}")

    # ---------- Buttons ----------
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

    sync_offsets_to_gui()
    return header
