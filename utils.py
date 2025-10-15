#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils.py – zentrale Hilfsfunktionen für 🌱 VIVOSUN Dashboard
(inkl. JSON, CSV, VPD & globalem Offset-Sync)
"""

import json, math, os, csv, sys
try:
    import tkinter as tk
except Exception:
    tk = None

import config


# ===============================================================
# 🗂️ PATH HELPER
# ===============================================================
def resource_path(relative_path: str) -> str:
    """Gibt absoluten Pfad zurück, auch im PyInstaller-Bundle."""
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ===============================================================
# 📜 JSON HELPERS
# ===============================================================
def safe_read_json(path):
    try:
        with open(resource_path(path), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def safe_write_json(path, obj):
    full_path = resource_path(path)
    tmp = full_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=4)
    os.replace(tmp, full_path)


# ===============================================================
# 🌡️ CONVERSION
# ===============================================================
def c_to_f(c): return c * 9.0 / 5.0 + 32.0


# ===============================================================
# 💧 VPD CALCULATION
# ===============================================================
def calc_vpd(temp_c, rh):
    if temp_c is None or rh is None:
        return None
    svp = 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
    return round(svp * (1.0 - (rh / 100.0)), 3)


# ===============================================================
# 🧾 CSV HELPER
# ===============================================================
def append_csv_row(path, header, row):
    try:
        full_path = resource_path(path)
        file_exists = os.path.exists(full_path)
        with open(full_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(header)
            writer.writerow(row)
    except Exception as e:
        raise RuntimeError(f"CSV append failed for {path}: {e}")


# ===============================================================
# 🔧 GLOBAL OFFSET MANAGEMENT
# ===============================================================

class OffsetManager:
    """Zentrale, globale Verwaltung der Leaf/Humidity-Offsets (Singleton)."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OffsetManager, cls).__new__(cls)
            cls._instance.leaf_offset = 0.0
            cls._instance.hum_offset = 0.0
            cls._instance._callbacks = []  # Widgets, die benachrichtigt werden
        return cls._instance

    def load_from_config(self):
        cfg = safe_read_json(config.CONFIG_FILE) or {}
        self.leaf_offset = float(cfg.get("leaf_offset", 0.0))
        self.hum_offset = float(cfg.get("humidity_offset", 0.0))
        config.leaf_offset_c[0] = self.leaf_offset
        config.humidity_offset[0] = self.hum_offset

    def save_to_config(self):
        cfg = safe_read_json(config.CONFIG_FILE) or {}
        cfg["leaf_offset"] = self.leaf_offset
        cfg["humidity_offset"] = self.hum_offset
        safe_write_json(config.CONFIG_FILE, cfg)

    def register_callback(self, func):
        """Callback wird bei Änderungen benachrichtigt."""
        if func not in self._callbacks:
            self._callbacks.append(func)

    def notify(self):
        for cb in self._callbacks:
            try:
                cb(self.leaf_offset, self.hum_offset)
            except Exception:
                pass

    def set_offsets(self, leaf=None, hum=None, persist=True):
        if leaf is not None:
            self.leaf_offset = float(leaf)
            config.leaf_offset_c[0] = self.leaf_offset
        if hum is not None:
            self.hum_offset = float(hum)
            config.humidity_offset[0] = self.hum_offset
        if persist:
            self.save_to_config()
        self.notify()


# Globale Instanz
offsets = OffsetManager()
offsets.load_from_config()

# ===============================================================
# 🌡️ Conversion Helpers
# ===============================================================
def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0

def f_to_c(f):
    return (f - 32) * 5.0 / 9.0


# ===============================================================
# 🌡️ Offset Display Helpers
# ===============================================================
def format_offset_display(value_c, is_celsius=True):
    """
    Gibt den Offset in der richtigen Einheit (°C oder °F) zurück.
    value_c: interner Wert in °C
    """
    try:
        if value_c is None:
            return 0.0
        if is_celsius:
            return round(float(value_c), 1)
        else:
            return round(float(value_c) * 9.0 / 5.0, 1)
    except Exception:
        return 0.0


def parse_offset_input(value_display, is_celsius=True):
    """
    Konvertiert Eingabewert vom Display zurück nach °C (intern).
    Beispiel:
        - wenn Programm auf °F steht → wird der Wert nach °C konvertiert
        - sonst bleibt er gleich
    """
    try:
        if value_display is None:
            return 0.0
        if is_celsius:
            return round(float(value_display), 1)
        else:
            return round((float(value_display) * 5.0 / 9.0), 1)
    except Exception:
        return 0.0

    
# ===============================================================
# 🔗 PUBLIC API
# ===============================================================
def set_offsets_from_outside(leaf=None, hum=None, persist=True):
    offsets.set_offsets(leaf, hum, persist)


def sync_offsets_to_gui():
    offsets.load_from_config()
    offsets.notify()


def register_offset_callback(callback):
    """Wird vom Header oder Scattered-Fenster aufgerufen, um auf Änderungen zu reagieren."""
    offsets.register_callback(callback)
