#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_layout.py – 🌱 VIVOSUN Setup Layout
Erzeugt das Setup-Fenster mit EINEM Theme-Picker und funktionierendem Scan-Stopp.
"""

import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import queue
import threading
import asyncio
import re

from setup import setup_logic, setup_assets


def build_gui(root, theme):
    """Erstellt das Setup-Fenster nach dem aktuellen Theme."""
    from main_gui import theme_picker

    # ============================================================
    # TOPBAR – nur ein Theme-Picker!
    # ============================================================
    for child in root.winfo_children():
        child.destroy()

    topbar = tk.Frame(root, bg=theme.CARD_BG)
    topbar.pack(fill="x", pady=(8, 10))

    tk.Label(
        topbar,
        text="🎨 Theme:",
        bg=theme.CARD_BG,
        fg=theme.TEXT_DIM,
        font=theme.FONT_LABEL
    ).pack(side="left", padx=(12, 6))

    theme_name = setup_logic.load_theme_from_config()
    theme_var = tk.StringVar(value=theme_name)

    def on_theme_change(new_name):
        new_theme = theme_picker.get_available_themes().get(new_name)
        if new_theme:
            theme_picker.save_theme_to_config(new_name)
            build_gui(root, new_theme)

    theme_dropdown, _ = theme_picker.create_theme_picker(
        topbar,
        current_theme=theme_name,
        on_change=on_theme_change
    )
    theme_dropdown.pack(side="left", padx=(0, 12))

    # ============================================================
    # HEADER
    # ============================================================
    header = theme.make_frame(root, bg=theme.CARD_BG)
    header.pack(fill="x", pady=(0, 10))

    tk.Label(
        header,
        text="🌱 VIVOSUN Thermo Setup",
        bg=theme.CARD_BG,
        fg=getattr(theme, "LIME", theme.AQUA),
        font=theme.FONT_TITLE
    ).pack(pady=(10, 4))

    logo_path = setup_assets.get_asset_path("setup.png")
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path).resize((380, 120), Image.LANCZOS)
            logo = ImageTk.PhotoImage(img)
            logo_label = tk.Label(header, image=logo, bg=theme.CARD_BG)
            logo_label.image = logo
            logo_label.pack(pady=(5, 5))
        except Exception:
            pass

    # ============================================================
    # TEXT OUTPUT
    # ============================================================
    text = tk.Text(
        root, width=68, height=10,
        bg=theme.CARD_BG, fg=theme.TEXT_DIM,
        font=("Consolas", 9),
        relief="flat",
        insertbackground=theme.BTN_PRIMARY
    )
    text.pack(padx=12, pady=10)

    # ============================================================
    # DEVICE LIST
    # ============================================================
    list_frame = theme.make_frame(root, bg=theme.CARD_BG)
    list_frame.pack(fill="x", padx=12, pady=(0, 10))

    device_listbox = tk.Listbox(
        list_frame,
        bg=theme.CARD_BG,
        fg=theme.TEXT,
        selectbackground=theme.BTN_PRIMARY,
        selectforeground="black",
        font=("Segoe UI", 13, "bold"),
        height=6,
        relief="flat",
        highlightbackground=theme.BORDER,
        highlightthickness=1
    )
    device_listbox.pack(fill="x", padx=8, pady=6)

    # ============================================================
    # PROGRESS BAR
    # ============================================================
    progress_frame = theme.make_frame(root, bg=theme.CARD_BG)
    progress_frame.pack(fill="x", pady=8)

    style = ttk.Style()
    style.configure("Pulse.Horizontal.TProgressbar",
                    troughcolor=theme.CARD_BG,
                    background=theme.BTN_PRIMARY,
                    lightcolor=theme.BTN_HOVER,
                    darkcolor=theme.BORDER,
                    thickness=14)

    progress = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate",
                               length=400, style="Pulse.Horizontal.TProgressbar", maximum=100)
    progress.pack(padx=12, pady=4)

    # ============================================================
    # SCAN UND SAVE
    # ============================================================
    result_queue = queue.Queue()
    devices = []
    pulse_running = False

    def start_pulse():
        nonlocal pulse_running
        pulse_running = True
        progress["value"] = 0
        animate_pulse()

    def stop_pulse():
        nonlocal pulse_running
        pulse_running = False
        progress["value"] = 0

    def animate_pulse():
        if not pulse_running:
            return
        progress.step(5)
        root.after(80, animate_pulse)

    def add_device(device_id, name):
        device_listbox.insert(tk.END, f"⚪ {device_id}  |  {name}")

    def finish_scan(output):
        stop_pulse()
        setup_logic.finish_scan_output(output, text, device_listbox, devices, add_device)
        scan_btn.config(state="normal")

    def poll_queue():
        try:
            while True:
                output = result_queue.get_nowait()
                finish_scan(output)
        except queue.Empty:
            pass
        root.after(300, poll_queue)

    def scan_devices():
        scan_btn.config(state="disabled")
        start_pulse()
        # Starte Scan mit Timeout
        threading.Thread(
            target=lambda: setup_logic.start_device_scan(text, result_queue, scan_btn, start_pulse, timeout=10),
            daemon=True
        ).start()

    def save_selected():
        setup_logic.save_selected_device(device_listbox, text, theme_var, root)

    button_frame = theme.make_frame(root, bg=theme.CARD_BG)
    button_frame.pack(pady=6)

    scan_btn = theme.make_button(button_frame, "🔍 Scan Devices", scan_devices, color=theme.BTN_PRIMARY)
    scan_btn.pack(side="left", padx=8)

    theme.make_button(button_frame, "💾 Save Selected", save_selected, color=theme.BTN_SECONDARY)\
        .pack(side="left", padx=8)

    # ============================================================
    # FOOTER
    # ============================================================
    footer = theme.make_frame(root, bg=theme.CARD_BG)
    footer.pack(side="bottom", fill="x", pady=6)

    tk.Label(footer,
             text=f"{theme_var.get()} • VIVOSUN Setup Tool v2.8",
             bg=theme.CARD_BG, fg=theme.TEXT_DIM,
             font=theme.FONT_LABEL).pack(side="right", padx=10)

    poll_queue()
