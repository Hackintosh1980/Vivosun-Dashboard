import json, math, os, csv, sys
try:
    import tkinter as tk
except Exception:
    tk = None  # Fallback für CLI oder frühe Imports

import config
# ---------- Path Helper ----------
def resource_path(relative_path: str) -> str:
    """
    Gibt absoluten Pfad zurück, auch im PyInstaller-Bundle.
    """
    if hasattr(sys, "_MEIPASS"):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ---------- JSON Helpers ----------
def safe_read_json(path):
    try:
        full_path = resource_path(path)
        with open(full_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def safe_write_json(path, obj):
    full_path = resource_path(path)
    tmp = full_path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f)
    os.replace(tmp, full_path)


# ---------- Conversion Helpers ----------
def c_to_f(c):
    return c * 9.0 / 5.0 + 32.0


# ---------- VPD Helper ----------
def calc_vpd(temp_c, rh):
    if temp_c is None or rh is None:
        return None
    # saturation vapor pressure in kPa (Tetens-Formel)
    svp = 0.6108 * math.exp((17.27 * temp_c) / (temp_c + 237.3))
    vpd = svp * (1.0 - (rh / 100.0))
    return round(vpd, 3)


# ---------- CSV Helper ----------
def append_csv_row(path, header, row):
    """
    Hängt eine Zeile an CSV-Datei an.
    Falls Datei nicht existiert → Header schreiben.
    """
    try:
        full_path = resource_path(path)
        file_exists = os.path.exists(full_path)
        with open(full_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(header)
            writer.writerow(row)
    except Exception as e:
        raise RuntimeError(f"CSV append failed for {path}: {e}")

# ===============================================================
# 🔧 Offset-Synchronisation (global für Widgets & Dashboard)
# ===============================================================
import tkinter as tk
import config


def sync_offsets_to_gui():
    """Aktualisiert GUI-Spinboxen basierend auf config-Werten."""
    try:
        cfg = safe_read_json(config.CONFIG_FILE) or {}
        use_celsius = cfg.get("unit_celsius", True)

        # Falls Header oder Widgets Variablen exportieren
        from main_gui import header_gui
        leaf_offset_var = getattr(header_gui, "leaf_offset_var", None)
        hum_offset_var = getattr(header_gui, "hum_offset_var", None)

        if isinstance(leaf_offset_var, tk.DoubleVar):
            val_c = float(config.leaf_offset_c[0])
            display_val = val_c if use_celsius else val_c * 9.0 / 5.0
            leaf_offset_var.set(round(display_val, 2))

        if isinstance(hum_offset_var, tk.DoubleVar):
            hum_offset_var.set(float(config.humidity_offset[0]))

    except Exception as e:
        print(f"⚠️ utils.sync_offsets_to_gui Fehler: {e}")


def set_offsets_from_outside(leaf=None, hum=None, persist=True):
    """Wird von Widgets genutzt, um globale Offsets zu aktualisieren."""
    try:
        cfg = safe_read_json(config.CONFIG_FILE) or {}

        if leaf is not None:
            config.leaf_offset_c[0] = float(leaf)
        if hum is not None:
            config.humidity_offset[0] = float(hum)

        if persist:
            cfg["leaf_offset"] = config.leaf_offset_c[0]
            cfg["humidity_offset"] = config.humidity_offset[0]
            safe_write_json(config.CONFIG_FILE, cfg)

        # GUI aktualisieren
        sync_offsets_to_gui()

    except Exception as e:
        print(f"⚠️ utils.set_offsets_from_outside Fehler: {e}")
