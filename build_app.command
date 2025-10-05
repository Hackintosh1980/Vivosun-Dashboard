#!/bin/bash
set -e

echo "🚀 Starte Build-Prozess für VIVOSUN Dashboard (macOS, Python 3.12 global)"

# 1. Ins Projekt-Root wechseln (dort wo das Script liegt)
cd "$(dirname "$0")"

# 2. Prüfen ob Python 3.12 installiert ist
if ! command -v python3.12 &> /dev/null
then
    echo "❌ Python 3.12 nicht gefunden!"
    echo "   Bitte zuerst installieren: https://www.python.org/downloads/macos/"
    exit 1
fi

# 3. Prüfen ob main.spec existiert
if [ ! -f "main.spec" ]; then
    echo "❌ main.spec nicht gefunden im Projekt-Root!"
    exit 1
fi

# 4. Dependencies installieren (global)
echo "📥 Installiere Dependencies..."
pip3.12 install --upgrade pip setuptools wheel
pip3.12 install pyinstaller pillow matplotlib numpy pyobjc-framework-Cocoa

# 5. App bauen
echo "🏗  Baue App mit PyInstaller..."
pyinstaller main.spec

# 6. Ergebnis
echo "✅ Build abgeschlossen!"
echo "👉 Fertige App im dist/ Ordner: dist/VIVOSUN_Dashboard.app"