#!/bin/bash
set -e

# Projektordner ermitteln (dort wo start.command liegt)
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# venv aktivieren
if [ -d "$PROJECT_DIR/venv" ]; then
    source "$PROJECT_DIR/venv/bin/activate"
else
    echo "❌ Fehler: Keine venv gefunden. Bitte zuerst ./setup.command ausführen!"
    exit 1
fi

# Starten
echo "🌱 Starte VIVOSUN Dashboard..."
python3 main.py
