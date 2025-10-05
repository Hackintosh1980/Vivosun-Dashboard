#!/bin/bash
set -e

echo "🚀 Starte Build-Prozess für VIVOSUN Dashboard (macOS, mit venv im Projekt-Root)"

# 1. Ins Projekt-Root wechseln (wo das Script liegt)
cd "$(dirname "$0")"

# 2. Prüfen ob Python 3.12 installiert ist
if ! command -v python3.12 &> /dev/null
then
    echo "❌ Python 3.12 nicht gefunden!"
    echo "   Bitte zuerst installieren: https://www.python.org/downloads/macos/"
    exit 1
fi

# 3. Virtuelle Umgebung erstellen, falls nicht vorhanden
if [ ! -d "venv" ]; then
    echo "📦 Erstelle virtuelle Umgebung..."
    python3.12 -m venv venv
fi

# 4. Aktivieren der venv
source venv/bin/activate

# 5. Abhängigkeiten installieren
echo "📥 Installiere Dependencies in venv..."
pip install --upgrade pip setuptools wheel
pip install pyinstaller pillow matplotlib numpy pyobjc-framework-Cocoa vivosun-thermo pandas

# 6. App bauen
echo "🏗  Baue App mit PyInstaller..."
pyinstaller main.spec

# 7. Ergebnis
echo "✅ Build abgeschlossen!"
echo "👉 Fertige App im dist/ Ordner: dist/VIVOSUN_Dashboard.app"