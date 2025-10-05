#!/usr/bin/env python3
import os, sys

try:
    from .gui import run_app
    from . import config, utils
    from . import setup_gui
except ImportError:
    from gui import run_app
    import config, utils
    import setup_gui


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
    for f in [config.DATA_FILE, config.HISTORY_FILE]:
        try:
            if os.path.exists(f):
                os.remove(f)
                print(f"🗑 Deleted old file: {f}")
        except Exception as e:
            print(f"⚠️ Could not delete {f}: {e}")

    # --- Dashboard starten ---
    print(f"🌱 Starting Dashboard with device {device_id}")
    run_app(device_id)


if __name__ == "__main__":
    main()
