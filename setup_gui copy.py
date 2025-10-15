#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌱 VIVOSUN Setup GUI – Theme Switchable (Green/Oceanic) without destroying root
- Rebuilds only the content area on theme change
- Cancels all pending `after()` jobs cleanly to avoid Tkinter invalid command errors
- Persists chosen theme to config.json (key: "theme")
"""

import os
import re
import sys
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import threading
import queue
import asyncio

# -------------------------------------------------------------
# Imports
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

def _load_initial_theme_name():
    """Read theme name from config.json; fall back to VIVOSUN Green."""
    try:
        cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
        name = cfg.get("theme")
        if name in THEMES:
            return name
    except Exception:
        pass
    return "🌿 VIVOSUN Green"


# -------------------------------------------------------------
# App
# -------------------------------------------------------------
def run_setup():
    # Shared state
    state = {
        "theme_name": _load_initial_theme_name(),
        "after_jobs": set(),      # track scheduled after() ids
        "pulse_running": False,   # for progress animation
        "pulse_value": 0,
        "pulse_dir": 1,
        "result_queue": queue.Queue(),
        "devices": [],
        "content": None,          # content frame handle (rebuilt on theme switch)
        "widgets": {},            # references to dynamic widgets (progress, buttons, etc.)
    }

    # Root window
    theme = THEMES[state["theme_name"]]
    root = tk.Tk()
    root.title("🌱 VIVOSUN Setup")
    root.geometry("560x800")
    root.minsize(540, 760)
    root.configure(bg=theme.BG_MAIN)
    icon_loader.set_app_icon(root)

    # --------- Topbar with Theme Switcher ---------
    topbar = tk.Frame(root, bg=theme.CARD_BG)
    topbar.pack(fill="x", pady=(8, 10))

    tk.Label(
        topbar,
        text="🎨 Theme:",
        bg=theme.CARD_BG,
        fg=theme.TEXT_DIM,
        font=("Segoe UI", 10, "bold")
    ).pack(side="left", padx=(12, 6))

    theme_var = tk.StringVar(value=state["theme_name"])
    theme_dropdown = ttk.Combobox(
        topbar, textvariable=theme_var, values=list(THEMES.keys()),
        state="readonly", width=22
    )
    theme_dropdown.pack(side="left", padx=(0, 12))

    # Give ttk combobox a dark-ish look
    style = ttk.Style()
    try:
        style.theme_use("default")
    except Exception:
        pass
    style.configure(
        "TCombobox",
        fieldbackground=theme.CARD_BG,
        background=theme.CARD_BG,
        foreground=theme.TEXT,
        arrowcolor=theme.TEXT
    )

    # --------- Content root (rebuilt on theme change) ---------
    state["content"] = tk.Frame(root, bg=theme.BG_MAIN)
    state["content"].pack(fill="both", expand=True)

    # ---------- Helpers to manage after() ----------
    def schedule(ms, fn):
        """Schedule and track an after() job."""
        job = root.after(ms, fn)
        state["after_jobs"].add(job)
        return job

    def cancel_all_after():
        """Cancel all tracked after() jobs safely."""
        for job in list(state["after_jobs"]):
            try:
                root.after_cancel(job)
            except Exception:
                pass
            finally:
                state["after_jobs"].discard(job)

    # ---------- Build UI (content) ----------
    def build_content():
        # Clear previous content
        for child in state["content"].winfo_children():
            child.destroy()

        # Reset timers
        cancel_all_after()
        state["pulse_running"] = False
        state["pulse_value"] = 0
        state["pulse_dir"] = 1

        th = THEMES[state["theme_name"]]
        root.configure(bg=th.BG_MAIN)

        # ----- HEADER -----
        header = th.make_frame(state["content"], bg=th.CARD_BG, height=120)
        header.pack(fill="x", pady=(0, 8))

        title = tk.Label(
            header,
            text="🌱 VIVOSUN Thermo Setup",
            bg=th.CARD_BG,
            fg=getattr(th, "LIME", getattr(th, "AQUA", "#00d8ff")),
            font=th.FONT_TITLE
        )
        title.pack(pady=(10, 4))

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

        # ----- TEXT LOG -----
        text = tk.Text(
            state["content"], width=68, height=10,
            bg=th.CARD_BG, fg=th.TEXT_DIM,
            font=("Consolas", 9), relief="flat",
            insertbackground=getattr(th, "LIME", getattr(th, "AQUA", "#00d8ff"))
        )
        text.pack(padx=12, pady=10)
        state["widgets"]["log"] = text

        # ----- DEVICE LIST -----
        list_frame = th.make_frame(state["content"], bg=th.CARD_BG)
        list_frame.pack(fill="x", padx=12, pady=(0, 10))

        device_listbox = tk.Listbox(
            list_frame,
            bg=th.CARD_BG,
            fg=th.TEXT,
            selectbackground=getattr(th, "LIME", getattr(th, "AQUA", "#00d8ff")),
            selectforeground="black",
            font=("Segoe UI", 13, "bold"),
            height=6,
            relief="flat",
            highlightbackground=th.BORDER,
            highlightthickness=1
        )
        device_listbox.pack(fill="x", padx=8, pady=6)
        state["widgets"]["listbox"] = device_listbox

        # ----- BUTTONS -----
        btn_frame = th.make_frame(state["content"], bg=th.CARD_BG)
        btn_frame.pack(pady=8)

        def add_device_to_list(device_id, name):
            device_listbox.insert(tk.END, f"⚪ {device_id}  |  {name}")

        def save_selected():
            sel = device_listbox.curselection()
            if not sel:
                text.insert("end", "❌ Kein Gerät ausgewählt!\n")
                text.see("end")
                return

            selected_line = device_listbox.get(sel[0])
            selected_id = selected_line.split("|")[0].replace("⚪", "").replace("🟢", "").strip()

            cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
            cfg["device_id"] = selected_id

            use_celsius = messagebox.askyesno("Unit Selection", "Möchten Sie Celsius verwenden?\n\nYes = °C, No = °F")
            cfg["unit_celsius"] = use_celsius

            # Persist current theme choice too
            cfg["theme"] = state["theme_name"]

            utils.safe_write_json(config.CONFIG_FILE, cfg)
            text.insert("end", f"💾 Gespeichert: Device-ID {selected_id} (Celsius={use_celsius}), theme='{state['theme_name']}'\n")
            text.see("end")

            root.destroy()
            core_gui.run_app(selected_id)

        # Scan workflow -------------
        def scan_devices():
            def worker():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    scanner = VivosunThermoScanner()
                    found = loop.run_until_complete(scanner.discover(timeout=10))
                    if not found:
                        state["result_queue"].put("⚠️ Keine Geräte gefunden.")
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
                        state["result_queue"].put("\n".join(out))
                except Exception as e:
                    state["result_queue"].put(f"❌ Scanfehler: {e}")
                finally:
                    try:
                        loop.close()
                    except Exception:
                        pass

            text.insert("end", "🔍 Suche nach Geräten (10s)…\n")
            text.see("end")
            scan_btn.config(state="disabled")
            start_pulse()
            threading.Thread(target=worker, daemon=True).start()

        def finish_scan(output):
            th2 = THEMES[state["theme_name"]]
            stop_pulse()
            scan_btn.config(state="normal")
            text.insert("end", output + "\n")
            text.insert("end", "✅ Scan abgeschlossen.\n")
            text.see("end")

            state["devices"].clear()
            device_listbox.delete(0, tk.END)

            pattern = r"([0-9A-F]{8}(?:-[0-9A-F]{4}){3}-[0-9A-F]{12}|(?:[0-9A-F]{2}:){5}[0-9A-F]{2})"
            for line in output.splitlines():
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    dev_id = match.group(1)
                    name = line.split("|")[-1].strip() if "|" in line else "Device"
                    state["devices"].append(dev_id)
                    add_device_to_list(dev_id, name)
            if not state["devices"]:
                text.insert("end", "⚠️ Keine gültigen Device-IDs gefunden.\n")
                text.see("end")

        def poll_queue():
            try:
                while True:
                    output = state["result_queue"].get_nowait()
                    finish_scan(output)
            except queue.Empty:
                pass
            schedule(500, poll_queue)

        # Buttons
        scan_btn = theme.make_button(
            btn_frame, "🔍 Scan Devices", scan_devices,
            color=getattr(theme, "LIME", getattr(theme, "AQUA", "#00d8ff")),
            font=theme.FONT_BTN
        )
        scan_btn.pack(side="left", padx=8)
        state["widgets"]["scan_btn"] = scan_btn

        save_btn = theme.make_button(
            btn_frame, "💾 Save Selected", save_selected,
            color=getattr(theme, "LIME_DARK", getattr(theme, "AQUA", "#00d8ff")),
            font=theme.FONT_BTN
        )
        save_btn.pack(side="left", padx=8)

        # ----- PROGRESS -----
        prog_frame = theme.make_frame(state["content"], bg=theme.CARD_BG)
        prog_frame.pack(fill="x", pady=8)

        # ttk progress style
        style.configure(
            "Pulse.Horizontal.TProgressbar",
            troughcolor=theme.CARD_BG,
            background=getattr(theme, "AQUA", getattr(theme, "LIME", "#00d8ff")),
            darkcolor=theme.BORDER,
            lightcolor=getattr(theme, "LIME", getattr(theme, "AQUA", "#00d8ff")),
            thickness=14
        )

        progress = ttk.Progressbar(
            prog_frame,
            orient="horizontal",
            mode="determinate",
            length=400,
            style="Pulse.Horizontal.TProgressbar",
            maximum=100
        )
        progress.pack(padx=12, pady=6)
        state["widgets"]["progress"] = progress

        # Pulse animation
        def animate_pulse():
            if not state["pulse_running"]:
                return
            v = state["pulse_value"] + state["pulse_dir"] * 5
            if v >= 100:
                v = 100
                state["pulse_dir"] = -1
            elif v <= 0:
                v = 0
                state["pulse_dir"] = 1
            state["pulse_value"] = v
            progress["value"] = v
            schedule(50, animate_pulse)

        def start_pulse():
            state["pulse_running"] = True
            state["pulse_value"] = 0
            state["pulse_dir"] = 1
            animate_pulse()

        def stop_pulse():
            state["pulse_running"] = False
            progress["value"] = 0

        # expose for scan workflow
        state["start_pulse"] = start_pulse
        state["stop_pulse"] = stop_pulse

        # ----- FOOTER -----
        footer = theme.make_frame(state["content"], bg=theme.CARD_BG)
        footer.pack(side="bottom", fill="x", pady=6)

        tk.Label(
            footer,
            text=f"{state['theme_name']} • VIVOSUN Setup Tool v2.6",
            bg=theme.CARD_BG,
            fg=theme.TEXT_DIM,
            font=theme.FONT_LABEL
        ).pack(side="right", padx=10)

        # Start queue polling
        poll_queue()

    # Bind combobox: theme switching WITHOUT destroying root
    def on_theme_change(event=None):
        new_name = theme_var.get()
        if new_name == state["theme_name"]:
            return
        # Save selection to config
        try:
            cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
            cfg["theme"] = new_name
            utils.safe_write_json(config.CONFIG_FILE, cfg)
        except Exception:
            pass
        # Update name and rebuild content
        state["theme_name"] = new_name
        build_content()

        # Re-style topbar to new theme
        th = THEMES[state["theme_name"]]
        topbar.configure(bg=th.CARD_BG)
        for w in topbar.winfo_children():
            try:
                if isinstance(w, tk.Label):
                    w.configure(bg=th.CARD_BG, fg=th.TEXT_DIM)
            except Exception:
                pass
        # Update ttk combobox style colors
        try:
            style.configure(
                "TCombobox",
                fieldbackground=th.CARD_BG,
                background=th.CARD_BG,
                foreground=th.TEXT,
                arrowcolor=th.TEXT
            )
        except Exception:
            pass

    theme_dropdown.bind("<<ComboboxSelected>>", on_theme_change)

    # Convenience wrappers to call current start/stop pulse
    def start_pulse():
        if "start_pulse" in state:
            state["start_pulse"]()

    def stop_pulse():
        if "stop_pulse" in state:
            state["stop_pulse"]()

    # Build initial content
    build_content()

    # Expose pulse control to scan callback closures
    def start_pulse_exposed():
        start_pulse()

    def stop_pulse_exposed():
        stop_pulse()

    # Store them (not strictly needed, but explicit)
    state["start_pulse"] = start_pulse_exposed
    state["stop_pulse"] = stop_pulse_exposed

    # Safe shutdown: cancel timers
    def on_close():
        try:
            cancel_all_after()
        except Exception:
            pass
        try:
            root.destroy()
        except Exception:
            pass

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    run_setup()
