#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_window.py – Ultimatives Testfenster mit Live-Charts, Reset & Statusanzeige
"""

import tkinter as tk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import utils, config
from widgets.footer_widget import create_footer


def open_window(parent, config=config, utils=utils):
    win = tk.Toplevel(parent)
    win.title("🧪 VIVOSUN Ultimate Test Window")
    win.geometry("1000x700")
    win.configure(bg=config.BG)

    # ---------- HEADER ----------
    header = tk.Frame(win, bg=config.CARD)
    header.pack(side="top", fill="x", padx=10, pady=6)

    # Logo
    try:
        img = Image.open("assets/Logo.png").resize((60, 60))
        logo = ImageTk.PhotoImage(img)
        lbl_logo = tk.Label(header, image=logo, bg=config.CARD)
        lbl_logo.image = logo
        lbl_logo.pack(side="left", padx=(5, 10))
    except Exception:
        tk.Label(header, text="🌱", bg=config.CARD, fg=config.TEXT, font=("Segoe UI", 28)).pack(side="left")

    tk.Label(
        header,
        text="VIVOSUN Ultimate Test Window",
        bg=config.CARD,
        fg=config.TEXT,
        font=("Segoe UI", 22, "bold")
    ).pack(side="left", padx=(10, 20))

    # ---------- RESET BUTTON ----------
    def reset_chart():
        """Leert Chart, Pufferspeicher & DATA_FILE."""
        data["internal"].clear()
        data["external"].clear()
        ax.clear()
        ax.set_facecolor(config.CARD)
        ax.grid(True, color="#333", linestyle=":", alpha=0.4)
        ax.set_title("Humidity Live Chart", color=config.TEXT)
        ax.set_xlabel("Samples", color=config.TEXT)
        ax.set_ylabel("Humidity (%)", color=config.TEXT)
        canvas.draw_idle()

        utils.safe_write_json(config.DATA_FILE, {
            "timestamp": None,
            "t_main": None,
            "h_main": None,
            "t_ext": None,
            "h_ext": None,
        })
        lbl_status.config(text="🧹 Chart reset – waiting for data …", fg="orange")
        print("🧹 Chart & data fully reset.")

    tk.Button(
        header,
        text="🔄 Reset Chart",
        bg="#ff8844",
        fg="white",
        font=("Segoe UI", 12, "bold"),
        relief="flat",
        command=reset_chart
    ).pack(side="right", padx=10)

    # ---------- BODY ----------
    body = tk.Frame(win, bg=config.BG)
    body.pack(fill="both", expand=True, padx=20, pady=20)

    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor(config.CARD)
    ax.set_facecolor(config.CARD)
    ax.grid(True, color="#333", linestyle=":", alpha=0.4)
    ax.set_title("Humidity Live Chart", color=config.TEXT)
    ax.set_xlabel("Samples", color=config.TEXT)
    ax.set_ylabel("Humidity (%)", color=config.TEXT)
    plt.setp(ax.get_xticklabels(), color=config.TEXT)
    plt.setp(ax.get_yticklabels(), color=config.TEXT)

    canvas = FigureCanvasTkAgg(fig, master=body)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    lbl_status = tk.Label(
        body,
        text="Initializing...",
        bg=config.BG,
        fg=config.TEXT,
        font=("Consolas", 14)
    )
    lbl_status.pack(pady=8)

    # Datenspeicher
    data = {"internal": [], "external": []}

    # ---------- FOOTER ----------
    set_status, mark_data_update, set_sensor_status = create_footer(win, config)
    set_status(False)
    set_sensor_status(False, False)

    # ---------- POLLING ----------
    def poll():
        """Liest Status + Daten, aktualisiert Footer, Statusanzeige & Chart."""
        try:
            status = utils.safe_read_json(config.STATUS_FILE) or {}
            connected = status.get("connected", False)
            main_ok = status.get("sensor_ok_main", False)
            ext_ok = status.get("sensor_ok_ext", False)
            set_status(connected)
            set_sensor_status(main_ok, ext_ok)

            d = utils.safe_read_json(config.DATA_FILE) or {}
            hm = d.get("h_main")
            he = d.get("h_ext")

            # --- Wenn keine Verbindung oder keine Daten ---
            if not connected or (hm is None and he is None):
                ax.clear()
                ax.set_facecolor(config.CARD)
                ax.grid(True, color="#333", linestyle=":", alpha=0.4)
                ax.set_title("Humidity Live Chart", color=config.TEXT)
                ax.set_xlabel("Samples", color=config.TEXT)
                ax.set_ylabel("Humidity (%)", color=config.TEXT)
                canvas.draw_idle()

                if not connected:
                    lbl_status.config(text="[🔴] Disconnected – waiting …", fg="red")
                else:
                    lbl_status.config(text="⚙️ Waiting for humidity data …", fg="orange")

                win.after(2000, poll)
                return

            # --- Daten anhängen ---
            if hm is not None:
                data["internal"].append(hm)
                data["internal"] = data["internal"][-100:]
            if he is not None:
                data["external"].append(he)
                data["external"] = data["external"][-100:]

            # --- Zeichnen ---
            ax.clear()
            ax.set_facecolor(config.CARD)
            ax.grid(True, color="#333", linestyle=":", alpha=0.4)
            ax.set_title("Humidity Live Chart", color=config.TEXT)
            ax.set_xlabel("Samples", color=config.TEXT)
            ax.set_ylabel("Humidity (%)", color=config.TEXT)

            if data["internal"]:
                ax.plot(data["internal"], color="lime", linewidth=2, label="Internal")
            if data["external"]:
                ax.plot(data["external"], color="orange", linewidth=2, label="External")

            if data["internal"] or data["external"]:
                ax.legend(facecolor=config.CARD, edgecolor="gray", labelcolor=config.TEXT)

            plt.setp(ax.get_xticklabels(), color=config.TEXT)
            plt.setp(ax.get_yticklabels(), color=config.TEXT)
            canvas.draw_idle()

            lbl_status.config(
                text=f"[🟢] Connected | Int: {hm:.1f}% | Ext: {he:.1f}%",
                fg="lime"
            )

        except Exception as e:
            lbl_status.config(text=f"⚠️ Poll error: {e}", fg="orange")

        win.after(2000, poll)

    poll()
    return win
