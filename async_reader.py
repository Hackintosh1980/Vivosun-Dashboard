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
STATUS_FILE = resource_path(getattr(config, "STATUS_FILE", "status.json"))


# -------------------------------------------------------------------
# Logging-Schutz
# -------------------------------------------------------------------
def _safe_log(callback, msg):
    """Ruft log_callback sicher auf (ignoriert zerstörte GUI oder Tk-Fehler)."""
    if not callable(callback):
        return
    try:
        callback(msg)
    except Exception:
        # Wenn das Fenster zerstört ist, einfach still abbrechen
        pass


# -------------------------------------------------------------------
# Hilfsfunktion: Fake-Werte erkennen
# -------------------------------------------------------------------
def sanitize(value):
    """Filtert unplausible Werte wie 0.0–0.2 (Sensor getrennt)."""
    if value is None:
        return None
    try:
        v = float(value)
        if 0.0 <= v <= 0.2:  # typische "Ghost"-Werte
            return None
        return v
    except Exception:
        return None


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

    while _running:
        try:
            async with VivosunThermoClient(device_id) as client:
                _safe_log(log_callback, f"✅ Connected to device {device_id}")
                utils.safe_write_json(STATUS_FILE, {"connected": True, "sensor_ok": True})

                while _running:
                    try:
                        # --- Messwerte holen ---
                        t_main = sanitize(await client.current_temperature(PROBE_MAIN, UNIT_CELSIUS))
                        h_main = sanitize(await client.current_humidity(PROBE_MAIN))
                        t_ext  = sanitize(await client.current_temperature(PROBE_EXTERNAL, UNIT_CELSIUS))
                        h_ext  = sanitize(await client.current_humidity(PROBE_EXTERNAL))

                        # --- Sensorstatus prüfen ---
                        sensor_ok = not all(v is None for v in [t_main, h_main, t_ext, h_ext])
                        if not sensor_ok:
                            _safe_log(log_callback, "⚠️ Sensor not connected or invalid readings (0.0–0.2)")
                            utils.safe_write_json(STATUS_FILE, {"connected": True, "sensor_ok": False})
                            # Dummy-Snapshot schreiben
                            utils.safe_write_json(resource_path(config.DATA_FILE), {
                                "timestamp": datetime.datetime.utcnow().isoformat(),
                                "t_main": None,
                                "h_main": None,
                                "t_ext": None,
                                "h_ext": None,
                            })
                            await asyncio.sleep(getattr(config, "SCAN_INTERVAL", 5))
                            continue

                        # --- Payload normal ---
                        ts = datetime.datetime.utcnow().isoformat()
                        payload = {
                            "timestamp": ts,
                            "t_main": t_main,
                            "h_main": h_main,
                            "t_ext": t_ext,
                            "h_ext": h_ext,
                        }

                        # --- JSON Snapshot ---
                        try:
                            utils.safe_write_json(resource_path(config.DATA_FILE), payload)
                        except Exception as e:
                            _safe_log(log_callback, f"⚠️ Snapshot write failed: {e}")

                        # --- CSV Logging (GrowHub kompatibel) ---
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

                        # --- Status als aktiv und Sensor OK ---
                        utils.safe_write_json(STATUS_FILE, {"connected": True, "sensor_ok": True})

                    except Exception as e:
                        _safe_log(log_callback, f"⚠️ Device read error → reconnecting: {e}\n{traceback.format_exc()}")
                        utils.safe_write_json(STATUS_FILE, {"connected": False, "sensor_ok": False})
                        break

                    await asyncio.sleep(getattr(config, "SCAN_INTERVAL", 5))

        except Exception as e:
            _safe_log(log_callback, f"❌ Could not connect: {e}\n{traceback.format_exc()}")
            utils.safe_write_json(STATUS_FILE, {"connected": False, "sensor_ok": False})

        # --- Reconnect-Delay ---
        delay = getattr(config, "RECONNECT_DELAY", 10)
        _safe_log(log_callback, f"🔄 Reconnecting in {delay}s ...")
        await asyncio.sleep(delay)


# -------------------------------------------------------------------
# Thread-Wrapper
# -------------------------------------------------------------------
def start_reader_thread(device_id, log_callback=None):
    """Startet den Background Reader in eigenem Thread."""
    global _thread, _running
    if _thread and _thread.is_alive():
        return
    _running = True

    def runner():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_read_loop(device_id, log_callback))
        finally:
            loop.close()

    _thread = threading.Thread(target=runner, daemon=True)
    _thread.start()


def stop_reader():
    """Beendet den Reader-Loop."""
    global _running
    _running = False
    try:
        utils.safe_write_json(STATUS_FILE, {"connected": False, "sensor_ok": False})
    except Exception:
        pass


# -------------------------------------------------------------------
# CLI-Hilfsfunktionen
# -------------------------------------------------------------------
def list_devices():
    """Device-ID aus config.json zurückgeben (CLI-Kompatibilität)."""
    cfg = utils.safe_read_json(resource_path(config.CONFIG_FILE)) or {}
    did = cfg.get("device_id")
    return [did] if did else []


def scan_once():
    """Letzten Snapshot aus DATA_FILE zurückgeben."""
    return utils.safe_read_json(resource_path(config.DATA_FILE))
