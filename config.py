import os

# --- App Infos ---
APP_NAME = "VIVOSUN Thermo Dashboard"       # Klarer Name für macOS / Info.plist
APP_DISPLAY = "🌱 VIVOSUN Thermo Dashboard" # Mit Emoji für GUI / Titlebars
APP_VERSION = "1.2.2"
APP_AUTHOR = "Dominik Rosenthal"
APP_COPYRIGHT = f"© 2025 {APP_AUTHOR}"
APP_GITHUB = "https://github.com/sormy/vivosun-thermo"

# Base paths
BASE_DIR = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
DATA_FILE = os.path.join(BASE_DIR, "thermo_values.json")
HISTORY_FILE = os.path.join(BASE_DIR, "thermo_history.csv")  # CSV-Logdatei

# UI Farben
BG = "#0b1620"
CARD = "#0f1e2a"
TEXT = "#d6eaff"
ACCENT = "#8be9fd"

# Timing
UI_POLL_INTERVAL = 2.0   # seconds (GUI Refresh)
PLOT_BUFFER_LEN = 600    # ~10 minutes @ 1s

# Reader Polling
SCAN_INTERVAL = 2        # Sekunden zwischen Messungen

# Offsets (global)
leaf_offset_c = [0.0]       # Leaf Temp Offset in °C
humidity_offset = [0.0]     # Humidity Offset in %

# Reconnect-Verhalten
RECONNECT_DELAY = 1   # Sekunden zwischen den Reconnect-Versuchen
