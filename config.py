#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
config.py – zentrale Konfiguration für das 🌱 VIVOSUN Thermo Dashboard
"""

import os

# --- App Infos ---
APP_NAME = "VIVOSUN Thermo Dashboard"        # Klarer Name für macOS / Info.plist
APP_DISPLAY = "🌱 VIVOSUN Thermo Dashboard"  # Mit Emoji für GUI / Titlebars
APP_VERSION = "1.2.2"
APP_AUTHOR = "Dominik Rosenthal"
APP_COPYRIGHT = f"© 2025 {APP_AUTHOR}"
APP_GITHUB = "https://github.com/sormy/vivosun-thermo"

# --- Basis-Pfade ---
BASE_DIR = os.path.dirname(__file__)
CONFIG_FILE  = os.path.join(BASE_DIR, "config.json")
DATA_FILE    = os.path.join(BASE_DIR, "thermo_values.json")
HISTORY_FILE = os.path.join(BASE_DIR, "thermo_history.csv")  # CSV-Logdatei
STATUS_FILE  = os.path.join(BASE_DIR, "status.json")         # Verbindungsstatus (für LED)

# --- UI Farben ---
BG     = "#0b1620"
CARD   = "#0f1e2a"
TEXT   = "#d6eaff"
ACCENT = "#8be9fd"

# --- Timing ---
UI_POLL_INTERVAL = 2.0    # Sekunden (GUI Refresh)
PLOT_BUFFER_LEN  = 600    # ~10 Minuten @ 1s

# --- Reader Polling ---
SCAN_INTERVAL = 2          # Sekunden zwischen Messungen

# --- Globale Offsets ---
leaf_offset_c   = [0.0]    # Leaf Temp Offset in °C
humidity_offset = [0.0]    # Humidity Offset in %

# --- Reconnect-Verhalten ---
RECONNECT_DELAY = 2        # Sekunden zwischen Reconnect-Versuchen
