import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------

st.set_page_config(
    page_title="Two-Process Sleep Model",
    layout="wide"
)

st.title("Two-Process Sleep Model")

# ---------------------------------------------------
# SIDEBAR INPUTS
# ---------------------------------------------------

st.sidebar.header("Model Parameters")

Mu = st.sidebar.slider(
    "Mu",
    min_value=0.0,
    max_value=1.0,
    value=0.6,
    step=0.01,
    help="Upper threshold mean value"
)

Ml = st.sidebar.number_input(
    "Ml",
    value=0.15,
    step=0.01,
    help="Lower threshold mean value"
)

Au = st.sidebar.number_input(
    "Au",
    value=0.1,
    step=0.01,
    help="Upper threshold oscillation amplitude"
)

Al = st.sidebar.number_input(
    "Al",
    value=0.1,
    step=0.01,
    help="Lower threshold oscillation amplitude"
)

T_circadian = st.sidebar.number_input(
    "T_circadian",
    value=24.0,
    step=0.5,
    help="Circadian period (hours)"
)

ti_hr = st.sidebar.number_input(
    "ti_hr",
    value=18.18,
    step=0.1,
    help="Sleep pressure buildup time constant (hours)"
)

td_hr = st.sidebar.number_input(
    "td_hr",
    value=4.2,
    step=0.1,
    help="Sleep pressure decay time constant (hours)"
)

N_days = st.sidebar.number_input(
    "N_days",
    value=10,
    step=1,
    help="Number of simulated days"
)

# ---------------------------------------------------
# SIMULATION SETTINGS
# ---------------------------------------------------

dt = 1  # minute

T = int(60 * T_circadian * N_days)

time = np.arange(0, T + dt, dt)

ti = ti_hr * 60
td = td_hr * 60

tau_c = T_circadian * 60
omega = 2 * np.pi / tau_c

# ---------------------------------------------------
# ARRAYS
# ---------------------------------------------------

U_vec = np.zeros(len(time))
L_vec = np.zeros(len(time))

S = np.zeros(len(time))
state = np.zeros(len(time))

S[0] = Ml
state[0] = 1

# ---------------------------------------------------
# SIMULATION LOOP
# ---------------------------------------------------

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

# ---------------------------------------------------
# CREATE FIGURE
# ---------------------------------------------------

fig, axes = plt.subplots(3, 1, figsize=(14, 12))

# ---------------------------------------------------
# PANEL 1 : S, U, L
# ---------------------------------------------------

axes[0].plot(
    time / 60,
    S,
    color="blue",
    linewidth=2,
    label="S (Sleep Pressure)"
)

axes[0].plot(
    time / 60,
    U_vec,
    color="red",
    linestyle="--",
    linewidth=2,
    label="U (Upper Threshold)"
)

axes[0].plot(
    time / 60,
    L_vec,
    color="green",
    linestyle="--",
    linewidth=2,
    label="L (Lower Threshold)"
)

axes[0].set_title("Two-Process Sleep Model")

axes[0].set_xlabel("Time (hours)")
axes[0].set_ylabel("Level")

axes[0].set_ylim(0, 1)

axes[0].legend()

# ---------------------------------------------------
# PANEL 2 : STATE
# ---------------------------------------------------

axes[1].plot(
    time / 60,
    state,
    color="black",
    linewidth=2
)

axes[1].set_title("Sleep/Wake State")

axes[1].set_xlabel("Time (hours)")
axes[1].set_ylabel("State")

axes[1].set_ylim(-0.1, 1.1)

axes[1].set_yticks([0, 1])
axes[1].set_yticklabels(["Wake", "Sleep"])

# ---------------------------------------------------
# PANEL 3 : DOUBLE-PLOTTED ACTOGRAM
# ---------------------------------------------------

sleep_signal = state.copy()

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

# ---------------------------------------------------
# ADD GAP BETWEEN DAYS
# ---------------------------------------------------

gap = 4

rows_with_gap = []

for row in actogram:

    rows_with_gap.append(row)

    for _ in range(gap):
        rows_with_gap.append(np.full_like(row, np.nan))

actogram_spaced = np.array(rows_with_gap)

# ---------------------------------------------------
# PLOT ACTOGRAM
# ---------------------------------------------------

im = axes[2].imshow(
    actogram_spaced,
    aspect='auto',
    cmap='Greys',
    interpolation='nearest',
    origin='upper'
)

im.cmap.set_bad(color='white')

# Day labels
day_positions = []

for d in range(n_days - 1):
    pos = d * (gap + 1)
    day_positions.append(pos)

axes[2].set_yticks(day_positions)
axes[2].set_yticklabels(np.arange(1, n_days))

# X-axis
xticks = np.arange(
    0,
    2 * mins_per_day + 1,
    6 * 60
)

xtick_labels = [
    str(int(x / 60) % hours_per_day)
    for x in xticks
]

axes[2].set_xticks(xticks)
axes[2].set_xticklabels(xtick_labels)

axes[2].set_xlabel("Circadian Time (Double-Plotted)")
axes[2].set_ylabel("Days")

axes[2].set_title("Double-Plotted Sleep Actogram")

plt.tight_layout()

# ---------------------------------------------------
# DISPLAY
# ---------------------------------------------------

st.pyplot(fig)

# ---------------------------------------------------
# SUMMARY METRICS
# ---------------------------------------------------

#sleep_percent = np.mean(state) * 100

#st.subheader("Simulation Summary")

#st.write(f"**Percent Sleep:** {sleep_percent:.2f}%")
#st.write(f"**Buildup Time Constant (ti):** {ti_hr:.2f} hr")
#st.write(f"**Decay Time Constant (td):** {td_hr:.2f} hr")