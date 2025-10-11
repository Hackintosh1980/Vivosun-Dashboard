#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config.py – zentrale Konfiguration für das 🌱 VIVOSUN Thermo Dashboard
"""

import os
import sys
from pathlib import Path

# --- App Infos ---
APP_NAME = "VIVOSUN Thermo Dashboard"
APP_DISPLAY = "🌱 VIVOSUN Thermo Dashboard"
APP_VERSION = "1.2.2"
APP_AUTHOR = "Dominik Rosenthal"
APP_COPYRIGHT = f"© 2025 {APP_AUTHOR}"
APP_GITHUB = "https://github.com/Hackintosh1980/Vivosun-Dashboard"

# --- Basis-Pfade ---
def app_root() -> Path:
    """Ermittle den App-Root (funktioniert in Source & PyInstaller)."""
    if getattr(sys, "frozen", False):
        # onedir/onefile-Build (PyInstaller)
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent

BASE_DIR = app_root()
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# --- Datei-Pfade (alle unter /data) ---
CONFIG_FILE  = DATA_DIR / "config.json"
DATA_FILE    = DATA_DIR / "thermo_values.json"
HISTORY_FILE = DATA_DIR / "thermo_history.csv"
STATUS_FILE  = DATA_DIR / "status.json"

# --- UI Farben ---
BG     = "#0b1620"
CARD   = "#0f1e2a"
TEXT   = "#d6eaff"
ACCENT = "#8be9fd"

# =====================================================
#                     TIMING
# =====================================================


# --- Dashboard / GUI ---
UI_POLL_INTERVAL = 1.0         # Sekunden für UI-Refresh
PLOT_BUFFER_LEN  = 600         # Anzahl gespeicherter Werte (~10 min bei 1s)

# --- Sensor Polling ---
SENSOR_POLL_INTERVAL = 1       # Sekunden zwischen Messwertabfragen

# --- Reconnect-Verhalten ---
RECONNECT_DELAY = 3            # Sekunden zwischen Reconnect-Versuchen

# =====================================================
#                     OFFSETS
# =====================================================

leaf_offset_c   = [0.0]        # Leaf-Temp-Offset (°C)
humidity_offset = [0.0]        # Humidity-Offset (%)
