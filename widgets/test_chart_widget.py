#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_chart_widget.py – Modul für Live-Humidity-Charts (internal/external)
Kann in jedes Fenster eingebunden werden.
"""

import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import utils, config


def create_chart_widget(parent, config=config, utils=utils):
    """Erzeugt einen Live-Chart-Frame für interne & externe Feuchtigkeit."""
    frame = tk.Frame(parent, bg=config.BG)

    fig, ax = plt.subplots(figsize=(8, 4))
    fig.patch.set_facecolor(config.CARD)
    ax.set_facecolor(config.CARD)
    ax.grid(True, color="#333", linestyle=":", alpha=0.4)
    ax.set_title("Humidity Live Chart", color=config.TEXT)
    ax.set_xlabel("Samples", color=config.TEXT)
    ax.set_ylabel("Humidity (%)", color=config.TEXT)
    plt.setp(ax.get_xticklabels(), color=config.TEXT)
    plt.setp(ax.get_yticklabels(), color=config.TEXT)

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.get_tk_widget().pack(fill="both", expand=True)

    lbl_status = tk.Label(
        frame,
        text="Initializing chart ...",
        bg=config.BG,
        fg=config.TEXT,
        font=("Consolas", 12)
    )
    lbl_status.pack(pady=6)

    data = {"internal": [], "external": []}
    _running = [True]

    # ---------- RESET ----------
    def reset_chart():
        """Leert Chart & JSON-Datei."""
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
        print("🧹 Chart reset complete.")

    # ---------- POLLING ----------
    def poll_chart():
        """Aktualisiert die Daten & zeichnet den Chart neu."""
        if not _running[0]:
            return

        try:
            status = utils.safe_read_json(config.STATUS_FILE) or {}
            connected = status.get("connected", False)

            d = utils.safe_read_json(config.DATA_FILE) or {}
            hm = d.get("h_main")
            he = d.get("h_ext")

            if not connected or (hm is None and he is None):
                ax.clear()
                ax.set_facecolor(config.CARD)
                ax.grid(True, color="#333", linestyle=":", alpha=0.4)
                ax.set_title("Humidity Live Chart", color=config.TEXT)
                ax.set_xlabel("Samples", color=config.TEXT)
                ax.set_ylabel("Humidity (%)", color=config.TEXT)
                canvas.draw_idle()

                lbl_status.config(
                    text="[🔴] Disconnected or waiting for data …",
                    fg="red" if not connected else "orange"
                )

                frame.after(2000, poll_chart)
                return

            # --- Daten hinzufügen ---
            if hm is not None:
                data["internal"].append(hm)
                data["internal"] = data["internal"][-100:]
            if he is not None:
                data["external"].append(he)
                data["external"] = data["external"][-100:]

            # --- Plot zeichnen ---
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

        frame.after(2000, poll_chart)

    # ---------- STOP ----------
    def stop_chart():
        """Beendet das Polling sauber."""
        _running[0] = False

    poll_chart()

    return frame, reset_chart, stop_chart
