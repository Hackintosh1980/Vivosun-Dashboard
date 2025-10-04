import json, math, os, csv, sys

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
