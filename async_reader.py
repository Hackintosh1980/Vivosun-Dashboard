#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
async_reader.py – Hintergrund-Reader für VIVOSUN Thermo
Liest Daten via vivosun_thermo, schreibt JSON + CSV im GrowHub-Format
mit Auto-Reconnect bei Verbindungsfehlern.
Schreibt zusätzlich status.json mit {"connected": True/False}.
"""

import asyncio
import datetime
import traceback
import threading
import os
import sys

try:
    from . import utils, config
except ImportError:
    import utils, config

# -------------------------------------------------------------------
# Helper: Safe path resolver (works in source & PyInstaller bundle)
# -------------------------------------------------------------------
def resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Control
_running = False
_thread = None

# Status-Datei (Pfad im Bundle absichern)
STATUS_FILE = resource_path(getattr(config, "STATUS_FILE", "status.json"))


async def _read_loop(device_id, log_callback=None):
    """
    Async loop: poll device and write JSON + CSV.
    Bricht bei Fehlern den Client ab und versucht Reconnect.
    """
    from vivosun_thermo import (
        VivosunThermoClient,
        PROBE_MAIN,
        PROBE_EXTERNAL,
        UNIT_CELSIUS,
    )

    while _running:  # Reconnect-Loop
        try:
            async with VivosunThermoClient(device_id) as client:
                if log_callback:
                    log_callback(f"✅ Connected to device {device_id}")
                utils.safe_write_json(STATUS_FILE, {"connected": True})

                while _running:
                    try:
                        # Messwerte holen
                        t_main = await client.current_temperature(PROBE_MAIN, UNIT_CELSIUS)
                        h_main = await client.current_humidity(PROBE_MAIN)
                        t_ext  = await client.current_temperature(PROBE_EXTERNAL, UNIT_CELSIUS)
                        h_ext  = await client.current_humidity(PROBE_EXTERNAL)

                        ts = datetime.datetime.utcnow().isoformat()
                        payload = {
                            "timestamp": ts,
                            "t_main": float(t_main) if t_main is not None else None,
                            "h_main": float(h_main) if h_main is not None else None,
                            "t_ext":  float(t_ext) if t_ext is not None else None,
                            "h_ext":  float(h_ext) if h_ext is not None else None,
                        }

                        # JSON snapshot
                        try:
                            utils.safe_write_json(resource_path(config.DATA_FILE), payload)
                        except Exception as e:
                            if log_callback:
                                log_callback(f"⚠️ Snapshot write failed: {e}")

                        # CSV logging (GrowHub-Format, nur MAIN)
                        try:
                            ts_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            t = payload["t_main"]
                            h = payload["h_main"]
                            vpd = None
                            if t is not None and h is not None:
                                vpd = utils.calc_vpd(t, h)

                            utils.append_csv_row(
                                resource_path(config.HISTORY_FILE),
                                ["Timestamp", "Temperature", "Humidity", "VPD"],
                                [ts_str, t, h, vpd],
                            )
                        except Exception as e:
                            if log_callback:
                                log_callback(f"⚠️ Append CSV failed: {e}")

                        # Verbindung als aktiv markieren
                        utils.safe_write_json(STATUS_FILE, {"connected": True})

                    except Exception as e:
                        if log_callback:
                            log_callback(f"⚠️ Device read error → reconnecting: {e}\n{traceback.format_exc()}")
                        utils.safe_write_json(STATUS_FILE, {"connected": False})
                        break  # beendet die innere while → Client-Context schließt sich

                    await asyncio.sleep(getattr(config, "SCAN_INTERVAL", 5))

        except Exception as e:
            if log_callback:
                log_callback(f"❌ Could not connect: {e}\n{traceback.format_exc()}")
            utils.safe_write_json(STATUS_FILE, {"connected": False})

        # Warten bis zum nächsten Reconnect-Versuch
        delay = getattr(config, "RECONNECT_DELAY", 10)
        if log_callback:
            log_callback(f"🔄 Reconnecting in {delay}s ...")
        await asyncio.sleep(delay)


def start_reader_thread(device_id, log_callback=None):
    """Startet den Background Reader in eigenem Thread."""
    global _thread, _running
    if _thread and _thread.is_alive():
        return
    _running = True

    def runner():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_read_loop(device_id, log_callback))

    _thread = threading.Thread(target=runner, daemon=True)
    _thread.start()


def stop_reader():
    """Beendet den Reader-Loop."""
    global _running
    _running = False
    utils.safe_write_json(STATUS_FILE, {"connected": False})


def list_devices():
    """Device-ID aus config.json zurückgeben (CLI Kompatibilität)."""
    cfg = utils.safe_read_json(resource_path(config.CONFIG_FILE)) or {}
    did = cfg.get("device_id")
    return [did] if did else []


def scan_once():
    """Letzten Snapshot aus DATA_FILE zurückgeben."""
    return utils.safe_read_json(resource_path(config.DATA_FILE))
