#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_ui.py – 🌱 VIVOSUN Setup (Release v3.0)
Klares, modernes Layout mit Theme-Picker, Status-Ausgabe, Device-Scan und Save-Funktion.
Einheitliches Design, rechtsbündige Buttons & Compact-Mode-Support.
"""

import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from setup import setup_logic, setup_assets
from main_gui.theme_picker import create_theme_picker
import config

def build_gui(root, theme):
    """Erstellt das komplette Setup-Fenster."""
    # ===================== FRAME CLEANUP =====================
    for child in root.winfo_children():
        child.destroy()

    # Compact Mode Layoutgrößen
    if getattr(config, "COMPACT_MODE", False):
        root.geometry("980x720")
    else:
        root.geometry("1180x840")

    root.configure(bg=theme.BG_MAIN)

    # ===================== TOPBAR =====================
    topbar = tk.Frame(root, bg=theme.CARD_BG)
    topbar.pack(fill="x", pady=(10, 12))

    # Theme Picker
    tk.Label(
        topbar, text="🎨 Theme:",
        bg=theme.CARD_BG, fg=theme.TEXT_DIM,
        font=theme.FONT_LABEL
    ).pack(side="left", padx=(12, 8))

    def _on_theme_change(new_theme_name):
        new_theme = setup_logic.get_theme_by_name(new_theme_name)
        setup_logic.save_theme_to_config(new_theme_name)
        build_gui(root, new_theme)

    theme_name = setup_logic.load_theme_from_config()
    theme_dropdown, theme_var = create_theme_picker(
        topbar,
        theme_name,
        on_change=_on_theme_change
    )
    theme_dropdown.pack(side="left")

    # ===================== HEADER =====================
    header = theme.make_frame(root, bg=theme.CARD_BG)
    header.pack(fill="x", padx=12, pady=(0, 12))

    # Titel
    tk.Label(
        header,
        text="🌱 VIVOSUN Thermo Setup",
        bg=theme.CARD_BG,
        fg=getattr(theme, "LIME", theme.BTN_PRIMARY),
        font=theme.FONT_TITLE
    ).pack(pady=(8, 4))

    # Logo
    logo_path = setup_assets.get_asset_path("setup.png")
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path).resize((360, 120), Image.LANCZOS)
            logo = ImageTk.PhotoImage(img)
            lbl = tk.Label(header, image=logo, bg=theme.CARD_BG)
            lbl.image = logo
            lbl.pack(pady=(2, 8))
        except Exception:
            pass

    # ===================== MAIN BODY =====================
    body = tk.Frame(root, bg=theme.BG_MAIN)
    body.pack(fill="both", expand=True, padx=16, pady=10)

    # Text Output
    tk.Label(
        body, text="📋 Setup Log:",
        bg=theme.BG_MAIN, fg=theme.TEXT_DIM, font=theme.FONT_LABEL
    ).pack(anchor="w", padx=8, pady=(0, 4))

    text = tk.Text(
        body, height=10, width=80,
        bg=theme.CARD_BG, fg=theme.TEXT,
        insertbackground=theme.BTN_PRIMARY,
        relief="flat", font=("Consolas", 10)
    )
    text.pack(fill="x", padx=10, pady=(0, 12))
    text.config(highlightbackground="#333", highlightthickness=1)

    # Device List
    tk.Label(
        body, text="🧭 Gefundene Geräte:",
        bg=theme.BG_MAIN, fg=theme.TEXT_DIM, font=theme.FONT_LABEL
    ).pack(anchor="w", padx=8, pady=(4, 4))

    device_listbox = tk.Listbox(
        body, height=8,
        bg=theme.CARD_BG, fg=theme.TEXT,
        selectbackground=theme.BTN_PRIMARY,
        selectforeground="black",
        font=("Segoe UI", 12, "bold"),
        relief="flat"
    )
    device_listbox.pack(fill="both", expand=True, padx=10, pady=(0, 12))
    device_listbox.config(highlightbackground="#333", highlightthickness=1)

    # ===================== PROGRESS BAR =====================
    progress_frame = tk.Frame(body, bg=theme.CARD_BG)
    progress_frame.pack(fill="x", pady=(0, 10))

    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "Pulse.Horizontal.TProgressbar",
        troughcolor=theme.CARD_BG,
        background=theme.BTN_PRIMARY,
        thickness=12
    )

    progress = ttk.Progressbar(
        progress_frame,
        orient="horizontal",
        mode="determinate",
        maximum=100,
        style="Pulse.Horizontal.TProgressbar"
    )
    progress.pack(fill="x", padx=10, pady=8)

    start_pulse, stop_pulse = setup_logic.create_progress_pulse(progress, root)

    # ===================== FOOTER =====================
    footer = tk.Frame(root, bg=theme.CARD_BG)
    footer.pack(fill="x", side="bottom", padx=12, pady=10)

    # Rechtsbündige Buttons
    btn_frame = tk.Frame(footer, bg=theme.CARD_BG)
    btn_frame.pack(side="right")

    devices = []
    result_queue = setup_logic.make_result_queue()

    def add_device(dev_id, name):
        device_listbox.insert(tk.END, f"⚪ {dev_id} | {name}")

    def on_scan():
        setup_logic.start_device_scan(text, result_queue, btn_scan, start_pulse)

    def on_save():
        setup_logic.save_selected_device(root, device_listbox, text, theme_var)

    # Buttons
    btn_scan = theme.make_button(btn_frame, "🔍 Scan Devices", on_scan, color=theme.BTN_PRIMARY)
    btn_save = theme.make_button(btn_frame, "💾 Save Selected", on_save, color=theme.BTN_SECONDARY)
    btn_close = theme.make_button(btn_frame, "❌ Close", root.destroy, color=theme.ORANGE)

    btn_close.pack(side="right", padx=4)
    btn_save.pack(side="right", padx=4)
    btn_scan.pack(side="right", padx=4)

    # Status Label
    status_label = tk.Label(
        footer,
        text="Ready ✅",
        bg=theme.CARD_BG, fg=theme.TEXT_DIM, font=theme.FONT_LABEL
    )
    status_label.pack(side="left", padx=10)

    # ===================== QUEUE HANDLING =====================
    def finish_scan(output):
        stop_pulse()
        btn_scan.config(state="normal")
        setup_logic.finish_scan_output(output, text, device_listbox, devices, add_device)
        status_label.config(text="Scan complete ✅")

    def poll_queue():
        output = setup_logic.try_get_result(result_queue)
        if output:
            finish_scan(output)
        root.after(300, poll_queue)

    poll_queue()
