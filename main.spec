# -*- mode: python ; coding: utf-8 -*-

import sys, os
sys.path.insert(0, os.path.abspath("."))   # Projektpfad hinzufügen
import config

block_cipher = None

a = Analysis(
    ['main.py'],                      # Einstiegspunkt
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets/*', 'assets'),        # Icons & PNGs
        ('status.json', '.'),          # Status
        ('thermo_history.csv', '.'),   # Historie
    ],
    hiddenimports=[
        # Matplotlib
        "matplotlib.backends.backend_tkagg",
        "matplotlib.pyplot",
        "matplotlib.dates",
        "matplotlib.patheffects",

        # Tkinter
        "tkinter",

        # Numpy / Pillow
        "numpy",
        "PIL",

        # Pandas für GrowHub CSV
        "pandas",

        # BLE / vivosun
        "vivosun_thermo",

        # interne Module
        "footer_widget",          # 👈 unser neues Modul
        "growhub_csv_viewer",
        "enlarged_charts",
        "scattered_vpd_chart",
        "setup_gui",
        "utils",
        "async_reader",
        "icon_loader",
        "config",
        "gui",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        "matplotlib.tests",
        "mpl_toolkits.tests",
        "tkinter.test",
        "scipy",
        "torch",  # YOLO ausschließen
    ],
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
    name='VIVOSUN_Dashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,   # Terminal-Fenster? False = App-only
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='VIVOSUN_Dashboard'
)

app = BUNDLE(
    coll,
    name='VIVOSUN_Dashboard.app',
    icon='assets/logo.icns',
    bundle_identifier='com.cueva.vivosun',
    info_plist={
        "CFBundleName": config.APP_NAME,
        "CFBundleDisplayName": config.APP_NAME,
        "CFBundleGetInfoString": f"{config.APP_NAME} by {config.APP_AUTHOR}",
        "CFBundleShortVersionString": config.APP_VERSION,
        "CFBundleVersion": config.APP_VERSION,
        "NSHumanReadableCopyright": f"© 2025 {config.APP_AUTHOR}",
        "NSHighResolutionCapable": True,
        "LSMultipleInstancesProhibited": True,
        "LSUIElement": False,
    },
)