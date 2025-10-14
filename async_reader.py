#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
async_reader.py – stabile Version mit getrennter Sensorerkennung
Aktualisiert status.json gemäß:
{
  "connected": bool,
  "sensor_ok_main": bool,
  "sensor_ok_ext": bool,
  "sensor_ok": bool
}
und leert thermo_values.json bei Disconnect.
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
    """Leert thermo_values.json (DATA_FILE)."""
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
    """Schreibt status.json bei jedem Zyklus neu; leert DATA_FILE bei Disconnect."""
    try:
        data = {
            "connected": connected,
            "sensor_ok_main": sensor_ok_main,
            "sensor_ok_ext": sensor_ok_ext,
            # Rückwärtskompatibilität für ältere Module
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
    RECONNECT_DELAY = getattr(config, "RECONNECT_DELAY", 10)

    while _running and not _stop_event.is_set():
        try:
            async with VivosunThermoClient(device_id) as client:
                _log(f"✅ Connected to device {device_id}")
                # Nach Connect sofort Status setzen (auch wenn Sensorwerte noch None sind)
                _update_status(True, False, False)

                while _running and not _stop_event.is_set():
                    try:
                        # --- Sensorwerte lesen ---
                        t_main = sanitize(await client.current_temperature(PROBE_MAIN, UNIT_CELSIUS))
                        h_main = sanitize(await client.current_humidity(PROBE_MAIN))
                        t_ext  = sanitize(await client.current_temperature(PROBE_EXTERNAL, UNIT_CELSIUS))
                        h_ext  = sanitize(await client.current_humidity(PROBE_EXTERNAL))

                        # --- Sensorstatus bestimmen ---
                        sensor_ok_main = (t_main is not None and h_main is not None)
                        sensor_ok_ext  = (t_ext  is not None and h_ext  is not None)

                        # --- Status schreiben (jede Runde) ---
                        _update_status(True, sensor_ok_main, sensor_ok_ext)

                        # --- Snapshot schreiben (auch mit None-Werten, damit GUI korrekt reagiert) ---
                        payload = {
                            "timestamp": datetime.datetime.utcnow().isoformat(),
                            "t_main": t_main,
                            "h_main": h_main,
                            "t_ext":  t_ext,
                            "h_ext":  h_ext,
                        }
                        utils.safe_write_json(resource_path(config.DATA_FILE), payload)

                        # --- CSV-Logging für internen Sensor (falls valide) ---
                        ts_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        vpd = utils.calc_vpd(t_main, h_main) if sensor_ok_main else None
                        utils.append_csv_row(
                            resource_path(config.HISTORY_FILE),
                            ["Timestamp", "Temperature", "Humidity", "VPD"],
                            [ts_str, t_main, h_main, vpd],
                        )

                    except Exception as e:
                        # Jede Lese-Exception betrachten wir als Verbindungsproblem → sauberer Disconnect
                        _log(f"⚠️ Device read error – reconnecting: {type(e).__name__}: {e}")
                        _update_status(False, False, False)  # leert auch DATA_FILE
                        break  # verlässt die innere Schleife → Context schließt → Reconnect

                    await asyncio.sleep(SCAN_INTERVAL)

        except Exception as e:
            # Verbindung konnte nicht aufgebaut/aufrechterhalten werden
            _log(f"❌ Bluetooth connection failed: {type(e).__name__}: {e}")
            _update_status(False, False, False)

        if _stop_event.is_set():
            break

        _log(f"🔄 Reconnecting in {RECONNECT_DELAY}s ...")
        await asyncio.sleep(RECONNECT_DELAY)


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
