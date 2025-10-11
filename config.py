#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config.py – zentrale Konfiguration für das 🌱 VIVOSUN Thermo Dashboard
"""

import os
import sys
import json
from pathlib import Path

# =====================================================
#                 BASIS-INFORMATIONEN
# =====================================================

APP_NAME     = "VIVOSUN Thermo Dashboard"
APP_DISPLAY  = "🌱 VIVOSUN Thermo Dashboard"
APP_VERSION  = "1.2.4"
APP_AUTHOR   = "Dominik Rosenthal"
APP_COPYRIGHT = f"© 2025 {APP_AUTHOR}"
APP_GITHUB   = "https://github.com/Hackintosh1980/Vivosun-Dashboard"


# =====================================================
#                 PFAD-DEFINITIONEN
# =====================================================

def app_root() -> Path:
    """Ermittle den App-Root – funktioniert sowohl im Source- als auch im PyInstaller-Build."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent

BASE_DIR  = app_root()
DATA_DIR  = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

CONFIG_FILE  = DATA_DIR / "config.json"
DATA_FILE    = DATA_DIR / "thermo_values.json"
HISTORY_FILE = DATA_DIR / "thermo_history.csv"
STATUS_FILE  = DATA_DIR / "status.json"


# =====================================================
#                 STANDARD-FARBEN
# =====================================================

BG     = "#0b1620"
CARD   = "#0f1e2a"
TEXT   = "#d6eaff"
ACCENT = "#8be9fd"


# =====================================================
#                     TIMING
# =====================================================

UI_POLL_INTERVAL     = 1.0   # Sekunden für UI-Refresh
PLOT_BUFFER_LEN      = 600   # Anzahl gespeicherter Werte
SENSOR_POLL_INTERVAL = 1     # Sekunden zwischen Messungen
RECONNECT_DELAY      = 3     # Sekunden zwischen Reconnect-Versuchen


# =====================================================
#                   OFFSET-WERTE
# =====================================================

leaf_offset_c   = [0.0]   # Leaf-Temp-Offset (°C)
humidity_offset = [0.0]   # Humidity-Offset (%)


# =====================================================
#              EINHEIT (°C / °F)
# =====================================================

def load_unit_preference() -> bool:
    """Liest unit_celsius aus config.json oder True als Fallback."""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return bool(data.get("unit_celsius", True))
    except Exception:
        pass
    return True


def save_unit_preference(value: bool) -> None:
    """Speichert unit_celsius in config.json und bewahrt weitere Schlüssel."""
    try:
        cfg = {}
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
        cfg["unit_celsius"] = bool(value)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=4)
    except Exception as e:
        print(f"⚠️ Fehler beim Speichern von unit_celsius: {e}")


# aktuelle Einheit laden (als Bool, nicht Liste!)
unit_celsius = load_unit_preference()
