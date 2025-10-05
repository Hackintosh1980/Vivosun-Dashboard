#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test für VivosunThermoScanner.discover()
"""

import asyncio
from vivosun_thermo import VivosunThermoScanner

async def main():
    print("🔍 Scanning for devices (60s)...")
    scanner = VivosunThermoScanner()
    devices = await scanner.discover(timeout=60)   # 60 Sekunden Scan
    if not devices:
        print("⚠️ Keine Geräte gefunden.")
    else:
        for d in devices:
            print("✅ Found device:", d)

if __name__ == "__main__":
    asyncio.run(main())
