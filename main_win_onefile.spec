# -*- mode: python ; coding: utf-8 -*-

import sys, os
sys.path.insert(0, os.path.abspath("."))
import config

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[
        '.',
        os.path.join(os.getcwd(), 'venv', 'Lib', 'site-packages'),
    ],
    binaries=[
        ('C:\\Users\\Dominik\\AppData\\Local\\Programs\\Python\\Python312\\DLLs\\_tkinter.pyd', '.'),
        ('C:\\Users\\Dominik\\AppData\\Local\\Programs\\Python\\Python312\\DLLs\\tcl86t.dll', '.'),
        ('C:\\Users\\Dominik\\AppData\\Local\\Programs\\Python\\Python312\\DLLs\\tk86t.dll', '.'),
    ],
    datas=[
        ('assets/*', 'assets'),
        ('config.json', '.'),
        ('status.json', '.'),
        ('thermo_history.csv', '.'),
    ],
    hiddenimports=[
        "matplotlib.backends.backend_tkagg",
        "matplotlib.pyplot",
        "matplotlib.dates",
        "matplotlib.patheffects",
        "tkinter",
        "numpy",
        "PIL",
        "pandas",
        "vivosun_thermo",
        "footer_widget",
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
    excludes=[
        "matplotlib.tests",
        "mpl_toolkits.tests",
        "tkinter.test",
        "scipy",
        "torch",
    ],
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
    console=False,
    icon='assets/icon.ico',
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