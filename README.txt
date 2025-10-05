# 🌱 VIVOSUN Thermo Dashboard

Ein elegantes Desktop-Dashboard für den **VIVOSUN THB-1S Thermo/Hygro Sensor**.  
Entwickelt von **Dominik Rosenthal** für alle, die ihre Grow-Umgebung übersichtlich und in Echtzeit überwachen möchten.  

Die App verbindet sich via **Bluetooth** mit deinem Sensor, zeigt dir **Temperatur, Luftfeuchtigkeit und VPD** in klaren Charts und speichert alle Werte automatisch.

---

## ✨ Funktionen

- 🔍 **Bluetooth-Gerätescan** direkt in der App – kein Terminal nötig  
- 📊 **Live-Diagramme** für Temperatur, Luftfeuchtigkeit und VPD (intern & extern)  
- 🌡️ **Leaf & Humidity Offsets** individuell einstellbar (°C / °F, %)  
- 🔄 **Automatischer Reconnect** bei Verbindungsproblemen  
- 💾 **CSV-Logging** kompatibel zum GrowHub-Format  
- 🌱 **VPD Comfort Chart** mit optimalen Wachstumszonen  
- 🗑️ **Config zurücksetzen** jederzeit möglich  
- 🔄 **Programm-Neustart** direkt aus der GUI  
- 🖼️ Eigene **Icons & Branding** – kein Python-Ei mehr im Dock 😉  
- ✅ Getestet & gebündelt für **macOS (Python 3.12, PyInstaller)**  

---

## 🖼️ Screenshots

### Setup
![Setup Screenshot](https://raw.githubusercontent.com/Hackintosh1980/Vivosun-Dashboard/main/screenshots/setup.png)

### Dashboard
![Dashboard Screenshot](https://raw.githubusercontent.com/Hackintosh1980/Vivosun-Dashboard/main/screenshots/dashboard.png)

### VPD Scatter
![VPD Scatter Screenshot](https://raw.githubusercontent.com/Hackintosh1980/Vivosun-Dashboard/main/screenshots/vpd_scatter.png)

### GrowHub CSV Viewer
![GrowHub Screenshot](https://raw.githubusercontent.com/Hackintosh1980/Vivosun-Dashboard/main/screenshots/growhub_csv.png)

---

## 🚀 Installation & Build (macOS)

### Voraussetzungen
- macOS  
- Python **3.12** installiert  
  - [Download von python.org](https://www.python.org/downloads/macos/)  
  - oder über Homebrew:  
    ```bash
    brew install python@3.12
    ```

---

### Build (global)
```bash
chmod +x build_app.sh
./build_app.sh
Build (mit venv, empfohlen)
bash
Code kopieren
chmod +x build_app_venv.sh
./build_app_venv.sh
➡️ Die fertige App findest du unter:

Code kopieren
dist/VIVOSUN_Dashboard.app
⚙️ Nutzung & Konfiguration
Beim ersten Start öffnet sich das Setup-Fenster:

App sucht automatisch nach Bluetooth-Geräten

Du wählst dein Gerät und Einheit (°C / °F)

Einstellungen werden in config.json gespeichert

Danach startet sofort das Dashboard

👉 Wenn du config.json löscht, beginnt die App wieder mit dem Setup.

🧑‍💻 Projektinfos
Autor: Dominik Rosenthal

Version: 1.2.2

Repository: Hackintosh1980/Vivosun-Dashboard

Lizenz: (z. B. MIT – frei wählbar)

🌍 Entwickelt mit ❤️ in Andalucía