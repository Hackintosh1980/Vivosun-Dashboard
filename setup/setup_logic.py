#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_logic.py – Logik für VIVOSUN Setup (Scan, Save, Progress, Queue)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading, queue, asyncio, re
import utils, config
from vivosun_thermo import VivosunThermoScanner
from main_gui import core_gui
from themes import theme_vivosun, theme_oceanic


# ------------------------------------------------------------
# 🌈 Themes
# ------------------------------------------------------------
THEMES = {
    "🌿 VIVOSUN Green": theme_vivosun,
    "🌊 Oceanic Blue": theme_oceanic,
}


def load_theme_from_config():
    """Lädt das aktuelle Theme aus config.json oder gibt Default zurück."""
    try:
        cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
        t = cfg.get("theme")
        if t in THEMES:
            return t
    except Exception:
        pass
    return "🌿 VIVOSUN Green"


# ------------------------------------------------------------
# 🚀 Gerätescan starten (mit Timeout)
# ------------------------------------------------------------
def start_device_scan(text_widget, result_queue, scan_btn, start_pulse, timeout=10):
    """
    Startet asynchron den BLE-Scan nach VIVOSUN-Geräten.
    Beendet sich automatisch nach <timeout> Sekunden.
    """
    def worker():
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            scanner = VivosunThermoScanner()
            found = loop.run_until_complete(scanner.discover(timeout=timeout))
            if not found:
                result_queue.put("⚠️ Keine Geräte gefunden.")
            else:
                out = []
                for d in found:
                    name = (getattr(d, "name", "") or "").strip()
                    addr = getattr(d, "address", None) or getattr(d, "identifier", None)
                    if not name or not addr:
                        continue
                    if not any(x in name.lower() for x in ("vivosun", "thermobeacon")):
                        continue
                    device_id = getattr(d, "identifier", addr)
                    out.append(f"{device_id}  |  {name}")
                result_queue.put("\n".join(out))
        except asyncio.TimeoutError:
            result_queue.put("⏱️ Scan-Timeout nach {timeout} Sekunden.")
        except Exception as e:
            result_queue.put(f"❌ Scanfehler: {e}")
        finally:
            loop.close()

    # UI vorbereiten
    text_widget.insert("end", f"🔍 Suche nach Geräten ({timeout}s)…\n")
    text_widget.see("end")
    scan_btn.config(state="disabled")
    start_pulse()
    threading.Thread(target=worker, daemon=True).start()


# ------------------------------------------------------------
# 💾 Auswahl speichern
# ------------------------------------------------------------
def save_selected_device(device_listbox, text, theme_var, root):
    """Speichert die gewählte Device-ID + Theme + Einheit in config.json."""
    sel = device_listbox.curselection()
    if not sel:
        text.insert("end", "❌ Kein Gerät ausgewählt!\n")
        text.see("end")
        return

    selected_line = device_listbox.get(sel[0])
    selected_id = selected_line.split("|")[0].replace("⚪", "").strip()

    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    cfg["device_id"] = selected_id
    cfg["theme"] = theme_var.get()

    use_celsius = messagebox.askyesno(
        "Unit Selection", "Möchten Sie Celsius verwenden?\n\nYes = °C, No = °F"
    )
    cfg["unit_celsius"] = use_celsius

    utils.safe_write_json(config.CONFIG_FILE, cfg)
    text.insert("end", f"💾 Gespeichert: Device {selected_id} ({'°C' if use_celsius else '°F'})\n")
    text.see("end")

    root.destroy()
    core_gui.run_app(selected_id)


# ------------------------------------------------------------
# 🔁 Fortschrittspuls
# ------------------------------------------------------------
def create_progress_pulse(progress, root):
    pulse_running = False
    pulse_value = 0
    pulse_dir = 1

    def start_pulse():
        nonlocal pulse_running, pulse_value, pulse_dir
        pulse_running = True
        pulse_value = 0
        pulse_dir = 1
        animate_pulse()

    def stop_pulse():
        nonlocal pulse_running
        pulse_running = False
        progress["value"] = 0

    def animate_pulse():
        nonlocal pulse_value, pulse_dir
        if not pulse_running:
            return
        pulse_value += pulse_dir * 5
        if pulse_value >= 100:
            pulse_value, pulse_dir = 100, -1
        elif pulse_value <= 0:
            pulse_value, pulse_dir = 0, 1
        progress["value"] = pulse_value
        root.after(50, animate_pulse)

    return start_pulse, stop_pulse


# ------------------------------------------------------------
# 📋 Scan-Ausgabe verarbeiten
# ------------------------------------------------------------
def finish_scan_output(output, text_widget, device_listbox, devices, add_device):
    """Verarbeitet die Ausgabe aus dem BLE-Scan (Ergebnis-Queue) und aktualisiert die UI."""
    try:
        text_widget.insert("end", output + "\n✅ Scan abgeschlossen.\n")
        text_widget.see("end")

        devices.clear()
        device_listbox.delete(0, tk.END)

        pattern = r"([0-9A-F]{8}(?:-[0-9A-F]{4}){3}-[0-9A-F]{12}|(?:[0-9A-F]{2}:){5}[0-9A-F]{2})"
        for line in output.splitlines():
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                dev_id = match.group(1)
                name = line.split("|")[-1].strip() if "|" in line else "Device"
                devices.append(dev_id)
                add_device(dev_id, name)

        if not devices:
            text_widget.insert("end", "⚠️ Keine gültigen Device-IDs gefunden.\n")
            text_widget.see("end")

    except Exception as e:
        text_widget.insert("end", f"❌ Fehler bei Scanverarbeitung: {e}\n")
        text_widget.see("end")
