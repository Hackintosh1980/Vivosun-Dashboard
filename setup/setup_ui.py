#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_ui.py – 🌱 VIVOSUN Setup UI (neu gestaltet)
Saubere Sektionen, ein Theme-Picker, ruhige Farbaufteilung, Buttons unten rechts.
"""

import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from setup import setup_logic, setup_assets
from main_gui.theme_picker import create_theme_picker


def build_gui(root, theme):
    """Erstellt das komplette Setup-Fenster mit ruhigem Layout und klarer Struktur."""
    # --- Reset Window Layout ---
    for child in root.winfo_children():
        child.destroy()

    root.configure(bg=theme.BG_MAIN)

    # ======================================================
    # 🟩 TOPBAR (Theme Picker)
    # ======================================================
    topbar = tk.Frame(root, bg=theme.CARD_BG)
    topbar.pack(fill="x", pady=(10, 12))

    tk.Label(
        topbar,
        text="🎨 Theme:",
        bg=theme.CARD_BG,
        fg=theme.TEXT_DIM,
        font=theme.FONT_LABEL
    ).pack(side="left", padx=(12, 6))

    def _on_theme_change(new_name):
        new_theme = setup_logic.get_theme_by_name(new_name)
        setup_logic.save_theme_to_config(new_name)
        build_gui(root, new_theme)

    theme_name = setup_logic.load_theme_from_config()
    theme_dropdown, theme_var = create_theme_picker(
        topbar,
        theme_name,
        on_change=_on_theme_change
    )
    theme_dropdown.pack(side="left", padx=(0, 8))

    # ======================================================
    # 🌿 HEADER
    # ======================================================
    header = theme.make_frame(root, bg=theme.CARD_BG)
    header.pack(fill="x", padx=14, pady=(0, 12))

    tk.Label(
        header,
        text="🌱 VIVOSUN Thermo Setup",
        bg=theme.CARD_BG,
        fg=(theme.LIME if hasattr(theme, "LIME") else theme.BTN_PRIMARY),
        font=theme.FONT_TITLE
    ).pack(pady=(8, 4))

    logo_path = setup_assets.get_asset_path("setup.png")
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path).resize((420, 130), Image.LANCZOS)
            logo = ImageTk.PhotoImage(img)
            logo_lbl = tk.Label(header, image=logo, bg=theme.CARD_BG)
            logo_lbl.image = logo
            logo_lbl.pack(pady=(2, 8))
        except Exception:
            pass

    # ======================================================
    # 🧭 MAIN CONTENT
    # ======================================================
    content = tk.Frame(root, bg=theme.BG_MAIN)
    content.pack(fill="both", expand=True, padx=14, pady=(0, 10))

    # --- Text Output (Log) ---
    log_card = theme.make_frame(content, bg=theme.CARD_BG)
    log_card.pack(fill="x", pady=(0, 10))

    tk.Label(
        log_card,
        text="📄 Scan Output",
        bg=theme.CARD_BG,
        fg=theme.TEXT_DIM,
        font=theme.FONT_LABEL
    ).pack(anchor="w", padx=10, pady=(8, 4))

    text = tk.Text(
        log_card,
        height=10,
        bg=theme.CARD_BG,
        fg=theme.TEXT_DIM,
        relief="flat",
        font=("Consolas", 10),
        insertbackground=theme.BTN_PRIMARY
    )
    text.pack(fill="x", padx=10, pady=(0, 10))

    # --- Device List ---
    device_card = theme.make_frame(content, bg=theme.CARD_BG)
    device_card.pack(fill="both", expand=True, pady=(0, 10))

    tk.Label(
        device_card,
        text="🧩 Gefundene Geräte",
        bg=theme.CARD_BG,
        fg=theme.TEXT,
        font=("Segoe UI", 12, "bold")
    ).pack(anchor="w", padx=10, pady=(10, 6))

    device_listbox = tk.Listbox(
        device_card,
        bg=theme.CARD_BG,
        fg=theme.TEXT,
        selectbackground=theme.BTN_PRIMARY,
        selectforeground="black",
        font=("Segoe UI", 13, "bold"),
        height=8,
        relief="flat",
        highlightbackground=theme.BORDER,
        highlightthickness=1
    )
    device_listbox.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ======================================================
    # 🔄 PROGRESS BAR
    # ======================================================
    progress_card = theme.make_frame(content, bg=theme.CARD_BG)
    progress_card.pack(fill="x", pady=(0, 10))

    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "Pulse.Horizontal.TProgressbar",
        troughcolor=theme.CARD_BG,
        background=theme.BTN_PRIMARY,
        lightcolor=theme.BTN_HOVER,
        darkcolor=theme.BORDER,
        thickness=14
    )

    progress = ttk.Progressbar(
        progress_card,
        orient="horizontal",
        mode="determinate",
        maximum=100,
        length=460,
        style="Pulse.Horizontal.TProgressbar"
    )
    progress.pack(padx=10, pady=10)

    start_pulse, stop_pulse = setup_logic.create_progress_pulse(progress, root)

    # ======================================================
    # ⚙️ FOOTER (Buttons unten rechts)
    # ======================================================
    footer = theme.make_frame(root, bg=theme.CARD_BG)
    footer.pack(side="bottom", fill="x", padx=14, pady=(6, 12))

    footer_left = tk.Label(
        footer,
        text=f"{theme_var.get()} • VIVOSUN Setup Tool",
        bg=theme.CARD_BG,
        fg=theme.TEXT_DIM,
        font=theme.FONT_LABEL
    )
    footer_left.pack(side="left", padx=10)

    footer_right = tk.Frame(footer, bg=theme.CARD_BG)
    footer_right.pack(side="right", padx=(0, 8))

    btn_scan = theme.make_button(footer_right, "🔍 Scan Devices", lambda: None, color=theme.BTN_PRIMARY)
    btn_scan.pack(side="right", padx=6)

    btn_save = theme.make_button(footer_right, "💾 Save Selected", lambda: None, color=theme.BTN_SECONDARY)
    btn_save.pack(side="right", padx=6)

    # ======================================================
    # ⚡ LOGIC WIRING
    # ======================================================
    devices = []
    result_queue = setup_logic.make_result_queue()

    def add_device(dev_id, name):
        device_listbox.insert(tk.END, f"⚪ {dev_id}  |  {name}")

    def on_scan():
        setup_logic.start_device_scan(text, result_queue, btn_scan, start_pulse)

    def on_save():
        setup_logic.save_selected_device(root, device_listbox, text, theme_var)

    btn_scan.config(command=on_scan)
    btn_save.config(command=on_save)

    # Poll Queue
    def finish_scan(output):
        stop_pulse()
        btn_scan.config(state="normal")
        setup_logic.finish_scan_output(output, text, device_listbox, devices, add_device)

    def poll_queue():
        output = setup_logic.try_get_result(result_queue)
        if output is not None:
            finish_scan(output)
        root.after(300, poll_queue)

    poll_queue()
