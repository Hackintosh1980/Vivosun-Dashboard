#!/bin/bash
set -e

# Immer in den Ordner wechseln, in dem build.sh liegt
cd "$(dirname "$0")"
echo "📦 Starte Build in $(pwd)"

# 1. Falls alte venv existiert → löschen
if [ -d "venv" ]; then
  echo "⚠️ Entferne alte venv..."
  rm -rf venv
fi

# 2. Neue venv anlegen im aktuellen Ordner
python3.12 -m venv venv
source venv/bin/activate

# 3. pip + build tools updaten
pip install --upgrade pip wheel setuptools

# 4. Dependencies installieren
pip install matplotlib>=3.7 numpy>=1.25 pandas pillow vivosun-thermo

# 5. PyInstaller mit main.spec starten
pyinstaller main.spec

# 6. Release-Ordner neu erstellen und App/Binary reinkopieren
rm -rf release
mkdir -p release
cp -R dist/VIVOSUN_Dashboard.app release/
cp dist/VIVOSUN_Dashboard release/

echo "✅ Build abgeschlossen!"
echo "➡️ App liegt in release/VIVOSUN_Dashboard.app"
echo "➡️ Unix-Binary in release/VIVOSUN_Dashboard"