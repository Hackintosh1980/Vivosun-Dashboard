#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌱 VIVOSUN Setup GUI – Cross-Platform (macOS & Windows)
"""

import os, re, sys, json, tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import threading, queue, asyncio

try:
    from . import config, utils, icon_loader, gui
except ImportError:
    import config, utils, icon_loader, gui

from vivosun_thermo import VivosunThermoScanner


def run_setup():
    root = tk.Tk()
    root.title("🌱 VIVOSUN Setup")
    root.geometry("600x800")
    root.configure(bg=config.BG)

    icon_loader.set_app_icon(root)

    # ---------- HEADER ----------
    title = tk.Label(
        root,
        text="🌱 VIVOSUN Thermo Setup Tool",
        bg=config.BG,
        fg=config.TEXT,
        font=("Segoe UI", 22, "bold")
    )
    title.pack(pady=(15, 5))

    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    logo_path = os.path.join(assets_dir, "setup.png")
    if os.path.exists(logo_path):
        img = Image.open(logo_path).resize((100, 100), Image.LANCZOS)
        logo_img = ImageTk.PhotoImage(img)
        logo_label = tk.Label(root, image=logo_img, bg=config.BG)
        logo_label.image = logo_img
        logo_label.pack(pady=10)

    # ---------- TEXT BOX ----------
    text = tk.Text(root, width=75, height=15, bg="#071116", fg="#bff5c9", font=("Consolas", 10))
    text.pack(padx=10, pady=10)

    # ---------- DEVICE LIST ----------
    list_frame = tk.Frame(root, bg=config.CARD)
    list_frame.pack(fill="x", padx=10, pady=(0, 10))

    device_listbox = tk.Listbox(
        list_frame,
        bg=config.CARD,
        fg=config.TEXT,
        selectbackground="lime",
        selectforeground="black",
        font=("Segoe UI", 16, "bold"),
        height=8
    )
    device_listbox.pack(fill="x", padx=5, pady=5)

    devices = []
    result_queue = queue.Queue()

    def add_device_to_list(device_id, name):
        device_listbox.insert(tk.END, f"⚪ {device_id}  |  {name}")

    # ---------- SAVE ----------
    def save_selected():
        sel = device_listbox.curselection()
        if not sel:
            text.insert("end", "❌ Kein Gerät ausgewählt!\n")
            return

        selected_line = device_listbox.get(sel[0])
        selected_id = selected_line.split("|")[0].replace("⚪", "").replace("🟢", "").strip()

        cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
        cfg["device_id"] = selected_id

        use_celsius = messagebox.askyesno("Unit Selection", "Möchten Sie Celsius verwenden?\n\nYes = °C, No = °F")
        cfg["unit_celsius"] = use_celsius

        utils.safe_write_json(config.CONFIG_FILE, cfg)
        text.insert("end", f"💾 Saved Device-ID {selected_id} and unit_celsius={use_celsius} in config.json\n")
        text.see("end")

        root.destroy()
        gui.run_app(selected_id)

    # ---------- SCAN ----------
    scan_btn = None

    def scan_devices():
        def worker():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                scanner = VivosunThermoScanner()
                found = loop.run_until_complete(scanner.discover(timeout=60))
                if not found:
                    result_queue.put("⚠️ Keine Geräte gefunden.")
                else:
                    out = []
                    for d in found:
                        name = (getattr(d, "name", "") or "").strip()
                        addr = getattr(d, "address", None) or getattr(d, "identifier", None)
                        if not name or not addr:
                            continue
                        # akzeptiere Vivosun & ThermoBeacon
                        if not any(x in name.lower() for x in ("vivosun", "thermobeacon")):
                            continue
                        # Plattformabhängige ID
                        if sys.platform.startswith("win"):
                            device_id = addr
                        else:
                            device_id = getattr(d, "identifier", addr)
                        out.append(f"{device_id}  |  {name}")
                    result_queue.put("\n".join(out))
            except Exception as e:
                result_queue.put(f"❌ Fehler beim Scan: {e}")
            finally:
                loop.close()

        text.insert("end", "🔍 Scanning for devices (60s)…\n")
        text.see("end")
        scan_btn.config(state="disabled")
        start_pulse()
        threading.Thread(target=worker, daemon=True).start()

    def finish_scan(output):
        nonlocal devices
        stop_pulse()
        scan_btn.config(state="normal")

        text.insert("end", output + "\n")
        text.insert("end", "✅ Scan abgeschlossen.\n")
        text.see("end")

        devices = []
        device_listbox.delete(0, tk.END)

        # Erkenne UUID oder MAC
        uuid_pattern = r"[0-9A-F]{8}(?:-[0-9A-F]{4}){3}-[0-9A-F]{12}"
        mac_pattern = r"(?:[0-9A-F]{2}:){5}[0-9A-F]{2}"
        for line in output.splitlines():
            match = re.search(f"({uuid_pattern}|{mac_pattern})", line, re.IGNORECASE)
            if match:
                dev_id = match.group(1)
                name = line.split("|")[-1].strip() if "|" in line else "Device"
                devices.append(dev_id)
                add_device_to_list(dev_id, name)

        if not devices:
            text.insert("end", "⚠️ Keine gültigen Device-IDs gefunden.\n")

    def poll_queue():
        try:
            while True:
                output = result_queue.get_nowait()
                finish_scan(output)
        except queue.Empty:
            pass
        root.after(500, poll_queue)

    # ---------- BUTTONS ----------
    button_frame = tk.Frame(root, bg=config.CARD)
    button_frame.pack(pady=10)

    def button_style(master, text, cmd):
        return tk.Button(
            master,
            text=text,
            command=cmd,
            bg="lime",
            fg="black",
            font=("Segoe UI", 14, "bold"),
            relief="ridge",
            padx=12, pady=6
        )

    scan_btn = button_style(button_frame, "🔍 Scan Devices", scan_devices)
    scan_btn.pack(side="left", padx=8)

    button_style(button_frame, "💾 Save Selected", save_selected).pack(side="left", padx=8)

    # ---------- FOOTER ----------
    footer = tk.Frame(root, bg=config.CARD)
    footer.pack(side="bottom", fill="x", pady=8)

    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "Pulse.Horizontal.TProgressbar",
        troughcolor=config.CARD,
        background="#00ccff",
        darkcolor="#004466",
        lightcolor="#33ddff",
        thickness=18
    )

    progress = ttk.Progressbar(
        footer,
        orient="horizontal",
        mode="determinate",
        length=280,
        style="Pulse.Horizontal.TProgressbar",
        maximum=100
    )
    progress.pack(side="left", padx=12, pady=4)

    pulse_running = False
    pulse_value = 0
    pulse_dir = 1

    def start_pulse():
        nonlocal pulse_running, pulse_value, pulse_dir
        pulse_running = True
        pulse_value = 0
        pulse_dir = 1
        animate_pulse()

    def stop_pulse():
        nonlocal pulse_running
        pulse_running = False
        progress["value"] = 0

    def animate_pulse():
        nonlocal pulse_value, pulse_dir
        if not pulse_running:
            return
        pulse_value += pulse_dir * 5
        if pulse_value >= 100:
            pulse_value = 100
            pulse_dir = -1
        elif pulse_value <= 0:
            pulse_value = 0
            pulse_dir = 1
        progress["value"] = pulse_value
        root.after(50, animate_pulse)

    footer_label = tk.Label(
        footer,
        text="📟 VIVOSUN Setup Tool v2.2 (Cross-Platform)",
        bg=config.CARD,
        fg=config.TEXT,
        font=("Segoe UI", 12)
    )
    footer_label.pack(side="right", padx=10)

    poll_queue()
    icon_loader.set_app_icon(root)
    root.mainloop()


if __name__ == "__main__":
    run_setup()
