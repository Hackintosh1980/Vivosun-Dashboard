#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
main.py – Startpunkt für das 🌱 VIVOSUN Thermo Dashboard
"""

import os
import sys
import json

# -------------------------------------------------------------
# Setup: Arbeitsverzeichnis & Pfade sicherstellen
# -------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# -------------------------------------------------------------
# Imports (aktuelle Struktur)
# -------------------------------------------------------------
from main_gui.core_gui import run_app  # Haupt-Dashboard
import setup_gui                   # ⚙️ Setup liegt jetzt im Root
import config, utils


# -------------------------------------------------------------
# App-Startfunktion
# -------------------------------------------------------------
def main():
    # --- Config prüfen ---
    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    device_id = cfg.get("device_id")

    if not device_id:
        print("⚠️ No device_id found → starting setup...")
        setup_gui.run_setup()
        sys.exit(0)

    # --- Alte Dateien löschen ---
    for f in [config.DATA_FILE, config.HISTORY_FILE, getattr(config, "STATUS_FILE", None)]:
        if not f:
            continue
        try:
            if os.path.exists(f):
                os.remove(f)
                print(f"🗑 Deleted old file: {os.path.basename(f)}")
        except Exception as e:
            print(f"⚠️ Could not delete {os.path.basename(f)}: {e}")

    # --- status.json neu anlegen ---
    try:
        with open(config.STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump({"connected": False}, f, indent=2)
        print("📄 New status.json created (connected = False)")
    except Exception as e:
        print(f"⚠️ Could not recreate status.json: {e}")

    # --- Dashboard starten ---
    print(f"🌱 Starting Dashboard with device {device_id}")
    run_app(device_id)


# -------------------------------------------------------------
# Entry Point
# -------------------------------------------------------------
if __name__ == "__main__":
    main()
