#!/bin/bash
set -e

# Projektordner merken
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"

# venv-Ordner anlegen, falls noch nicht vorhanden
if [ ! -d "$PROJECT_DIR/venv" ]; then
    echo "🚀 Erstelle virtuelle Umgebung..."
    python3.12 -m venv "$PROJECT_DIR/venv"
else
    echo "✅ Virtuelle Umgebung existiert bereits."
fi

# Aktivieren
source "$PROJECT_DIR/venv/bin/activate"

# Abhängigkeiten installieren
echo "📦 Installiere Abhängigkeiten..."
pip install --upgrade pip setuptools wheel
pip install -r "$PROJECT_DIR/requirements.txt"

echo "🎉 Setup abgeschlossen! Starte die App jetzt mit ./start.command"
