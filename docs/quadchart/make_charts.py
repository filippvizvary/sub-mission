#!/usr/bin/env python3
"""Quad-chart charts for sub-mission (AMAVET finale).

Every curve here is a COMPUTATION from the repo models, not a measurement:
  - rotor shaft power: Cp 0.393 / TSR 5 / D 220 mm, the rotor of record that
    sim/rotor_check.py validates (7.46 W at 1.0 m/s).
  - generator: T-Motor GB2208 KV128, R_phase 14.4 ohm, max-power-transfer
    bound P = 3*E_ph_rms^2/(4*R_ph) with E_ll_pk = rpm/KV.
  - coupling: the sim/clutch_check.py rows (8 x N52 D10x5, 8 mm pitch 28 mm).
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter

OUT = "charts"
RHO = 1000.0
R = 0.110           # rotor radius m
AREA = np.pi * R**2
CP = 0.393          # rotor of record
TSR = 5.0
TAU_SEAL, TAU_VISC = 1.0e-3, 2.0e-5
KV = 128.0          # rpm/V
R_PH = 14.4         # ohm per phase
VF = 0.35

INK = "#1c1c1c"
GRID = "#d8d6d0"
ACCENT = "#0b5f8a"
ACCENT2 = "#b4560f"


def shaft_power(v):
    omega = TSR * v / R
    p_hyd = 0.5 * RHO * AREA * v**3 * CP
    return np.maximum(p_hyd - (TAU_SEAL + TAU_VISC * omega) * omega, 0.0)


def elec_power(v):
    rpm = TSR * v / R * 60.0 / (2 * np.pi)
    e_ll_pk = rpm / KV                       # V, line-to-line peak
    e_ph_rms = e_ll_pk / np.sqrt(6.0)
    return 3 * e_ph_rms**2 / (4 * R_PH)


def style(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(INK)
        ax.spines[s].set_linewidth(0.8)
    ax.tick_params(colors=INK, labelsize=9, width=0.8, length=3)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: ("%g" % v).replace(".", ",")))
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: ("%g" % v).replace(".", ",")))
    ax.grid(True, color=GRID, lw=0.6)
    ax.set_axisbelow(True)


# ---------------------------------------------------------------- chart 1
v = np.linspace(0.15, 1.5, 400)
fig, ax = plt.subplots(figsize=(3.40, 2.32), dpi=350)
ax.semilogy(v, shaft_power(v) * 1e3, color=ACCENT2, lw=1.8,
            label="rotor na hriadeli")
ax.semilogy(v, elec_power(v) * 1e3, color=ACCENT, lw=1.8,
            label="generátor GB2208 + MPPT")
ax.axhline(28 / 86400 * 1e3, color="#7a1f1f", lw=1.3, ls="--")
ax.text(0.17, 28 / 86400 * 1e3 * 1.35, "spotreba 28 J/deň = 0,32 mW",
        fontsize=10, color="#7a1f1f")
ax.set_xlabel("rýchlosť toku [m/s]", fontsize=10)
ax.set_ylabel("výkon [mW]", fontsize=10)
ax.set_xlim(0.15, 1.5)
ax.set_ylim(0.2, 4e4)
ax.legend(fontsize=9.5, frameon=False, loc="upper left")
style(ax)
fig.tight_layout(pad=0.3)
fig.savefig(f"{OUT}/energia.png", facecolor="white")
plt.close(fig)

# ---------------------------------------------------------------- chart 2
gap = np.array([4.0, 4.2, 5.0, 6.0, 7.0, 8.0])
slip = np.array([1.062, 1.000, 0.789, 0.596, 0.457, 0.355])
fig, ax = plt.subplots(figsize=(2.05, 2.32), dpi=350)
pos = np.arange(len(gap))
bars = ax.bar(pos, slip, color=ACCENT, width=0.62)
for b, s in zip(bars, slip):
    ax.text(b.get_x() + b.get_width() / 2, s + 0.03, f"{s:.2f}".replace(".", ","),
            ha="center", fontsize=9.5, color=INK)
ax.axhline(0.1624, color="#7a1f1f", lw=1.3, ls="--")
style(ax)
ax.set_xticks(pos)
ax.set_xticklabels([f"{g:.1f}".replace(".", ",") for g in gap], fontsize=8.2,
                   rotation=45, ha="right", rotation_mode="anchor")
ax.annotate("0,16", xy=(1.015, 0.1624), xycoords=("axes fraction", "data"),
            fontsize=8.8, color="#7a1f1f", ha="left", va="center",
            annotation_clip=False)
ax.set_xlim(-0.62, 5.55)
ax.set_xlabel("medzera [mm]", fontsize=9.8)
ax.set_ylabel("sklzový moment [N·m]", fontsize=8.8)
ax.set_ylim(0, 1.2)
fig.tight_layout(pad=0.3)
fig.savefig(f"{OUT}/spojka.png", facecolor="white")
plt.close(fig)

# ---------------------------------------------------------------- chart 3
fig, ax = plt.subplots(figsize=(2.05, 2.32), dpi=350)
flows = [0.5, 1.0, 1.5]
need = np.full(3, 28.0)
harv = np.array([elec_power(f) * 86400 for f in flows])
x = np.arange(3)
ax.bar(x - 0.19, harv, width=0.36, color=ACCENT, label="zisk/deň")
ax.bar(x + 0.19, need, width=0.36, color="#8a8f96", label="spotreba/deň")
for xi, h in zip(x, harv):
    ax.text(xi - 0.19, h * 1.25, f"{h:.0f}", ha="center", fontsize=9.5, color=INK)
ax.set_yscale("log")
ax.set_xticks(x)
ax.set_xticklabels([f"{f} m/s" for f in flows], fontsize=8)
ax.set_ylabel("energia za deň [J]", fontsize=8.4)
ax.set_ylim(10, 1e4)
ax.legend(fontsize=7.0, frameon=False, loc="upper left")
style(ax)
fig.tight_layout(pad=0.3)
fig.savefig(f"{OUT}/bilancia.png", facecolor="white")
plt.close(fig)

print("shaft 1.0 m/s: %.2f W" % shaft_power(1.0))
print("elec  1.0 m/s: %.0f mW | 0.5: %.0f mW | 0.3: %.0f mW"
      % (elec_power(1.0) * 1e3, elec_power(0.5) * 1e3, elec_power(0.3) * 1e3))
print("harvest/day 0.5/1.0/1.5: %.0f / %.0f / %.0f J" % tuple(elec_power(np.array(flows)) * 86400))
print("ratio at 0.5 m/s: %.0fx" % (elec_power(0.5) * 86400 / 28))
