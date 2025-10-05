import os, re, sys, threading, queue, asyncio, tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

try:
    from . import config, utils, icon_loader, gui
except ImportError:
    import config, utils, icon_loader, gui

from vivosun_thermo import VivosunThermoScanner


def run_setup():
    root = tk.Tk()
    root.title("🌱 VIVOSUN Setup")
    root.geometry("520x650")   # kompakter
    root.configure(bg=config.BG)
    root.resizable(False, False)

    icon_loader.set_app_icon(root)

    # ---------- TITLE ----------
    tk.Label(
        root,
        text="🌱 VIVOSUN Thermo Setup Tool",
        bg=config.BG, fg=config.TEXT,
        font=("Segoe UI", 18, "bold")
    ).pack(pady=(10, 5))

    # ---------- LOGO ----------
    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    logo_path = os.path.join(assets_dir, "setup.png")
    if os.path.exists(logo_path):
        img = Image.open(logo_path).resize((360, 270), Image.LANCZOS)
        logo_img = ImageTk.PhotoImage(img)
        lbl = tk.Label(root, image=logo_img, bg=config.BG)
        lbl.image = logo_img
        lbl.pack(pady=5)

    # ---------- TEXTBOX ----------
    text = tk.Text(
        root, width=62, height=8,
        bg="#071116", fg="#bff5c9",
        font=("Consolas", 9)
    )
    text.pack(padx=10, pady=6)

    # ---------- LISTBOX ----------
    list_frame = tk.Frame(root, bg=config.CARD)
    list_frame.pack(fill="x", padx=10, pady=(0, 5))
    device_listbox = tk.Listbox(
        list_frame,
        bg=config.CARD, fg=config.TEXT,
        selectbackground="lime", selectforeground="black",
        font=("Segoe UI", 12, "bold"), height=5
    )
    device_listbox.pack(fill="x", padx=4, pady=4)

    # ---------- PROGRESSBAR ----------
    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "Pulse.Horizontal.TProgressbar",
        troughcolor=config.CARD, background="#00ccff",
        darkcolor="#004466", lightcolor="#33ddff",
        thickness=14
    )
    progress = ttk.Progressbar(
        root, orient="horizontal", mode="determinate",
        length=300, style="Pulse.Horizontal.TProgressbar", maximum=100
    )
    progress.pack(pady=(4, 10))

    pulse_running, pulse_value, pulse_dir = False, 0, 1
    def start_pulse():
        nonlocal pulse_running, pulse_value, pulse_dir
        pulse_running, pulse_value, pulse_dir = True, 0, 1
        animate_pulse()
    def stop_pulse():
        nonlocal pulse_running
        pulse_running = False
        progress["value"] = 0
    def animate_pulse():
        nonlocal pulse_value, pulse_dir
        if not pulse_running: return
        pulse_value += pulse_dir * 5
        if pulse_value >= 100: pulse_dir = -1
        elif pulse_value <= 0: pulse_dir = 1
        progress["value"] = pulse_value
        root.after(50, animate_pulse)

    # ---------- SCAN + SAVE ----------
    devices, result_queue = [], queue.Queue()

    def add_device_to_list(dev_id):
        device_listbox.insert(tk.END, f"⚪ {dev_id}")

    def finish_scan(output):
        nonlocal devices
        stop_pulse(); scan_btn.config(state="normal")
        text.insert("end", output + "\n✅ Scan abgeschlossen.\n"); text.see("end")
        devices.clear(); device_listbox.delete(0, tk.END)
        for line in output.splitlines():
            m = re.search(r"([0-9A-F]{8}(?:-[0-9A-F]{4}){3}-[0-9A-F]{12})", line)
            if m: devices.append(m.group(1)); add_device_to_list(m.group(1))
        if not devices: text.insert("end", "⚠️ Keine gültigen Device-IDs gefunden.\n")

    def poll_queue():
        try:
            while True: finish_scan(result_queue.get_nowait())
        except queue.Empty: pass
        root.after(500, poll_queue)

    def scan_devices():
        def worker():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                found = loop.run_until_complete(VivosunThermoScanner().discover(timeout=30))
                result_queue.put("\n".join(map(str, found)) if found else "⚠️ Keine Geräte gefunden.")
            except Exception as e:
                result_queue.put(f"❌ Fehler beim Scan: {e}")
            finally: loop.close()

        text.insert("end", "🔍 Scanning for devices (30s)…\n"); text.see("end")
        scan_btn.config(state="disabled"); start_pulse()
        threading.Thread(target=worker, daemon=True).start()

    def save_selected():
        sel = device_listbox.curselection()
        if not sel:
            text.insert("end", "❌ Kein Gerät ausgewählt!\n")
            return
        dev_id = device_listbox.get(sel[0]).replace("⚪ ", "").replace("🟢 ", "")
        cfg = utils.safe_read_json(config.CONFIG_FILE) or {}
        cfg["device_id"] = dev_id
        use_c = messagebox.askyesno("Einheit", "Celsius verwenden?\n\nYes = °C, No = °F")
        cfg["unit_celsius"] = use_c
        utils.safe_write_json(config.CONFIG_FILE, cfg)
        text.insert("end", f"💾 Saved {dev_id}, °C={use_c}\n"); text.see("end")
        root.destroy()
        gui.run_app(dev_id)

    # ---------- BUTTONS ----------
    btn_frame = tk.Frame(root, bg=config.CARD)
    btn_frame.pack(pady=(4, 6))
    def make_btn(t, cmd, bg="lime"):
        return tk.Button(
            btn_frame, text=t, command=cmd,
            bg=bg, fg="black", font=("Segoe UI", 12, "bold"),
            padx=8, pady=4, relief="ridge"
        )
    scan_btn = make_btn("🔍 Scan Devices", scan_devices)
    scan_btn.pack(side="left", padx=6)
    make_btn("💾 Save Selected", save_selected).pack(side="left", padx=6)

    # ---------- FOOTER ----------
    tk.Label(
        root,
        text="📟 VIVOSUN Setup Tool v2.2  •  Dominik Hackintosh",
        bg=config.CARD, fg=config.TEXT, font=("Segoe UI", 10)
    ).pack(side="bottom", pady=6)

    poll_queue()
    root.mainloop()


if __name__ == "__main__":
    run_setup()
