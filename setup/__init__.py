#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup – Initialisierung für das VIVOSUN Setup-Modul.
Ermöglicht den einfachen Start per `from setup import run_setup` oder `python3 -m setup`.
"""

from .setup_gui import run_setup

__all__ = ["run_setup"]


if __name__ == "__main__":
    run_setup()
