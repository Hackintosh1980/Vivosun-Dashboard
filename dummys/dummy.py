#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dummy.py – Vollständig Theme-gesteuerte Testoberfläche + Status-Bar Scan-Animation
"""

import tkinter as tk
from tkinter import ttk
import random, time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import theme


class DummyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🌱 VIVOSUN Theme Dummy + Status-Bar")
        self.root.geometry("1300x900")

        # ---- Theme ----
        theme.init_all(root, mode="dark")

        # ---- State ----
        self.leaf_offset = tk.DoubleVar(value=0.0)
        self.hum_offset = tk.DoubleVar(value=0.0)
        self.running = False
        self.start_time = None
        self.scan_duration = 45  # Sekunden

        # ---------- HEADER ----------
        header = ttk.Frame(root, style="VivoCard.TFrame", padding=(theme.spacing()["lg"], theme.spacing()["sm"]))
        header.pack(fill="x", padx=theme.spacing()["md"], pady=theme.spacing()["md"])

        ttk.Label(header, text="VIVOSUN Theme Dummy", style="VivoTitle.TLabel").pack(side="left", padx=8)

        ttk.Button(header, text="☀️ Light", style="VivoAccent.TButton",
                   command=lambda: self.set_mode("light")).pack(side="right", padx=6)
        ttk.Button(header, text="🌙 Dark", style="VivoAccent.TButton",
                   command=lambda: self.set_mode("dark")).pack(side="right", padx=6)

        # ---------- BODY ----------
        body = ttk.Frame(root, style="Vivo.TFrame")
        body.pack(fill="both", expand=True, padx=theme.spacing()["lg"], pady=theme.spacing()["md"])

        # LEFT: Offsets
        left = theme.mk_card(body)
        left.pack(side="left", fill="y", padx=(0, theme.spacing()["lg"]), pady=(0, theme.spacing()["md"]))

        ttk.Label(left, text="Offsets", style="VivoTitle.TLabel").pack(anchor="w", pady=(0, 8))
        self.add_offset_field(left, "Leaf Offset (°C)", self.leaf_offset).pack(fill="x", pady=4)
        self.add_offset_field(left, "Humidity Offset (%)", self.hum_offset).pack(fill="x", pady=4)

        ttk.Separator(left).pack(fill="x", pady=10)
        ttk.Label(left, text="Statusfarben", style="VivoSub.TLabel").pack(anchor="w", pady=(0, 4))
        ttk.Label(left, text="Connected", style="VivoOk.TLabel").pack(anchor="w")
        ttk.Label(left, text="Warning", style="VivoWarn.TLabel").pack(anchor="w")
        ttk.Label(left, text="Error", style="VivoErr.TLabel").pack(anchor="w")

        # RIGHT: Chart
        chart_card = theme.mk_card(body)
        chart_card.pack(side="left", fill="both", expand=True)

        ttk.Label(chart_card, text="Matplotlib Chart", style="VivoTitle.TLabel").pack(anchor="w", pady=(0, 8))
        fig, ax = plt.subplots(figsize=(6, 4))
        theme.style_figure(fig)
        self.line, = ax.plot([], [], label="Random Data")
        ax.set_xlabel("Zeit")
        ax.set_ylabel("Wert")
        ax.legend()
        ax.grid(True)
        canvas = FigureCanvasTkAgg(fig, master=chart_card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self.fig, self.ax, self.canvas = fig, ax, canvas
        self.xdata = list(range(20))
        self.ydata = [random.uniform(20, 28) for _ in self.xdata]
        self.update_plot()

        # ---------- STATUS BAR (unten) ----------
        status_card = theme.mk_card(root, padding=(theme.spacing()["lg"], theme.spacing()["sm"]))
        status_card.pack(fill="x", padx=theme.spacing()["md"], pady=(theme.spacing()["sm"], theme.spacing()["lg"]))

        ttk.Label(status_card, text="Sensor-Scan Status", style="VivoTitle.TLabel").pack(anchor="w")

        self.progress = ttk.Progressbar(
            status_card,
            orient="horizontal",
            length=800,
            mode="determinate",
            style="Vivo.Horizontal.TProgressbar"
        )
        self.progress.pack(pady=10)
        self.progress["value"] = 0

        self.status_lbl = ttk.Label(status_card, text="Bereit", style="VivoSub.TLabel")
        self.status_lbl.pack(anchor="w", pady=(0, 6))

        self.btn_scan = ttk.Button(
            status_card,
            text="🔍 Scan starten",
            style="VivoAccent.TButton",
            command=self.start_scan
        )
        self.btn_scan.pack(anchor="e")

    # -------------------- Offset-Felder --------------------
    def add_offset_field(self, parent, label, var):
        frame = ttk.Frame(parent, style="Vivo.TFrame")
        ttk.Label(frame, text=label, style="VivoSub.TLabel").grid(row=0, column=0, sticky="w")
        entry = ttk.Entry(frame, textvariable=var, width=8, justify="center", style="Vivo.TEntry")
        entry.grid(row=0, column=1, padx=6)

        def step(delta):
            try:
                v = float(var.get()) + delta
            except Exception:
                v = 0.0
            var.set(round(v, 2))

        up_symbol = "▲"
        down_symbol = "▼"
        ttk.Button(frame, text=down_symbol, style="VivoArrow.TButton",
                   width=3, command=lambda: step(-0.1)).grid(row=0, column=2, padx=4)
        ttk.Button(frame, text=up_symbol, style="VivoArrow.TButton",
                   width=3, command=lambda: step(+0.1)).grid(row=0, column=3, padx=2)
        frame.grid_columnconfigure(0, weight=1)
        return frame

    # -------------------- Plot Update --------------------
    def update_plot(self):
        self.ydata.pop(0)
        self.ydata.append(random.uniform(20, 28))
        self.line.set_data(self.xdata, self.ydata)
        self.ax.set_ylim(min(self.ydata) - 1, max(self.ydata) + 1)
        self.ax.set_xlim(0, len(self.xdata))
        self.canvas.draw_idle()
        self.root.after(1000, self.update_plot)

    # -------------------- Theme Umschalten --------------------
    def set_mode(self, mode):
        theme.set_mode(mode)
        theme.apply_theme(self.root)
        theme.apply_matplotlib_defaults()
        theme.style_figure(self.fig)
        self.canvas.draw_idle()

    # -------------------- Scan Animation --------------------
    def start_scan(self):
        if self.running:
            return
        self.running = True
        self.start_time = time.time()
        self.progress["value"] = 0
        self.status_lbl.configure(text="Suche läuft …")
        self.btn_scan.configure(text="⏳ Scanne …", state="disabled")
        self.animate_progress()

    def animate_progress(self):
        elapsed = time.time() - self.start_time
        percent = min(100, (elapsed / self.scan_duration) * 100)
        self.progress["value"] = percent
        if elapsed < self.scan_duration:
            self.root.after(100, self.animate_progress)
        else:
            self.finish_scan()

    def finish_scan(self):
        self.progress["value"] = 100
        self.status_lbl.configure(text="✅ Suche abgeschlossen")
        self.btn_scan.configure(text="✔ Fertig", state="normal")
        self.running = False


if __name__ == "__main__":
    root = tk.Tk()
    DummyApp(root)
    root.mainloop()
