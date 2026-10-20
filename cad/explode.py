#!/usr/bin/env python3
"""
Exploded elevation drawings + coupling section for the sub-mission probe.

Renders orthographic elevations (not perspective), because a drivetrain is a
body of revolution: an elevation with parts separated along the axis is what
a workshop drawing actually looks like, and labels stay readable.

Outputs into the renders dir:
  E1_drivetrain_explode.png
  E2_site_explode.png
  E3_coupling_section.png
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from matplotlib.collections import PolyCollection

CQ = "/home/filip/sub-mission/cad/cq"
OUT = "/home/filip/.hermes/profiles/haven/cache/scratch/renders"
os.makedirs(OUT, exist_ok=True)

# (part, colour, label) - order is the physical order along the flow axis
CHAIN = [
    ("weed_guard",   "#2e7d32", "weed guard"),
    ("rotor",        "#ef6c00", "rotor  3x NACA4412, D220"),
    ("wet_carrier",  "#607d8b", "bearing carrier + PEEK bushings"),
    ("magcup_wet",   "#f9a825", "magnet cup A (wet, 8x N52 potted)"),
    ("pod_seal",     "#795548", "coupling wall 5 mm - no shaft hole"),
    ("magcup_dry",   "#fbc02d", "magnet cup B (dry)"),
    ("generator",    "#c62828", "generator GB2208"),
    ("pod",          "#1565c0", "pod shell OD110"),
    ("cage_adapter", "#455a64", "adapter OD110 -> OD130"),
    ("sensors",      "#00838f", "sensors: pH, DO, TDS, turbidity, temp, level"),
    ("cage",         "#2e7d32", "sensor cage OD130, 12 slots"),
]

SITE = [
    ("site_pole",    "#546e7a", "pole 2.6 m (600 mm driven)"),
    ("site_collar",  "#37474f", "pole collar + anchor plate"),
    ("site_arm",     "#5d4037", "swing arm 1.2 m"),
    ("site_elbow",   "#4e342e", "elbow clamp, 2 bolts"),
    ("site_drop",    "#455a64", "drop tube OD28, cable inside"),
    ("site_clamp",   "#37474f", "collar clamp around pod"),
    ("site_strut",   "#616161", "diagonal strut"),
    ("site_box",     "#1565c0", "dry box"),
    ("site_lid",     "#1976d2", "lid + O-ring"),
    ("site_antenna", "#b71c1c", "868 MHz antenna"),
    ("cable_run",    "#212121", "cable run"),
]


def load(name):
    path = os.path.join(CQ, name + ".stl")
    if not os.path.exists(path):
        return None
    m = trimesh.load(path, force="mesh")
    return m if hasattr(m, "vertices") and len(m.vertices) else None


def elevation(items, path, title, gap, axis="y", elev_axis="z"):
    """Project onto (axis, elev_axis) and separate parts along `axis`."""
    fig, ax = plt.subplots(figsize=(16, 8.5), dpi=140)

    cursor = 0.0
    spans = []
    for i, (name, colour, label) in enumerate(items):
        mesh = load(name)
        if mesh is None:
            spans.append((i, None, label, colour))
            continue
        v = mesh.vertices.copy()
        lo, hi = v[:, 1].min(), v[:, 1].max() if axis == "y" else (None, None)
        width = hi - lo
        shift = cursor - lo
        v[:, 1] += shift
        tris = v[mesh.faces]
        p2 = tris[:, :, [1, 2]]          # (along axis, height)
        depth = tris[:, :, 0].mean()
        poly = PolyCollection(p2, facecolors=colour, edgecolors="#1a1a1a",
                              linewidths=0.06, alpha=0.95, zorder=3)
        ax.add_collection(poly)
        spans.append((i, (v[:, 1].min(), v[:, 1].max(), v[:, 2].min(), v[:, 2].max()),
                      label, colour))
        cursor += width + gap

    # labels: alternate above / below, vertical leader
    for i, span, label, colour in spans:
        if span is None:
            continue
        y0, y1, z0, z1 = span
        yc = (y0 + y1) / 2
        above = (i % 2 == 0)
        zl = z1 + 26 if above else z0 - 26
        ax.annotate(label, xy=(yc, z1 if above else z0), xytext=(yc, zl),
                    fontsize=8.2, ha="center",
                    va="bottom" if above else "top", color=colour,
                    weight="bold",
                    arrowprops=dict(arrowstyle="-", lw=0.7, color=colour,
                                    shrinkA=1, shrinkB=2))
        ax.text(y0, -115, f"{i + 1}", fontsize=7.5, color="#555", ha="center")

    ax.autoscale_view()
    ax.set_aspect("equal")
    ax.set_xlabel("flow axis / assembly order  (mm)")
    ax.set_ylabel("height (mm)")
    ax.set_title(title + "\nnumbers show the assembly order", fontsize=12, pad=12)
    ax.grid(alpha=0.15, lw=0.5)
    ax.tick_params(labelsize=7)
    fig.tight_layout()
    fig.savefig(path, dpi=140, facecolor="white")
    plt.close(fig)
    print("wrote", path)


def coupling_section(path):
    # draw the pod FIRST so the coupling stack is not hidden behind the shell
    names = ["pod", "wet_carrier", "magcup_wet", "pod_seal", "magcup_dry"]
    colours = {"wet_carrier": "#607d8b", "magcup_wet": "#f9a825",
               "pod_seal": "#795548", "magcup_dry": "#fbc02d", "pod": "#1565c0"}
    labels = {"wet_carrier": "bearing carrier (wet, PEEK bushings)",
              "magcup_wet": "cup A - wet side, 8x N52 potted in epoxy",
              "pod_seal": "coupling wall 5 mm - SOLID, no shaft hole",
              "magcup_dry": "cup B - dry side, inside the pod",
              "pod": "pod shell OD110 - pressure vessel"}

    pod = load("pod")
    z0 = pod.bounds.mean(axis=0)[2]      # pod axis height
    y0 = pod.bounds.mean(axis=0)[1]      # pod mid along the axis

    fig, ax = plt.subplots(figsize=(12, 7), dpi=140)
    drawn = {}
    for name in names:
        mesh = load(name)
        if mesh is None:
            continue
        sec = mesh.section(plane_origin=mesh.bounds.mean(axis=0),
                           plane_normal=[1.0, 0.0, 0.0])
        if sec is None:
            continue
        for poly in sec.discrete:
            p = np.array(poly)
            x = p[:, 1] - y0
            y = p[:, 2] - z0
            ax.fill(x, y, color=colours[name], alpha=0.8,
                    edgecolor="#111", lw=0.6)
            drawn.setdefault(name, [x.min(), x.max(), y.min(), y.max()])

    ax.set_aspect("equal")
    ax.set_xlabel("along the axis (mm, 0 = pod middle)")
    ax.set_ylabel("radial (mm)")
    ax.set_title("Magnetic coupling - section through the axis\n"
                 "cup A wet | 5 mm solid wall | cup B dry: nothing pierces the shell",
                 fontsize=11)

    # fixed label slots so nothing collides and each arrow lands on its own part
    slots = {
        "wet_carrier": (-150, 55),
        "magcup_wet":  (-105, -55),
        "pod_seal":    (-30, 70),
        "magcup_dry":  (10, -55),
        "pod":         (95, 62),
    }
    # explicit anchors from the design table, not bbox centres (glands skew those)
    anchors = {"wet_carrier": (-110, 6), "magcup_wet": (-70, 20),
               "pod_seal": (-59.5, 30), "magcup_dry": (-50, 22),
               "pod": (30, 55)}
    for name, (xa, xb, ya, yb) in drawn.items():
        tx, ty = slots.get(name, (0, 70))
        ax.annotate(labels[name],
                    xy=anchors.get(name, ((xa + xb) / 2, yb)),
                    xytext=(tx, ty),
                    fontsize=8.5, weight="bold", ha="center",
                    arrowprops=dict(arrowstyle="->", lw=0.9, color="#333",
                                    connectionstyle="arc3,rad=0.15"),
                    bbox=dict(boxstyle="round,pad=0.25", fc="white",
                              ec=colours[name], alpha=0.98))

    ax.grid(alpha=0.2, lw=0.5)
    ax.set_ylim(-80, 90)
    fig.tight_layout()
    fig.savefig(path, dpi=140, facecolor="white")
    plt.close(fig)
    print("wrote", path)


def main():
    elevation(CHAIN, os.path.join(OUT, "E1_drivetrain_explode.png"),
              "Wet drivetrain - exploded elevation", 55)
    elevation(SITE, os.path.join(OUT, "E2_site_explode.png"),
              "Bank structure - exploded elevation", 45)
    coupling_section(os.path.join(OUT, "E3_coupling_section.png"))


if __name__ == "__main__":
    main()
