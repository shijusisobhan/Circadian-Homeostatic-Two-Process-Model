import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

# -----------------------------
# MAIN WINDOW
# -----------------------------
root = tk.Tk()
root.title("Two-Process Sleep Model")
root.geometry("1200x800")

# -----------------------------
# INPUT FRAME
# -----------------------------
input_frame = ttk.Frame(root, padding=10)
input_frame.pack(side=tk.LEFT, fill=tk.Y)

title = tk.Label(
    input_frame,
    text="Two-Process Sleep Model Parameters",
    font=("Arial", 14, "bold")
)
title.grid(row=0, column=0, columnspan=2, pady=10)

# -----------------------------
# PARAMETERS + DESCRIPTIONS
# -----------------------------
params = [
    ("Au", 0.1, "Upper threshold oscillation amplitude"),
    ("Al", 0.1, "Lower threshold oscillation amplitude"),
    ("T_circadian", 24, "Circadian period (hr)"),
    ("ti_hr", 18.18, "Sleep pressure buildup time constant (hr)"),
    ("td_hr", 4.2, "Sleep pressure decay time constant (hr)"),
    ("N_days", 10, "Number of days"),
    ("Ml", 0.15, "Lower threshold mean value")
]

entries = {}

# Create input labels and boxes
for i, (label, default, desc) in enumerate(params, start=1):

    tk.Label(
        input_frame,
        text=f"{label} ({desc})",
        anchor="w",
        justify="left"
    ).grid(row=i, column=0, sticky="w", pady=4)

    entry = tk.Entry(input_frame, width=12)
    entry.insert(0, str(default))
    entry.grid(row=i, column=1, padx=5, pady=4)

    entries[label] = entry

# -----------------------------
# MU SLIDER
# -----------------------------
mu_row = len(params) + 1

tk.Label(
    input_frame,
    text="Mu (Upper threshold mean value)",
    anchor="w"
).grid(row=mu_row, column=0, sticky="w", pady=10)

mu_slider = tk.Scale(
    input_frame,
    from_=0,
    to=1,
    resolution=0.01,
    orient=tk.HORIZONTAL,
    length=200
)

mu_slider.set(0.6)
mu_slider.grid(row=mu_row, column=1)

# -----------------------------
# FIGURE FRAME
# -----------------------------
fig_frame = ttk.Frame(root)
fig_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# -----------------------------
# RUN SIMULATION FUNCTION
# -----------------------------
def run_simulation():

    # Get parameters
    Ml = float(entries["Ml"].get())
    Au = float(entries["Au"].get())
    Al = float(entries["Al"].get())
    T_circadian = float(entries["T_circadian"].get())
    ti_hr = float(entries["ti_hr"].get())
    td_hr = float(entries["td_hr"].get())
    N_days = float(entries["N_days"].get())

    Mu = mu_slider.get()

    # -----------------------------
    # SIMULATION SETTINGS
    # -----------------------------
    dt = 1  # minute
    T = int(60 * T_circadian * N_days)

    time = np.arange(0, T + dt, dt)

    ti = ti_hr * 60
    td = td_hr * 60

    tau_c = T_circadian * 60
    omega = 2 * np.pi / tau_c

    # -----------------------------
    # ARRAYS
    # -----------------------------
    U_vec = np.zeros(len(time))
    L_vec = np.zeros(len(time))

    S = np.zeros(len(time))
    state = np.zeros(len(time))

    S[0] = Ml
    state[0] = 1

    # -----------------------------
    # SIMULATION LOOP
    # -----------------------------
    for i in range(1, len(time)):

        # Circadian thresholds
        U = Mu + Au * np.cos(omega * time[i])
        L = Ml + Al * np.cos(omega * time[i])

        U_vec[i] = U
        L_vec[i] = L

        # State transitions
        if S[i - 1] >= U:
            state[i] = 1  # sleep

        elif S[i - 1] <= L:
            state[i] = 0  # wake

        else:
            state[i] = state[i - 1]

        # Update S
        if state[i] == 0:

            # Wake -> buildup
            S[i] = S[i - 1] + (1 - S[i - 1]) * (dt / ti)

        else:

            # Sleep -> decay
            S[i] = S[i - 1] - S[i - 1] * (dt / td)

    # Initialize first threshold values
    U_vec[0] = Mu + Au * np.cos(omega * time[0])
    L_vec[0] = Ml + Al * np.cos(omega * time[0])

    # -----------------------------
    # CLEAR OLD FIGURES
    # -----------------------------
    for widget in fig_frame.winfo_children():
        widget.destroy()

    # -----------------------------
    # CREATE FIGURE
    # -----------------------------
    #fig, axes = plt.subplots(2, 1, figsize=(10, 7))
    fig, axes = plt.subplots(3, 1, figsize=(12, 10))

    # -----------------------------
    # PANEL 1
    # -----------------------------
    axes[0].plot(time / 60, S,
                 color="blue",
                 linewidth=2,
                 label="S (Sleep Pressure)")

    axes[0].plot(time / 60, U_vec,
                 color="red",
                 linestyle="--",
                 linewidth=2,
                 label="U (Upper Threshold)")

    axes[0].plot(time / 60, L_vec,
                 color="green",
                 linestyle="--",
                 linewidth=2,
                 label="L (Lower Threshold)")

    axes[0].set_title("Two-Process Sleep Model")
    axes[0].set_xlabel("Time (hours)")
    axes[0].set_ylabel("Level")
    axes[0].set_ylim(0, 1)

    axes[0].legend()

    # -----------------------------
    # PANEL 2
    # -----------------------------
    axes[1].plot(time / 60,
                 state,
                 color="black",
                 linewidth=2)

    axes[1].set_title("Sleep/Wake State")
    axes[1].set_xlabel("Time (hours)")
    axes[1].set_ylabel("State")
    axes[1].set_ylim(-0.1, 1.1)

    axes[1].set_yticks([0, 1])
    axes[1].set_yticklabels(["Wake", "Sleep"])

    plt.tight_layout()

    # -----------------------------
    # PANEL 3 : DOUBLE-PLOTTED ACTOGRAM
    # -----------------------------

    # Convert to binary sleep signal
    sleep_signal = state.copy()

    # Double-plot settings
    hours_per_day = int(T_circadian)
    mins_per_day = int(hours_per_day * 60)

    n_days = int(len(time) / mins_per_day)

    actogram = []

    for day in range(n_days - 1):

        start1 = day * mins_per_day
        end1 = start1 + mins_per_day

        start2 = end1
        end2 = start2 + mins_per_day

        row = np.concatenate([
            sleep_signal[start1:end1],
            sleep_signal[start2:end2]
        ])

        actogram.append(row)

    actogram = np.array(actogram)

    # Plot actogram
    # -----------------------------
    # ADD SPACING BETWEEN DAYS
    # -----------------------------

    gap = 5  # number of blank rows between days

    rows_with_gap = []

    for row in actogram:

        rows_with_gap.append(row)

        # Add blank separator row(s)
        for _ in range(gap):
            rows_with_gap.append(np.zeros_like(row) * np.nan)

    actogram_spaced = np.array(rows_with_gap)

    # -----------------------------
    # CORRECT DAY LABELS
    # -----------------------------

    day_positions = []

    for d in range(n_days - 1):
        pos = d * (gap + 1)

        day_positions.append(pos)

    axes[2].set_yticks(day_positions)
    axes[2].set_yticklabels(np.arange(1, n_days))

    # Plot spaced actogram
    im = axes[2].imshow(
        actogram_spaced,
        aspect='auto',
        cmap='Greys',
        interpolation='nearest',
        origin='upper'
    )

    # Make NaN rows white
    im.cmap.set_bad(color='white')

    # X-axis labels
    xticks = np.arange(0, 2 * mins_per_day + 1, 6 * 60)

    xtick_labels = [
        str(int(x / 60) % hours_per_day)
        for x in xticks
    ]

    axes[2].set_xticks(xticks)
    axes[2].set_xticklabels(xtick_labels)

    axes[2].set_xlabel("Circadian Time (Double-Plotted)")
    axes[2].set_ylabel("Days")

    axes[2].set_title("Double-Plotted Sleep Actogram")

    # -----------------------------
    # DISPLAY FIGURE
    # -----------------------------
    canvas = FigureCanvasTkAgg(fig, master=fig_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# -----------------------------
# RUN BUTTON
# -----------------------------
run_button = tk.Button(
    input_frame,
    text="Run Simulation",
    command=run_simulation,
    bg="lightblue",
    font=("Arial", 12, "bold")
)

run_button.grid(
    row=mu_row + 1,
    column=0,
    columnspan=2,
    pady=20
)

# -----------------------------
# RUN INITIAL SIMULATION
# -----------------------------
run_simulation()

# -----------------------------
# START GUI
# -----------------------------
root.mainloop()