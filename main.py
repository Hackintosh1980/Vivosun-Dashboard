#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json

# -------------------------------------------------------------
# Direkt-Start-kompatible Imports (kein Punkt-Prefix nötig)
# -------------------------------------------------------------
try:
    from gui import run_app
    import config, utils, setup_gui
except ImportError:
    # Fallback, falls als Paket gestartet wird
    from .gui import run_app
    from . import config, utils, setup_gui


def main():
    # --- Config prüfen ---
    cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
    device_id = cfg.get("device_id")

    if not device_id:
        print("⚠️ No device_id found → starting setup...")
        setup_gui.run_setup()
        # Nach Setup sofort beenden, sonst läuft Dashboard parallel
        sys.exit(0)

    # --- Immer frische Dateien erzeugen ---
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


if __name__ == "__main__":
    main()
