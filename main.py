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
# Imports (neue Struktur)
# -------------------------------------------------------------
from main_gui.core_gui import run_app  # 🌿 Dashboard
from setup.setup_gui import run_setup  # ⚙️ Neues Setup-Modul
import config, utils


# -------------------------------------------------------------
# App-Startfunktion
# -------------------------------------------------------------
def main():
    """Startet Setup oder Dashboard abhängig von Config."""
    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    device_id = cfg.get("device_id")

    # --- Kein Gerät gespeichert → Setup starten ---
    if not device_id:
        print("⚠️ Kein device_id gefunden → Starte Setup...")
        run_setup()
        sys.exit(0)

    # --- Alte Log-/Status-Dateien löschen ---
    for f in [config.DATA_FILE, config.HISTORY_FILE, getattr(config, "STATUS_FILE", None)]:
        if not f:
            continue
        try:
            if os.path.exists(f):
                os.remove(f)
                print(f"🗑 Gelöscht: {os.path.basename(f)}")
        except Exception as e:
            print(f"⚠️ Fehler beim Löschen von {os.path.basename(f)}: {e}")

    # --- Neue Statusdatei anlegen ---
    try:
        with open(config.STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump({"connected": False}, f, indent=2)
        print("📄 Neue status.json erstellt (connected = False)")
    except Exception as e:
        print(f"⚠️ Fehler beim Erstellen von status.json: {e}")

    # --- Dashboard starten ---
    print(f"🌱 Starte Dashboard mit Device: {device_id}")
    run_app(device_id)


# -------------------------------------------------------------
# Entry Point
# -------------------------------------------------------------
if __name__ == "__main__":
    main()
