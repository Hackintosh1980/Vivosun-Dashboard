import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patheffects as path_effects
from PIL import Image, ImageTk
import os


def open_window(parent, config, utils,
                key, title, color, ylabel,
                data_buffers, time_buffer, unit_celsius):
    win = tk.Toplevel(parent)
    win.title(f"🔍 {title} – Enlarged View")
    win.geometry("1400x900")
    win.configure(bg=config.BG)

    # ---------- HEADER ----------
    header = tk.Frame(win, bg=config.CARD)
    header.pack(side="top", fill="x", padx=10, pady=8)

    left_frame = tk.Frame(header, bg=config.CARD)
    left_frame.pack(side="left", padx=6)

    assets_dir = os.path.join(os.path.dirname(__file__), "assets")
    logo_path = os.path.join(assets_dir, "Logo.png")
    if os.path.exists(logo_path):
        try:
            img = Image.open(logo_path).resize((90, 90), Image.LANCZOS)
            logo_img = ImageTk.PhotoImage(img)
            logo_label = tk.Label(left_frame, image=logo_img, bg=config.CARD)
            logo_label.image = logo_img
            logo_label.pack(side="left", padx=(0, 10))
        except Exception as e:
            print(f"⚠️ Logo konnte nicht geladen werden: {e}")

    title_label = tk.Label(
        left_frame,
        text=f"🌱 Enlarged – {title}",
        bg=config.CARD,
        fg=config.TEXT,
        font=("Segoe UI", 18, "bold"),
        anchor="w",
        justify="left"
    )
    title_label.pack(side="left", anchor="center")

    # ---------- Matplotlib Setup ----------
    fig, ax = plt.subplots(figsize=(10, 5), facecolor=config.BG)
    ax.set_facecolor("#121a24")
    ax.set_ylabel(ylabel, color=config.TEXT, fontsize=11, weight="bold")
    ax.tick_params(axis="y", labelcolor=config.TEXT)
    ax.grid(True, linestyle="--", alpha=0.3)

    line, = ax.plot([], [], color=color, linewidth=2.2, alpha=0.95, zorder=1)

    # große Wertanzeige im Plot
    value_label = ax.text(
        0.02, 0.98, "--",
        transform=ax.transAxes,
        color=color,
        fontsize=40,
        weight="bold",
        va="top", ha="left",
        path_effects=[path_effects.withStroke(linewidth=6, foreground="black")],
        zorder=5
    )

    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))
    ax.tick_params(axis="x", labelcolor=config.TEXT, rotation=0)

    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    # ---------- Steuerleiste ----------
    ctrl = tk.Frame(win, bg=config.CARD)
    ctrl.pack(side="bottom", fill="x", pady=6)

    paused = tk.BooleanVar(value=False)
    xs = []

    # Zeitfenster-Auswahl
    SPANS_DAYS = {
        "1s": 1 / 86400,
        "3s": 3 / 86400,
        "10s": 10 / 86400,
        "30s": 30 / 86400,
        "1m": 1 / 1440,
        "15m": 15 / 1440,
        "30m": 30 / 1440,
        "1h": 1 / 24,
        "3h": 3 / 24,
        "12h": 12 / 24,
        "24h": 1,
        "1w": 7,
        "1M": 30,
        "3M": 90,
    }
    span_choice = tk.StringVar(value="1h")

    def apply_locator(span_days: float) -> None:
        if span_days <= 30 / 86400:
            ax.xaxis.set_major_locator(mdates.SecondLocator(interval=5))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        elif span_days <= 2 / 1440:
            ax.xaxis.set_major_locator(mdates.SecondLocator(interval=10))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
        elif span_days <= 1 / 24:
            ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=5))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        elif span_days <= 1:
            ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
        elif span_days <= 7:
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        elif span_days <= 31:
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=2))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        else:
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.ConciseDateFormatter(ax.xaxis.get_major_locator()))

    tk.Label(ctrl, text="⏱ Window:", bg=config.CARD, fg=config.TEXT).pack(side="left", padx=6)
    window_box = tk.OptionMenu(ctrl, span_choice, *SPANS_DAYS.keys())
    window_box.config(bg="lime", fg="black", font=("Segoe UI", 10, "bold"), activebackground="lime")
    window_box["highlightthickness"] = 0
    window_box.pack(side="left", padx=6)

    # Pause / Reset
    def toggle_pause():
        paused.set(not paused.get())
        btn_pause.config(text="▶ Resume" if paused.get() else "⏸ Pause")

    def reset_view():
        if xs:
            ax.set_xlim(xs[0], xs[-1])
            ax.relim()
            ax.autoscale_view(scalex=False, scaley=True)
            canvas.draw_idle()

    btn_pause = tk.Button(ctrl, text="⏸ Pause", command=toggle_pause,
                          bg="orange", fg="black", font=("Segoe UI", 10, "bold"))
    btn_pause.pack(side="left", padx=6)

    tk.Button(ctrl, text="🔄 Reset View", command=reset_view,
              bg="lime", fg="black", font=("Segoe UI", 10, "bold")).pack(side="left", padx=6)

    # ---------- Pan & Zoom ----------
    _drag = {"x": None, "xlim": None}

    def on_scroll(event):
        cur_lo, cur_hi = ax.get_xlim()
        if cur_lo == cur_hi:
            return
        x0 = event.xdata if event.xdata is not None else (cur_lo + cur_hi) / 2
        zoom_in = event.step > 0 if hasattr(event, "step") else (event.button == "up")
        factor = 0.9 if zoom_in else 1.1
        width = (cur_hi - cur_lo) * factor
        left, right = x0 - width / 2, x0 + width / 2
        ax.set_xlim(left, right)
        canvas.draw_idle()

    def on_press(event):
        if event.button == 1:
            _drag["x"] = event.x
            _drag["xlim"] = ax.get_xlim()

    def on_motion(event):
        if _drag["x"] is None or event.x is None:
            return
        dx_pix = event.x - _drag["x"]
        lo, hi = _drag["xlim"]
        if ax.bbox.width == 0:
            return
        scale = (hi - lo) / ax.bbox.width
        ax.set_xlim(lo - dx_pix * scale, hi - dx_pix * scale)
        canvas.draw_idle()

    def on_release(event):
        _drag["x"] = None
        _drag["xlim"] = None

    fig.canvas.mpl_connect("scroll_event", on_scroll)
    fig.canvas.mpl_connect("button_press_event", on_press)
    fig.canvas.mpl_connect("motion_notify_event", on_motion)
    fig.canvas.mpl_connect("button_release_event", on_release)

    # ---------- Update Loop ----------
    _prev_span_key = [span_choice.get()]

    def update():
        if paused.get():
            win.after(1000, update)
            return

        nonlocal xs
        xs = [mdates.date2num(t) for t in time_buffer]
        ys = []
        for v in data_buffers[key]:
            if v is None:
                ys.append(float("nan"))
            elif key in ("t_main", "t_ext"):
                ys.append(v if unit_celsius.get() else utils.c_to_f(v))
            else:
                ys.append(v)

        if xs and ys:
            line.set_data(xs, ys)
            span_days = SPANS_DAYS.get(span_choice.get(), 1 / 24)
            right = xs[-1]
            left = right - span_days
            ax.set_xlim(left, right)
            ax.relim()
            ax.autoscale_view(scalex=False, scaley=True)

            if span_choice.get() != _prev_span_key[0]:
                apply_locator(span_days)
                _prev_span_key[0] = span_choice.get()

            latest = ys[-1]
            if latest is not None and not (latest != latest):
                if key in ("t_main", "t_ext"):
                    unit = "°C" if unit_celsius.get() else "°F"
                    value_label.set_text(f"{latest:.1f} {unit}")
                elif "h_" in key:
                    value_label.set_text(f"{latest:.1f} %")
                else:
                    value_label.set_text(f"{latest:.2f} kPa")
            else:
                value_label.set_text("--")

        canvas.draw_idle()
        win.after(1000, update)

    apply_locator(SPANS_DAYS[span_choice.get()])
    update()
    return win
