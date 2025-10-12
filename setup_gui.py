#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌱 VIVOSUN Setup GUI – Themed Lime Edition
"""

import os, re, sys, tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import threading, queue, asyncio

try:
    import config, utils, icon_loader, theme_vivosun as theme
    from main_gui import core_gui
except ImportError:
    sys.path.append(os.path.dirname(__file__))
    import config, utils, icon_loader, theme_vivosun as theme
    from main_gui import core_gui

from vivosun_thermo import VivosunThermoScanner

C = theme.VIVOSUN_COLORS


def run_setup():
    root = tk.Tk()
    root.title("🌱 VIVOSUN Setup – Themed Lime Edition")
    root.geometry("520x720")
    root.configure(bg=C["bg_main"])
    icon_loader.set_app_icon(root)

    # ---------- HEADER ----------
    theme_frame = theme.make_frame(root, bg=C["card_bg"])
    theme_frame.pack(fill="x", pady=(10, 8))

    title = tk.Label(
        theme_frame,
        text="🌱 VIVOSUN Thermo Setup",
        bg=C["card_bg"], fg=C["lime"],
        font=C["font_title"]
    )
    title.pack(pady=(8, 5))

    logo_path = os.path.join(os.path.dirname(__file__), "assets", "setup.png")
    if os.path.exists(logo_path):
        img = Image.open(logo_path).resize((380, 120), Image.LANCZOS)
        logo_img = ImageTk.PhotoImage(img)
        logo_label = tk.Label(theme_frame, image=logo_img, bg=C["card_bg"])
        logo_label.image = logo_img
        logo_label.pack(pady=6)

    # ---------- TEXTBOX ----------
    text = tk.Text(
        root, width=64, height=10,
        bg="#071116", fg=C["lime"], font=("Consolas", 9)
    )
    text.pack(padx=8, pady=8)

    # ---------- LISTBOX ----------
    list_frame = theme.make_frame(root, bg=C["card_bg"])
    list_frame.pack(fill="x", padx=10, pady=(0, 8))

    device_listbox = tk.Listbox(
        list_frame, bg=C["card_bg"], fg=C["text"],
        selectbackground=C["lime"], selectforeground="black",
        font=("Segoe UI", 14, "bold"), height=6
    )
    device_listbox.pack(fill="x", padx=6, pady=6)

    devices, result_queue = [], queue.Queue()

    def add_device(device_id, name):
        device_listbox.insert(tk.END, f"⚪ {device_id}  |  {name}")

    # ---------- SAVE ----------
    def save_selected():
        sel = device_listbox.curselection()
        if not sel:
            text.insert("end", "❌ Kein Gerät ausgewählt!\n")
            return

        selected_line = device_listbox.get(sel[0])
        selected_id = selected_line.split("|")[0].replace("⚪", "").strip()

        cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
        cfg["device_id"] = selected_id
        use_celsius = messagebox.askyesno(
            "Unit Selection", "Möchten Sie Celsius verwenden?\n\nYes = °C, No = °F"
        )
        cfg["unit_celsius"] = use_celsius
        utils.safe_write_json(config.CONFIG_FILE, cfg)
        text.insert("end", f"💾 Saved Device-ID {selected_id}\n")
        text.see("end")

        root.destroy()
        core_gui.run_app(selected_id)

    # ---------- SCAN ----------
    def scan_devices():
        def worker():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                scanner = VivosunThermoScanner()
                found = loop.run_until_complete(scanner.discover(timeout=10))
                if not found:
                    result_queue.put("⚠️ Keine Geräte gefunden.")
                else:
                    out = []
                    for d in found:
                        name = (getattr(d, "name", "") or "").strip()
                        addr = getattr(d, "address", None) or getattr(d, "identifier", None)
                        if not name or not addr:
                            continue
                        if not any(x in name.lower() for x in ("vivosun", "thermobeacon")):
                            continue
                        device_id = getattr(d, "identifier", addr)
                        out.append(f"{device_id}  |  {name}")
                    result_queue.put("\n".join(out))
            except Exception as e:
                result_queue.put(f"❌ Fehler beim Scan: {e}")
            finally:
                loop.close()

        text.insert("end", "🔍 Scanning for devices (10s)…\n")
        text.see("end")
        scan_btn.config(state="disabled")
        start_pulse()
        threading.Thread(target=worker, daemon=True).start()

    def finish_scan(output):
        stop_pulse()
        scan_btn.config(state="normal")
        text.insert("end", output + "\n✅ Scan abgeschlossen.\n")
        text.see("end")

        device_listbox.delete(0, tk.END)
        pattern = r"([0-9A-F]{8}(?:-[0-9A-F]{4}){3}-[0-9A-F]{12}|(?:[0-9A-F]{2}:){5}[0-9A-F]{2})"
        for line in output.splitlines():
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                dev_id = match.group(1)
                name = line.split("|")[-1].strip() if "|" in line else "Device"
                add_device(dev_id, name)

    def poll_queue():
        try:
            while True:
                out = result_queue.get_nowait()
                finish_scan(out)
        except queue.Empty:
            pass
        root.after(500, poll_queue)

    # ---------- BUTTONS ----------
    btn_frame = theme.make_frame(root, bg=C["card_bg"])
    btn_frame.pack(pady=10)
    scan_btn = theme.make_button(btn_frame, "🔍 Scan Devices", scan_devices)
    scan_btn.pack(side="left", padx=8)
    theme.make_button(btn_frame, "💾 Save Selected", save_selected, C["orange"]).pack(side="left", padx=8)

    # ---------- PROGRESS ----------
    progress_frame = theme.make_frame(root, bg=C["card_bg"])
    progress_frame.pack(fill="x", pady=8)

    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "Lime.Horizontal.TProgressbar",
        troughcolor=C["card_bg"], background=C["lime"],
        darkcolor=C["lime_dark"], lightcolor=C["lime"], thickness=16
    )

    progress = ttk.Progressbar(progress_frame, orient="horizontal",
                               mode="determinate", length=400,
                               style="Lime.Horizontal.TProgressbar", maximum=100)
    progress.pack(padx=12, pady=4)

    pulse_running, pulse_val, pulse_dir = False, 0, 1

    def start_pulse():
        nonlocal pulse_running, pulse_val, pulse_dir
        pulse_running = True; pulse_val = 0; pulse_dir = 1
        animate_pulse()

    def stop_pulse():
        nonlocal pulse_running
        pulse_running = False; progress["value"] = 0

    def animate_pulse():
        nonlocal pulse_val, pulse_dir
        if not pulse_running:
            return
        pulse_val += pulse_dir * 5
        if pulse_val >= 100:
            pulse_val, pulse_dir = 100, -1
        elif pulse_val <= 0:
            pulse_val, pulse_dir = 0, 1
        progress["value"] = pulse_val
        root.after(50, animate_pulse)

    # ---------- FOOTER ----------
    footer = theme.make_frame(root, bg=C["card_bg"])
    footer.pack(side="bottom", fill="x", pady=8)
    tk.Label(
        footer,
        text="📟 VIVOSUN Setup Tool v2.5 – Lime Edition",
        bg=C["card_bg"], fg=C["text"], font=("Segoe UI", 11)
    ).pack(side="right", padx=10)

    poll_queue()
    root.mainloop()


if __name__ == "__main__":
    run_setup()
