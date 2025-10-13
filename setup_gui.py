#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌱 VIVOSUN Setup GUI – Live Theme Switch Edition
"""

import os, re, sys, tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import threading, queue, asyncio

# -------------------------------------------------------------
# Imports & Themes
# -------------------------------------------------------------
try:
    import config, utils, icon_loader
    from main_gui import core_gui
    from themes import theme_vivosun, theme_oceanic
except ImportError:
    sys.path.append(os.path.dirname(__file__))
    import config, utils, icon_loader
    from main_gui import core_gui
    from themes import theme_vivosun, theme_oceanic

from vivosun_thermo import VivosunThermoScanner


# -------------------------------------------------------------
# Theme registry
# -------------------------------------------------------------
THEMES = {
    "🌿 VIVOSUN Green": theme_vivosun,
    "🌊 Oceanic Blue": theme_oceanic,
}


def load_theme_from_config():
    try:
        cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
        t = cfg.get("theme")
        if t in THEMES:
            return t
    except Exception:
        pass
    return "🌿 VIVOSUN Green"


# -------------------------------------------------------------
# Main GUI
# -------------------------------------------------------------
def run_setup():
    theme_name = load_theme_from_config()
    theme = THEMES[theme_name]

    root = tk.Tk()
    root.title("🌱 VIVOSUN Setup")
    root.geometry("560x780")
    root.configure(bg=theme.BG_MAIN)
    icon_loader.set_app_icon(root)

    # ============ THEME SWITCHER ============
    topbar = tk.Frame(root, bg=theme.CARD_BG)
    topbar.pack(fill="x", pady=(8, 10))

    tk.Label(topbar, text="🎨 Theme:", bg=theme.CARD_BG, fg=theme.TEXT_DIM, font=theme.FONT_LABEL)\
        .pack(side="left", padx=(12, 6))

    theme_var = tk.StringVar(value=theme_name)
    theme_dropdown = ttk.Combobox(
        topbar, textvariable=theme_var, values=list(THEMES.keys()), state="readonly", width=22
    )
    theme_dropdown.pack(side="left", padx=(0, 12))

    # Combobox-Theme style
    style = ttk.Style()
    style.theme_use("default")
    style.configure("TCombobox",
                    fieldbackground=theme.CARD_BG,
                    background=theme.CARD_BG,
                    foreground=theme.TEXT,
                    arrowcolor=theme.TEXT)

    # ============ BUILD FUNCTION ============
    def build_gui(th):
        """Rebuilds GUI layout dynamically when theme changes."""
        for child in root.winfo_children():
            if child not in (topbar,):
                child.destroy()

        # --- Header ---
        header = th.make_frame(root, bg=th.CARD_BG)
        header.pack(fill="x", pady=(0, 10))

        tk.Label(
            header,
            text="🌱 VIVOSUN Thermo Setup",
            bg=th.CARD_BG,
            fg=th.LIME if hasattr(th, "LIME") else th.AQUA,
            font=th.FONT_TITLE
        ).pack(pady=(10, 4))

        logo_path = os.path.join(os.path.dirname(__file__), "assets", "setup.png")
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path).resize((380, 120), Image.LANCZOS)
                logo = ImageTk.PhotoImage(img)
                logo_label = tk.Label(header, image=logo, bg=th.CARD_BG)
                logo_label.image = logo
                logo_label.pack(pady=(5, 5))
            except Exception:
                pass

        # --- Text Output ---
        text = tk.Text(
            root, width=68, height=10,
            bg=th.CARD_BG, fg=th.TEXT_DIM,
            font=("Consolas", 9),
            relief="flat",
            insertbackground=th.BTN_PRIMARY
        )
        text.pack(padx=12, pady=10)

        # --- Device List ---
        list_frame = th.make_frame(root, bg=th.CARD_BG)
        list_frame.pack(fill="x", padx=12, pady=(0, 10))

        device_listbox = tk.Listbox(
            list_frame,
            bg=th.CARD_BG,
            fg=th.TEXT,
            selectbackground=th.BTN_PRIMARY,
            selectforeground="black",
            font=("Segoe UI", 13, "bold"),
            height=6,
            relief="flat",
            highlightbackground=th.BORDER,
            highlightthickness=1
        )
        device_listbox.pack(fill="x", padx=8, pady=6)

        devices = []
        result_queue = queue.Queue()

        def add_device_to_list(device_id, name):
            device_listbox.insert(tk.END, f"⚪ {device_id}  |  {name}")

        # --- Device Scanning ---
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
                    result_queue.put(f"❌ Scanfehler: {e}")
                finally:
                    loop.close()

            text.insert("end", "🔍 Suche nach Geräten (10s)…\n")
            text.see("end")
            scan_btn.config(state="disabled")
            start_pulse()
            threading.Thread(target=worker, daemon=True).start()

        def finish_scan(output):
            stop_pulse()
            scan_btn.config(state="normal")
            text.insert("end", output + "\n✅ Scan abgeschlossen.\n")
            text.see("end")

            devices.clear()
            device_listbox.delete(0, tk.END)
            pattern = r"([0-9A-F]{8}(?:-[0-9A-F]{4}){3}-[0-9A-F]{12}|(?:[0-9A-F]{2}:){5}[0-9A-F]{2})"
            for line in output.splitlines():
                match = re.search(pattern, line, re.IGNORECASE)
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

        # --- Save Selection ---
        def save_selected():
            sel = device_listbox.curselection()
            if not sel:
                text.insert("end", "❌ Kein Gerät ausgewählt!\n")
                text.see("end")
                return

            selected_line = device_listbox.get(sel[0])
            selected_id = selected_line.split("|")[0].replace("⚪", "").strip()

            cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
            cfg["device_id"] = selected_id
            cfg["theme"] = theme_var.get()

            use_celsius = messagebox.askyesno("Unit Selection", "Möchten Sie Celsius verwenden?\n\nYes = °C, No = °F")
            cfg["unit_celsius"] = use_celsius

            utils.safe_write_json(config.CONFIG_FILE, cfg)
            text.insert("end", f"💾 Gespeichert: Device {selected_id} ({'°C' if use_celsius else '°F'})\n")
            text.see("end")

            root.destroy()
            core_gui.run_app(selected_id)

        # --- Buttons ---
        button_frame = th.make_frame(root, bg=th.CARD_BG)
        button_frame.pack(pady=6)

        nonlocal scan_btn
        scan_btn = th.make_button(button_frame, "🔍 Scan Devices", scan_devices, color=th.BTN_PRIMARY)
        scan_btn.pack(side="left", padx=8)

        th.make_button(button_frame, "💾 Save Selected", save_selected, color=th.BTN_SECONDARY).pack(side="left", padx=8)

        # --- Progress Bar ---
        progress_frame = th.make_frame(root, bg=th.CARD_BG)
        progress_frame.pack(fill="x", pady=8)

        style.configure("Pulse.Horizontal.TProgressbar",
                        troughcolor=th.CARD_BG,
                        background=th.BTN_PRIMARY,
                        lightcolor=th.BTN_HOVER,
                        darkcolor=th.BORDER,
                        thickness=14)

        progress = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate",
                                   length=400, style="Pulse.Horizontal.TProgressbar", maximum=100)
        progress.pack(padx=12, pady=4)

        pulse_running, pulse_value, pulse_dir = False, 0, 1

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
                pulse_value, pulse_dir = 100, -1
            elif pulse_value <= 0:
                pulse_value, pulse_dir = 0, 1
            progress["value"] = pulse_value
            root.after(50, animate_pulse)

        # --- Footer ---
        footer = th.make_frame(root, bg=th.CARD_BG)
        footer.pack(side="bottom", fill="x", pady=6)

        tk.Label(footer, text=f"{theme_var.get()} • VIVOSUN Setup Tool v2.8",
                 bg=th.CARD_BG, fg=th.TEXT_DIM, font=th.FONT_LABEL).pack(side="right", padx=10)

        poll_queue()

    # ============ THEME SWITCH HANDLER ============
    def on_theme_change(event=None):
        new_name = theme_var.get()
        new_theme = THEMES[new_name]
        utils.safe_write_json(config.CONFIG_FILE, {"theme": new_name})
        build_gui(new_theme)

    theme_dropdown.bind("<<ComboboxSelected>>", on_theme_change)

    # ============ INITIAL BUILD ============
    scan_btn = None
    build_gui(theme)

    root.mainloop()


if __name__ == "__main__":
    run_setup()
