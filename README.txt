# 🌱 VIVOSUN Thermo Dashboard

Ein modernes Desktop-Dashboard für den **VIVOSUN THB-1S Thermo/Hygro Sensor**, entwickelt von **Dominik Rosenthal**.  
Die App verbindet sich via **Bluetooth**, visualisiert **Temperatur**, **Luftfeuchtigkeit** und **VPD** in Echtzeit und speichert Messwerte automatisch.  

---

## ✨ Features

- 🔍 **Bluetooth-Scan** direkt in der App (kein CLI nötig)  
- 📈 **Live-Charts** für Temperatur, Luftfeuchtigkeit und VPD (intern & extern)  
- 🌡️ **Leaf-Offset & Humidity-Offset** (°C/°F und %) frei einstellbar  
- 🔄 **Auto-Reconnect** bei Verbindungsabbruch  
- 📊 **CSV-Export** im GrowHub-Format  
- 🌱 **VPD Comfort Chart (Scatter)** mit Wachstums-Zonen  
- 🗑️ **Config-Reset** direkt aus dem Dashboard  
- 🔄 **Programm-Neustart** auf Knopfdruck  
- 🖼️ Eigene **Icons & Branding** (kein Python-Ei im Dock 😉)  
- ✅ Getestet & gepackt für **macOS (Python 3.12 + PyInstaller)**  

---

## 🖼️ Screenshots

### 🔧 Setup
![Setup Screenshot](https://raw.githubusercontent.com/Hackintosh1980/Vivosun-Dashboard/main/screenshots/setup.png)

### 📊 Dashboard
![Dashboard Screenshot](https://raw.githubusercontent.com/Hackintosh1980/Vivosun-Dashboard/main/screenshots/dashboard.png)

### 🌱 VPD Scatter
![VPD Scatter Screenshot](https://raw.githubusercontent.com/Hackintosh1980/Vivosun-Dashboard/main/screenshots/vpd_scatter.png)

### 📂 GrowHub CSV Viewer
![GrowHub Screenshot](https://raw.githubusercontent.com/Hackintosh1980/Vivosun-Dashboard/main/screenshots/growhub_csv.png)

---

## 📦 Installation & Build (macOS)

### 🔑 Voraussetzungen
- macOS  
- Python **3.12** installiert  
  - Download: [python.org](https://www.python.org/downloads/macos/)  
  - oder via Homebrew:  
    ```bash
    brew install python@3.12
    ```

---

### 🚀 Build (global)
```bash
chmod +x build_app.sh
./build_app.sh