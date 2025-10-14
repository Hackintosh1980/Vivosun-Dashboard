#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
async_reader.py – stabile Version mit getrennter Sensorerkennung
Aktualisiert status.json alle 2 Sekunden mit:
{
  "connected": bool,
  "sensor_ok_main": bool,
  "sensor_ok_ext": bool,
  "sensor_ok": bool
}
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


_log_callback = None
_status_callback = None


def set_log_callback(func):
    global _log_callback
    _log_callback = func


def set_status_callback(func):
    global _status_callback
    _status_callback = func


def _log(msg):
    print(msg)
    if _log_callback:
        try:
            _log_callback(msg)
        except Exception:
            pass


def _status(connected: bool):
    if _status_callback:
        try:
            _status_callback(connected)
        except Exception:
            pass


# -------------------------------------------------------------------
# Helper
# -------------------------------------------------------------------
def resource_path(relative_path: str) -> str:
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# -------------------------------------------------------------------
# Globale Kontrolle
# -------------------------------------------------------------------
_running = False
_thread = None
_stop_event = threading.Event()
STATUS_FILE = resource_path(getattr(config, "STATUS_FILE", "status.json"))


# -------------------------------------------------------------------
# Hilfsfunktionen
# -------------------------------------------------------------------
def sanitize(value):
    """Filtert unplausible Sensorwerte (-0.07 … +0.07 = kein Signal)."""
    if value is None:
        return None
    try:
        v = float(value)
        if -0.07 <= v <= 0.07:
            return None
        return v
    except Exception:
        return None


def _clear_data_file():
    try:
        utils.safe_write_json(resource_path(config.DATA_FILE), {
            "timestamp": None,
            "t_main": None,
            "h_main": None,
            "t_ext": None,
            "h_ext": None,
        })
        _log("🧹 DATA_FILE geleert (Verbindungsverlust).")
    except Exception as e:
        _log(f"⚠️ DATA_FILE konnte nicht geleert werden: {e}")


def _update_status(connected: bool, sensor_ok_main: bool, sensor_ok_ext: bool):
    """Schreibt status.json bei jedem Zyklus neu."""
    try:
        data = {
            "connected": connected,
            "sensor_ok_main": sensor_ok_main,
            "sensor_ok_ext": sensor_ok_ext,
            # Rückwärtskompatibilität
            "sensor_ok": sensor_ok_main or sensor_ok_ext
        }
        utils.safe_write_json(STATUS_FILE, data)
        _status(connected)
        if not connected:
            _clear_data_file()
    except Exception as e:
        _log(f"⚠️ Fehler im Status-Update: {e}")


# -------------------------------------------------------------------
# Haupt-Async-Loop
# -------------------------------------------------------------------
async def _read_loop(device_id, log_callback=None):
    from vivosun_thermo import (
        VivosunThermoClient,
        PROBE_MAIN,
        PROBE_EXTERNAL,
        UNIT_CELSIUS,
    )

    SCAN_INTERVAL = getattr(config, "SCAN_INTERVAL", 2)

    while _running and not _stop_event.is_set():
        try:
            async with VivosunThermoClient(device_id) as client:
                _log(f"✅ Connected to device {device_id}")
                _update_status(True, False, False)

                while _running and not _stop_event.is_set():
                    try:
                        # Sensorwerte abfragen
                        t_main = sanitize(await client.current_temperature(PROBE_MAIN, UNIT_CELSIUS))
                        h_main = sanitize(await client.current_humidity(PROBE_MAIN))
                        t_ext = sanitize(await client.current_temperature(PROBE_EXTERNAL, UNIT_CELSIUS))
                        h_ext = sanitize(await client.current_humidity(PROBE_EXTERNAL))

                        # Sensorstatus bestimmen
                        sensor_ok_main = (t_main is not None and h_main is not None)
                        sensor_ok_ext = (t_ext is not None and h_ext is not None)

                        # Status schreiben (jede Runde)
                        _update_status(True, sensor_ok_main, sensor_ok_ext)

                        # Snapshot-Datei aktualisieren
                        payload = {
                            "timestamp": datetime.datetime.utcnow().isoformat(),
                            "t_main": t_main,
                            "h_main": h_main,
                            "t_ext": t_ext,
                            "h_ext": h_ext,
                        }
                        utils.safe_write_json(resource_path(config.DATA_FILE), payload)

                        # CSV-Logging
                        ts_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        t = payload["t_main"]
                        h = payload["h_main"]
                        vpd = utils.calc_vpd(t, h) if (t is not None and h is not None) else None
                        utils.append_csv_row(
                            resource_path(config.HISTORY_FILE),
                            ["Timestamp", "Temperature", "Humidity", "VPD"],
                            [ts_str, t, h, vpd],
                        )

                    except Exception as e:
                        _log(f"⚠️ Device read error: {type(e).__name__}: {e}")
                        _update_status(True, False, False)

                    await asyncio.sleep(SCAN_INTERVAL)

        except Exception as e:
            _log(f"❌ Bluetooth connection failed: {type(e).__name__}: {e}")
            _update_status(False, False, False)

        if _stop_event.is_set():
            break

        delay = getattr(config, "RECONNECT_DELAY", 10)
        _log(f"🔄 Reconnecting in {delay}s ...")
        await asyncio.sleep(delay)


# -------------------------------------------------------------------
# Thread-Wrapper
# -------------------------------------------------------------------
def start_reader_thread(device_id, log_callback=None):
    global _thread, _running
    if _thread and _thread.is_alive():
        return

    _running = True
    _stop_event.clear()
    _log("🧵 Reader-Thread gestartet")

    def runner():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_read_loop(device_id, log_callback))
        except Exception as e:
            _log(f"❌ Fehler im Reader-Thread: {e}")
            traceback.print_exc()
        finally:
            loop.close()
            _update_status(False, False, False)
            _log("🧹 Reader-Thread beendet.")
            _running = False

    _thread = threading.Thread(target=runner, daemon=True)
    _thread.start()


def stop_reader():
    global _running
    if not _running:
        return
    _log("[🧹] Stoppe Async-Reader …")
    _stop_event.set()
    _running = False
    try:
        _update_status(False, False, False)
    except Exception:
        pass


# -------------------------------------------------------------------
# CLI-Hilfsfunktionen
# -------------------------------------------------------------------
def list_devices():
    cfg = utils.safe_read_json(resource_path(config.CONFIG_FILE)) or {}
    did = cfg.get("device_id")
    return [did] if did else []


def scan_once():
    return utils.safe_read_json(resource_path(config.DATA_FILE))
