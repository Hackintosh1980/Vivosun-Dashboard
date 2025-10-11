#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
async_reader.py – Hintergrund-Reader für VIVOSUN Thermo (THB-1S)
Liest Werte über vivosun_thermo, schreibt Snapshots + CSV
und hält status.json mit {"connected": bool, "sensor_ok": bool} aktuell.
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
# Helper: Safe path resolver (funktioniert auch in PyInstaller)
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
def _safe_log(callback, msg):
    if not callable(callback):
        return
    try:
        callback(msg)
    except Exception:
        pass


def sanitize(value):
    """Filtert unplausible Sensorwerte heraus (z. B. -0.06 °C / % = kein Signal)."""
    if value is None:
        return None
    try:
        v = float(value)
        # ⚙️ Neue Logik: erkennt negative Nullwerte wie -0.06
        if -0.1 <= v <= 0.0:
            _safe_log(_log_callback, f"⚠️ Sensor liefert negativen Nullwert ({v:.2f}) → ignoriert")
            return None
        return v
    except Exception:
        return None

def _update_status(connected: bool, sensor_ok: bool):
    """Schreibt status.json nur, wenn sich der Zustand wirklich geändert hat."""
    try:
        old = utils.safe_read_json(STATUS_FILE) or {}
        if old.get("connected") == connected and old.get("sensor_ok") == sensor_ok:
            return
        utils.safe_write_json(STATUS_FILE, {"connected": connected, "sensor_ok": sensor_ok})
        _status(connected)
    except Exception:
        pass


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

    while _running and not _stop_event.is_set():
        try:
            async with VivosunThermoClient(device_id) as client:
                _safe_log(log_callback, f"✅ Connected to device {device_id}")
                _log(f"✅ Connected to device {device_id}")
                _update_status(True, True)

                while _running and not _stop_event.is_set():
                    try:
                        t_main = sanitize(await client.current_temperature(PROBE_MAIN, UNIT_CELSIUS))
                        h_main = sanitize(await client.current_humidity(PROBE_MAIN))
                        t_ext = sanitize(await client.current_temperature(PROBE_EXTERNAL, UNIT_CELSIUS))
                        h_ext = sanitize(await client.current_humidity(PROBE_EXTERNAL))

                        sensor_ok = not all(v is None for v in [t_main, h_main, t_ext, h_ext])
                        if not sensor_ok:
                            _safe_log(log_callback, "⚠️ Sensor not connected or invalid readings (0.0–0.2)")
                            _log("⚠️ Sensor not connected or invalid readings (0.0–0.2)")
                            _update_status(True, False)
                            utils.safe_write_json(resource_path(config.DATA_FILE), {
                                "timestamp": datetime.datetime.utcnow().isoformat(),
                                "t_main": None,
                                "h_main": None,
                                "t_ext": None,
                                "h_ext": None,
                            })
                            await asyncio.sleep(getattr(config, "SCAN_INTERVAL", 5))
                            continue

                        ts = datetime.datetime.utcnow().isoformat()
                        payload = {
                            "timestamp": ts,
                            "t_main": t_main,
                            "h_main": h_main,
                            "t_ext": t_ext,
                            "h_ext": h_ext,
                        }

                        try:
                            utils.safe_write_json(resource_path(config.DATA_FILE), payload)
                        except Exception as e:
                            _safe_log(log_callback, f"⚠️ Snapshot write failed: {e}")
                            _log(f"⚠️ Snapshot write failed: {e}")

                        try:
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
                            _safe_log(log_callback, f"⚠️ Append CSV failed: {e}")
                            _log(f"⚠️ Append CSV failed: {e}")

                        _update_status(True, True)

                    except Exception as e:
                        msg = f"⚠️ Device read error – reconnecting: {type(e).__name__}: {e}"
                        _safe_log(log_callback, msg)
                        _log(msg)
                        _update_status(False, False)
                        break

                    await asyncio.sleep(getattr(config, "SCAN_INTERVAL", 5))

        except Exception as e:
            msg = f"❌ Bluetooth connection failed ({type(e).__name__}): {e}"
            _safe_log(log_callback, msg)
            _log(msg)
            _update_status(False, False)

        if _stop_event.is_set():
            break

        delay = getattr(config, "RECONNECT_DELAY", 15)
        _safe_log(log_callback, f"🔄 Reconnecting in {delay}s ...")
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
            _update_status(False, False)
            _safe_log(log_callback, "🧹 Reader-Thread beendet.")
            _running = False

    _thread = threading.Thread(target=runner, daemon=True)
    _thread.start()


def stop_reader():
    global _running
    if not _running:
        return
    _safe_log(print, "[🧹] Stoppe Async-Reader …")
    _stop_event.set()
    _running = False
    try:
        _update_status(False, False)
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
