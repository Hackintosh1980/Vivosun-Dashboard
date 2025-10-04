# 🌱 VIVOSUN Thermo Dashboard

Ein Desktop-Dashboard für den **VIVOSUN THB-1S Thermo/Hygrometer**, entwickelt von Dominik Rosenthal.  
Die App verbindet sich via Bluetooth, visualisiert Temperatur, Luftfeuchtigkeit & VPD in Echtzeit und speichert Messwerte.

---

## ✨ Features

- 🔍 Geräte-Scan direkt in der GUI  
- 📈 Live-Charts (intern & extern) für Temperatur, Luftfeuchtigkeit & VPD  
- 🌡️ Leaf-Offset & Humidity-Offset einstellbar  
- 🔄 Auto-Reconnect bei Verbindungsabbruch  
- 📊 Export & Historie im GrowHub-kompatiblen CSV  
- 🖼️ VPD Scatter-Chart mit Komfortzonen  
- 🗑️ Config-Löschen / Neustart-Funktion  
- ✅ Getestet & gepackt für macOS via Python 3.12 + PyInstaller  

---

## 🖼️ Screenshots

*(Die Screenshots liegen im Ordner `screenshots/` im Repo.)*

### Setup
![Setup Screenshot](screenshots/setup.png)

### Dashboard
![Dashboard Screenshot](screenshots/dashboard.png)

### VPD Scatter
![VPD Scatter Screenshot](screenshots/vpd_scatter.png)

### GrowHub CSV Ansicht
![GrowHub CSV Screenshot](screenshots/growhub_csv.png)

---

## 📦 Installation & Build (macOS)

### Voraussetzungen

- macOS  
- Python **3.12** installiert  

---

### Build (global)

```bash
chmod +x build_app.sh
./build_app.sh