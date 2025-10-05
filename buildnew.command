#!/bin/bash
set -e

# Immer im Ordner des Skripts starten
cd "$(dirname "$0")"
echo "📦 Starte Build in $(pwd)"

# 1. Alte venv löschen (falls vorhanden)
if [ -d "venv" ]; then
  echo "⚠️ Entferne alte venv..."
  rm -rf venv
fi

# 2. Neue venv anlegen im Projektordner
python3.12 -m venv venv
source venv/bin/activate

# 3. pip + build tools updaten
pip install --upgrade pip wheel setuptools

# 4. Nur benötigte Dependencies installieren
pip install "matplotlib>=3.7" "numpy>=1.25" pandas pillow vivosun-thermo

# 5. PyInstaller mit main.spec starten
pyinstaller main.spec

# 6. Release-Ordner frisch erstellen
rm -rf release
mkdir -p release

# 7. Build-Ergebnisse reinkopieren
cp -R dist/VIVOSUN_Dashboard.app release/
cp dist/VIVOSUN_Dashboard release/

echo "✅ Build abgeschlossen!"
echo "➡️ App liegt in release/VIVOSUN_Dashboard.app"
echo "➡️ Unix-Binary in release/VIVOSUN_Dashboard"