#!/usr/bin/env python3
"""Device schematic for the quad chart: mechanical side and the power/radio
chain, drawn as a block diagram at the physical print size (132 x 39 mm).

The chain itself is the message, so the boxes carry it and the text does not
repeat it. Everything shown is design intent, not a measurement.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = "/home/filip/sub-mission/docs/quadchart/charts/schema.png"

INK = "#1c1c1c"
LINE = "#0b5f8a"
FILL = "#eef4f8"
FILL2 = "#f6f1e9"
GREEN = "#3f7a4a"

fig, ax = plt.subplots(figsize=(5.20, 1.55), dpi=350)
ax.set_xlim(0, 100)
ax.set_ylim(0, 33)


def box(x, y, w, h, text, fill=FILL, edge=LINE, fs=8.0):
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0.3,rounding_size=0.8",
                                linewidth=0.8, edgecolor=edge, facecolor=fill))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fs, color=INK, linespacing=1.25)


def arrow(x1, y1, x2, y2):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>",
                                 mutation_scale=7, color=LINE, lw=0.8,
                                 shrinkA=0, shrinkB=0))


# ---- mechanical row
box(0.5, 21.0, 14.0, 7.0, "rotor\nØ220 mm", FILL2, "#b4560f")
arrow(15.2, 24.5, 17.6, 24.5)
box(18.0, 21.0, 22.0, 7.0, "magnetická spojka\ncez 4 mm stenu")
arrow(40.8, 24.5, 43.2, 24.5)
box(43.6, 21.0, 18.0, 7.0, "BLDC\ngenerátor")
arrow(62.4, 24.5, 64.8, 24.5)
box(65.2, 21.0, 17.5, 7.0, "usmerňovač")

# ---- power / logic row
box(0.5, 11.0, 24.5, 7.0, "2× superkondenzátor\n(20 F / 5,4 V)")
arrow(25.8, 14.5, 28.2, 14.5)
box(28.6, 11.0, 17.0, 7.0, "regulátor\n3,3 V")
arrow(46.4, 14.5, 48.8, 14.5)
box(49.2, 11.0, 14.0, 7.0, "ESP32")
ax.add_patch(FancyArrowPatch((63.9, 14.5), (66.3, 14.5), arrowstyle="<|-|>",
                             mutation_scale=7, color=LINE, lw=0.8,
                             shrinkA=0, shrinkB=0))
box(66.7, 11.0, 17.5, 7.0, "LoRa\n868 MHz")

# ---- rectifier down into the storage row, routed in the gap between rows
ax.plot([73.95, 73.95], [20.8, 19.5], color=LINE, lw=0.8)
ax.plot([12.75, 73.95], [19.5, 19.5], color=LINE, lw=0.8)
arrow(12.75, 19.5, 12.75, 18.2)

# ---- sensors
box(30.0, 2.0, 40.0, 5.5, "senzory: pH, TDS, turbidita, teplota", "#f2f5f2", GREEN)
arrow(56.0, 7.8, 56.0, 10.8)

# ---- water flow
arrow(0.5, 31.0, 13.0, 31.0)
ax.text(14.2, 31.0, "tok vody", fontsize=8.0, color=LINE, va="center", ha="left")

ax.axis("off")
fig.subplots_adjust(0, 0, 1, 1)
fig.savefig(OUT, facecolor="white")
print("wrote", OUT)
