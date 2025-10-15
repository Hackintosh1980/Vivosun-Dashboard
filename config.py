#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config.py – zentrale Konfiguration für das 🌱 VIVOSUN Thermo Dashboard
mit integriertem Theme-Loader (VIVOSUN Green, Sunset, Blue etc.)
"""

import os
import sys
import json
from pathlib import Path

# --- App Infos ---
APP_NAME = "VIVOSUN Thermo Dashboard"
APP_DISPLAY = "🌱 VIVOSUN Thermo Dashboard"
VERSION = "v3.0 Release"
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

# --- UI Farben (Fallback, falls Theme nicht geladen werden kann) ---
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

# =====================================================
#                 ANZEIGE / FORMATIERUNG
# =====================================================

TEMP_DECIMALS = 1        # Nachkommastellen für Temperatur (°C/°F)
HUMID_DECIMALS = 1       # Nachkommastellen für Luftfeuchte (%)
VPD_DECIMALS  = 2        # Nachkommastellen für VPD (kPa)

# =====================================================
#                     THEME SYSTEM 🌈
# =====================================================

def load_active_theme():
    """
    Lädt das aktuell gesetzte Theme aus config.json.
    Fällt automatisch auf das Standard-VIVOSUN-Theme zurück, wenn Fehler auftreten.
    """
    try:
        if not CONFIG_FILE.exists():
            raise FileNotFoundError("config.json fehlt, Theme nicht geladen")

        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        theme_name = cfg.get("theme", "🌿 VIVOSUN Green")

        # --- Dynamische Theme-Zuweisung ---
        if "Sunset" in theme_name:
            from themes import theme_sunset as theme
        elif "Blue" in theme_name or "Oceanic" in theme_name:
            from themes import theme_oceanic as theme
        else:
            from themes import theme_vivosun as theme

        return theme

    except Exception as e:
        print(f"⚠️ Theme konnte nicht geladen werden: {e}")
        from themes import theme_vivosun as theme
        return theme


# Globale THEME-Variable für alle Module verfügbar machen
THEME = load_active_theme()


DEBUG_LOGGING = True  # Kann über Settings toggled werden

# --- THEME COLORS (fallbacks for modules) ---
try:
    LIME = THEME.LIME
except Exception:
    LIME = "#00FF66"

try:
    ORANGE = THEME.ORANGE
except Exception:
    ORANGE = "#FF8800"
