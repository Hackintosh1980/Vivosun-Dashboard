#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
async_reader.py – stabile Version mit automatischem Reconnect bei externem Sensorwechsel.
"""

import asyncio
import datetime
import traceback
import threading
import os
import sys
import time

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

# Wir merken uns den vorherigen Zustand des externen Sensors:
_last_sensor_ok_ext = [False]


# -------------------------------------------------------------------
# Hilfsfunktionen
# -------------------------------------------------------------------
def sanitize(value):
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
        _log("🧹 DATA_FILE geleert (Verbindungsverlust oder Sensor-Wechsel).")
    except Exception as e:
        _log(f"⚠️ DATA_FILE konnte nicht geleert werden: {e}")


def _trigger_chart_reset():
    """Versucht, das Chart-GUI im Hauptprogramm zurückzusetzen."""
    try:
        # 1️⃣ Prüfen, ob ein aktiver Chart-Frame bekannt ist
        import config
        charts_frame = getattr(config, "active_charts_frame", None)

        if charts_frame and hasattr(charts_frame, "reset_charts"):
            charts_frame.reset_charts()
            _log("✅ Chart-Frame über config.reset_charts() zurückgesetzt.")
            return

        # 2️⃣ Falls nicht in config → global gespeicherte Referenz probieren
        import builtins
        charts_frame = getattr(builtins, "_vivosun_chart_frame", None)
        if charts_frame and hasattr(charts_frame, "reset_charts"):
            charts_frame.reset_charts()
            _log("✅ Chart-Frame über builtins._vivosun_chart_frame zurückgesetzt.")
            return

        # 3️⃣ Fallback: Direktes Importieren von charts_gui (wenn geladen)
        try:
            import main_gui.charts_gui as charts_gui
            if hasattr(charts_gui, "data_buffers"):
                for key, buf in charts_gui.data_buffers.items():
                    if isinstance(buf, list):
                        buf.clear()
                if "timestamps" in charts_gui.data_buffers:
                    charts_gui.data_buffers["timestamps"].clear()
                _log("✅ Charts direkt über Datenpuffer geleert (Fallback).")
                return
        except Exception:
            pass

        _log("⚠️ Kein aktiver Chart-Frame (config.active_charts_frame fehlt).")

    except Exception as e:
        _log(f"⚠️ Fehler beim Chart-Reset aus async_reader: {e}")


def _update_status(connected: bool, sensor_ok_main: bool, sensor_ok_ext: bool):
    """Schreibt status.json neu, erkennt externe Sensor-Wechsel und triggert Reconnect."""
    try:
        global _last_sensor_ok_ext

        data = {
            "connected": connected,
            "sensor_ok_main": sensor_ok_main,
            "sensor_ok_ext": sensor_ok_ext,
            "sensor_ok": sensor_ok_main or sensor_ok_ext
        }

        utils.safe_write_json(STATUS_FILE, data)
        _status(connected)

        # 🧹 Bei kompletter Trennung → Daten löschen
        if not connected:
            _clear_data_file()

        # 🔁 Externer Sensor von False → True → Soft-Reconnect
        if sensor_ok_ext and not _last_sensor_ok_ext[0]:
            _log("🔁 Externer Sensor wieder erkannt – Soft-Reconnect & Chart-Reset.")
            _trigger_chart_reset()

        # 🧹 Externer Sensor entfernt → Datenfile leeren
        elif not sensor_ok_ext and _last_sensor_ok_ext[0]:
            _log("🧹 Externer Sensor entfernt – DATA_FILE leeren.")
            _clear_data_file()

        _last_sensor_ok_ext[0] = sensor_ok_ext

    except Exception as e:
        _log(f"⚠️ Fehler im Status-Update: {e}")


# -------------------------------------------------------------------
# Haupt-Async-Loop (mit Sensor-Reset-Erkennung)
# -------------------------------------------------------------------
_sensor_reset_pending = False  # globales Flag außerhalb der Schleifen

async def _read_loop(device_id, log_callback=None):
    from vivosun_thermo import (
        VivosunThermoClient,
        PROBE_MAIN,
        PROBE_EXTERNAL,
        UNIT_CELSIUS,
    )

    SCAN_INTERVAL = getattr(config, "SCAN_INTERVAL", 5)
    RECONNECT_DELAY = getattr(config, "RECONNECT_DELAY", 10)

    last_ext_state = None  # Merkt sich den letzten Sensorstatus

    while _running and not _stop_event.is_set():
        try:
            async with VivosunThermoClient(device_id) as client:
                _log(f"✅ Connected to device {device_id}")
                _update_status(True, False, False)

                while _running and not _stop_event.is_set():
                    try:
                        global _sensor_reset_pending

                        # --- Prüfe, ob Sensor-Reset markiert wurde ---
                        if _sensor_reset_pending:
                            _log("🧹 Sensor-Reset aktiv – DATA_FILE leeren & Charts zurücksetzen …")
                            _clear_data_file()
                            _trigger_chart_reset()
                            _sensor_reset_pending = False
                            await asyncio.sleep(2)
                            continue

                        # --- Sensorwerte lesen ---
                        t_main = sanitize(await client.current_temperature(PROBE_MAIN, UNIT_CELSIUS))
                        h_main = sanitize(await client.current_humidity(PROBE_MAIN))
                        t_ext  = sanitize(await client.current_temperature(PROBE_EXTERNAL, UNIT_CELSIUS))
                        h_ext  = sanitize(await client.current_humidity(PROBE_EXTERNAL))

                        # --- Sensorstatus bestimmen ---
                        sensor_ok_main = (t_main is not None and h_main is not None)
                        sensor_ok_ext  = (t_ext  is not None and h_ext  is not None)

                        # --- Wenn sich der externe Sensorstatus geändert hat ---
                        if last_ext_state is None:
                            last_ext_state = sensor_ok_ext
                        elif last_ext_state != sensor_ok_ext:
                            last_ext_state = sensor_ok_ext
                            _sensor_reset_pending = True
                            if sensor_ok_ext:
                                _log("🔁 Externer Sensor erkannt – Soft-Reconnect & Chart-Reset markiert.")
                            else:
                                _log("🔌 Externer Sensor entfernt – Chart-Reset markiert.")

                        # --- Statusdatei aktualisieren ---
                        _update_status(True, sensor_ok_main, sensor_ok_ext)

                        # --- Daten speichern ---
                        payload = {
                            "timestamp": datetime.datetime.utcnow().isoformat(),
                            "t_main": t_main,
                            "h_main": h_main,
                            "t_ext":  t_ext,
                            "h_ext":  h_ext,
                        }
                        utils.safe_write_json(resource_path(config.DATA_FILE), payload)

                        # --- CSV Logging (optional) ---
                        ts_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        vpd = utils.calc_vpd(t_main, h_main) if sensor_ok_main else None
                        utils.append_csv_row(
                            resource_path(config.HISTORY_FILE),
                            ["Timestamp", "Temperature", "Humidity", "VPD"],
                            [ts_str, t_main, h_main, vpd],
                        )

                    except Exception as e:
                        _log(f"⚠️ Device read error – reconnecting: {type(e).__name__}: {e}")
                        _update_status(False, False, False)
                        break

                    await asyncio.sleep(SCAN_INTERVAL)

        except Exception as e:
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
