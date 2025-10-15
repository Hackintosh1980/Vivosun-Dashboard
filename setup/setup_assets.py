#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_assets.py – zentraler Zugriff auf Setup-Assets (Icons, Logos usw.)
"""

import os

def get_asset_path(filename: str) -> str:
    """
    Gibt den absoluten Pfad zu einer Datei im globalen 'assets'-Ordner zurück.
    Beispiel: get_asset_path("setup.png")
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))  # -> /Users/.../vivosun
    asset_dir = os.path.join(base_dir, "assets")
    return os.path.join(asset_dir, filename)
