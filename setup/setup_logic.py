#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_logic.py – Logik für VIVOSUN Setup (Scan, Save, Progress, Queue)
"""

import asyncio
import queue
import re
import threading
import tkinter as tk
from tkinter import messagebox

import config, utils
from vivosun_thermo import VivosunThermoScanner
from main_gui import core_gui
import tkinter as tk
from tkinter import messagebox, ttk   # ← ttk hier mit importieren
from themes import theme_vivosun, theme_oceanic
try:
    from themes import theme_sunset
    THEMES = {
        "🌿 VIVOSUN Green": theme_vivosun,
        "🌊 Oceanic Blue": theme_oceanic,
        "🔥 VIVOSUN Sunset": theme_sunset,
    }
except Exception:
    THEMES = {
        "🌿 VIVOSUN Green": theme_vivosun,
        "🌊 Oceanic Blue": theme_oceanic,
    }


# ========== Theme Helpers ==========
def load_theme_from_config() -> str:
    try:
        cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
        name = cfg.get("theme")
        if name in THEMES:
            return name
    except Exception:
        pass
    return "🌿 VIVOSUN Green"


def get_theme_by_name(name: str):
    return THEMES.get(name, theme_vivosun)


def save_theme_to_config(name: str):
    try:
        cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
        cfg["theme"] = name
        utils.safe_write_json(config.CONFIG_FILE, cfg)
    except Exception:
        pass


# ========== Result Queue Helpers ==========
def make_result_queue():
    return queue.Queue()


def try_get_result(q: queue.Queue):
    try:
        return q.get_nowait()
    except queue.Empty:
        return None


# ========== Scan ==========
def start_device_scan(text_widget: tk.Text, result_queue: queue.Queue, scan_btn: tk.Widget, start_pulse):
    """
    Startet asynchron den BLE-Scan (10s) und schreibt Ergebnis in result_queue.
    """
    def worker():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            scanner = VivosunThermoScanner()
            found = loop.run_until_complete(scanner.discover(timeout=10))
            if not found:
                result_queue.put("⚠️ Keine Geräte gefunden.")
            else:
                lines = []
                for d in found:
                    name = (getattr(d, "name", "") or "").strip()
                    addr = getattr(d, "address", None) or getattr(d, "identifier", None)
                    if not name or not addr:
                        continue
                    if not any(x in name.lower() for x in ("vivosun", "thermobeacon")):
                        continue
                    device_id = getattr(d, "identifier", addr)
                    lines.append(f"{device_id}  |  {name}")
                if lines:
                    result_queue.put("\n".join(lines))
                else:
                    result_queue.put("⚠️ Keine passenden VIVOSUN-Geräte gefunden.")
        except Exception as e:
            result_queue.put(f"❌ Scanfehler: {e}")
        finally:
            try:
                loop.close()
            except Exception:
                pass

    try:
        text_widget.insert("end", "🔍 Suche nach Geräten (10s)…\n")
        text_widget.see("end")
    except Exception:
        pass

    try:
        scan_btn.config(state="disabled")
    except Exception:
        pass

    start_pulse()
    threading.Thread(target=worker, daemon=True).start()


def finish_scan_output(output: str, text_widget: tk.Text, device_listbox: tk.Listbox, devices: list, add_device_cb):
    """
    Verarbeitet Ausgabe nach einem Scan: Log-Text + Listbox + Devices-Liste.
    """
    try:
        text_widget.insert("end", output + "\n✅ Scan abgeschlossen.\n")
        text_widget.see("end")
    except Exception:
        pass

    try:
        devices.clear()
        device_listbox.delete(0, tk.END)
    except Exception:
        pass

    pattern = r"([0-9A-F]{8}(?:-[0-9A-F]{4}){3}-[0-9A-F]{12}|(?:[0-9A-F]{2}:){5}[0-9A-F]{2})"
    for line in output.splitlines():
        m = re.search(pattern, line, re.IGNORECASE)
        if m:
            dev_id = m.group(1)
            name = line.split("|")[-1].strip() if "|" in line else "Device"
            devices.append(dev_id)
            try:
                add_device_cb(dev_id, name)
            except Exception:
                pass

    if not devices:
        try:
            text_widget.insert("end", "⚠️ Keine gültigen Device-IDs gefunden.\n")
            text_widget.see("end")
        except Exception:
            pass


# ========== Save ==========
def save_selected_device(root: tk.Tk, device_listbox: tk.Listbox, text_widget: tk.Text, theme_var: tk.StringVar):
    """
    Speichert selektiertes Device + Theme + Unit in config.json und startet Dashboard.
    """
    sel = device_listbox.curselection() if hasattr(device_listbox, "curselection") else ()
    if not sel:
        try:
            text_widget.insert("end", "❌ Kein Gerät ausgewählt!\n")
            text_widget.see("end")
        except Exception:
            pass
        return

    selected_line = device_listbox.get(sel[0])
    selected_id = selected_line.split("|")[0].replace("⚪", "").strip()

    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    cfg["device_id"] = selected_id
    try:
        cfg["theme"] = theme_var.get()
    except Exception:
        cfg["theme"] = load_theme_from_config()

    use_c = messagebox.askyesno("Unit Selection", "Möchten Sie Celsius verwenden?\n\nYes = °C, No = °F")
    cfg["unit_celsius"] = use_c

    utils.safe_write_json(config.CONFIG_FILE, cfg)

    try:
        text_widget.insert("end", f"💾 Gespeichert: Device {selected_id} ({'°C' if use_c else '°F'})\n")
        text_widget.see("end")
    except Exception:
        pass

    try:
        root.destroy()
    except Exception:
        pass

    core_gui.run_app(selected_id)


# ========== Progress Pulse ==========
def create_progress_pulse(progress: ttk.Progressbar, root: tk.Tk):
    running = {"state": False}
    value = {"v": 0}
    direction = {"d": 1}

    def start_pulse():
        running["state"] = True
        value["v"] = 0
        direction["d"] = 1
        tick()

    def stop_pulse():
        running["state"] = False
        try:
            progress["value"] = 0
        except Exception:
            pass

    def tick():
        if not running["state"]:
            return
        value["v"] += direction["d"] * 5
        if value["v"] >= 100:
            value["v"] = 100
            direction["d"] = -1
        elif value["v"] <= 0:
            value["v"] = 0
            direction["d"] = 1
        try:
            progress["value"] = value["v"]
        except Exception:
            pass
        root.after(50, tick)

    return start_pulse, stop_pulse
