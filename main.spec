# -*- mode: python ; coding: utf-8 -*-
"""
main.spec – Build-Konfiguration für VIVOSUN Dashboard
Projektstruktur:
  vivosun/
    ├── main.py
    ├── assets/
    ├── widgets/
    ├── main_gui/
    ├── data/
    └── themes/
"""

import glob
import os
from PyInstaller.utils.hooks import collect_data_files

# Projektpfad (funktioniert auch ohne __file__)
try:
    project_root = os.path.abspath(os.path.dirname(__file__))
except NameError:
    project_root = os.getcwd()

src_dir = project_root  # direkt der vivosun-Ordner

# --- Hilfsfunktion: rekursiv alle Dateien in Unterordnern einbinden ---
def recursive_datas(src_folder, target_folder):
    files = []
    if os.path.exists(src_folder):
        for path in glob.glob(os.path.join(src_folder, "**"), recursive=True):
            if os.path.isfile(path):
                rel_path = os.path.relpath(os.path.dirname(path), src_dir)
                files.append((path, rel_path))
    return files

# --- Alle Ressourcen automatisch einsammeln ---
datas = []
datas += recursive_datas(os.path.join(src_dir, "assets"), "assets")
datas += recursive_datas(os.path.join(src_dir, "widgets"), "widgets")
datas += recursive_datas(os.path.join(src_dir, "themes"), "themes")
datas += recursive_datas(os.path.join(src_dir, "main_gui"), "main_gui")
datas += recursive_datas(os.path.join(src_dir, "data"), "data")

# Zusätzliche Paketdaten (z. B. Matplotlib, PIL, Fonts)
datas += collect_data_files("matplotlib", include_py_files=True)
datas += collect_data_files("PIL", include_py_files=True)

block_cipher = None

a = Analysis(
    [os.path.join(src_dir, "main.py")],
    pathex=[src_dir],
    binaries=[],
    datas=datas,
    hiddenimports=[
        "tkinter",
        "matplotlib",
        "PIL",
        "numpy",
        "json",
        "datetime",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="VIVOSUN_Dashboard",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # False = keine Terminalausgabe
    icon=os.path.join(src_dir, "assets", "Icon.ico") if os.path.exists(os.path.join(src_dir, "assets", "Icon.ico")) else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="VIVOSUN_Dashboard",
)
app = BUNDLE(
    coll,
    name='VIVOSUN_Dashboard.app',
    icon=os.path.join(src_dir, "assets", "Icon.icns"),
    bundle_identifier='com.vivosun.dashboard',
)