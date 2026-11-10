#!/usr/bin/env python3
"""Assembly animation of the sub-mission pod chain.

Renders the real exported geometry in the order it is actually assembled, one
part at a time, each sliding in from the side it comes from, with the camera
drifting so a part never hides behind another. Output: print/zlozenie.mp4 plus
two stills (exploded + assembled).

    python3 tools/assembly_anim.py

Parts are subsampled to ~2000 triangles each: matplotlib is the renderer, so the
frames are shaded by hand (colour * a lambert term) rather than by matplotlib's
lighting, which does not exist for Poly3DCollection.
"""
import os
import shutil
import subprocess
import sys

import numpy as np
import trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CQ = os.path.join(ROOT, "cad", "cq")
OUT = os.path.join(ROOT, "print")
TMP = os.path.join(os.path.expanduser("~"), ".hermes", "profiles", "haven", "cache", "scratch", "anim_frames")
FPS = 24
TRI_BUDGET = 2200

# (file, label, colour, entry offset along +Y in mm)
STEPS = [
    ("pod",         "barel (plasť + dno = magneticka stena)", (0.13, 0.45, 0.30), +520),
    ("cup_washer",  "tlačena podlozka do dna",               (0.90, 0.85, 0.45), -300),
    ("wet_carrier", "pavuk - drzi obe igus lozska",          (0.15, 0.55, 0.60), -300),
    ("magcup_wet",  "MOKRY pohar spojky",                    (0.55, 0.58, 0.62), -300),
    ("magnets_wet", "8x magnet N52",                          (0.85, 0.25, 0.25), -300),
    ("shaft",       "mokry hriadeľ Ø5",                       (0.75, 0.75, 0.78), -300),
    ("collar_up",   "zarazka pred pavukom",                   (0.85, 0.60, 0.25), -300),
    ("collar_dn",   "zarazka za pavukom",                     (0.85, 0.60, 0.25), -300),
    ("rotor",       "vrtula + hub + nosovy kuzel",            (1.00, 0.45, 0.10), -460),
    ("magcup_dry",  "SUCHY pohar spojky",                     (0.50, 0.53, 0.58), +520),
    ("magnets_dry", "8x magnet N52",                           (0.85, 0.25, 0.25), +520),
    ("dry_shaft",   "suchy hriadeľ Ø5",                        (0.75, 0.75, 0.78), +520),
    ("dry_bearing", "lozisko 695ZZ",                           (0.80, 0.80, 0.85), +520),
    ("dry_collar",  "zarazka o lozisko",                       (0.85, 0.60, 0.25), +520),
    ("oldham",      "Oldham - kruti, ale netlaci",             (0.70, 0.35, 0.75), +520),
    ("generator",   "motor GB2208",                            (0.20, 0.35, 0.70), +520),
    ("engine_block", "motorovy blok + privruba + O-kruzok",    (0.30, 0.50, 0.70), +620),
]

LIGHT = np.array([0.4, -0.7, 0.6])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def load(name):
    m = trimesh.load(os.path.join(CQ, name + ".stl"))
    comps = m.split(only_watertight=False)
    if len(comps) > 1:
        m = max(comps, key=lambda c: abs(c.volume))
    # NO subsampling: striding triangles punches holes in every surface and the
    # render then looks transparent. matplotlib copes with the full 60-70k.
    return m.triangles.copy(), m.bounds


def shade_faces(tris, colour):
    """Flat lambert per triangle; matplotlib has no lighting for Poly3D sets."""
    e1 = tris[:, 1] - tris[:, 0]
    e2 = tris[:, 2] - tris[:, 0]
    n = np.cross(e1, e2)
    ln = np.linalg.norm(n, axis=1)
    ln[ln == 0] = 1.0
    n = n / ln[:, None]
    lam = np.abs(n @ LIGHT)
    k = 0.45 + 0.55 * lam
    base = np.array(colour)
    return np.clip(k[:, None] * base[None, :], 0, 1)


def main():
    os.makedirs(TMP, exist_ok=True)
    for f in os.listdir(TMP):
        os.remove(os.path.join(TMP, f))
    data = {}
    lo = np.array([1e9, 1e9, 1e9])
    hi = -lo.copy()
    for name, label, colour, off in STEPS:
        tris, b = load(name)
        data[name] = (tris, colour, off)
        lo = np.minimum(lo, b[0])
        hi = np.maximum(hi, b[1])
    mid = (lo + hi) / 2
    span = (hi - lo).max() * 0.62
    y_axis = 1  # the pod chain runs along world +Y

    plt.rcParams["font.size"] = 13
    frames = 0

    def draw(visible, azim, title):
        """One Poly3DCollection for ALL parts: matplotlib sorts polygons within a
        collection, not between collections, so per-part collections draw the
        internals straight through the shell. Depth-sorting has to happen on the
        whole triangle soup at once."""
        fig = plt.figure(figsize=(10, 6.6))
        ax = fig.add_subplot(111, projection="3d")
        alltris, allcols = [], []
        lo2 = np.array([1e9, 1e9, 1e9])
        hi2 = -lo2.copy()
        for name in visible:
            tris, colour, shift = visible[name]
            t = tris.copy()
            t[:, :, y_axis] += shift
            alltris.append(t)
            allcols.append(shade_faces(t, colour))
            lo2 = np.minimum(lo2, t.reshape(-1, 3).min(0))
            hi2 = np.maximum(hi2, t.reshape(-1, 3).max(0))
        tris = np.concatenate(alltris)
        cols = np.concatenate(allcols)
        pc = Poly3DCollection(tris, facecolors=cols, edgecolors="none", linewidths=0)
        pc.set_sort_zpos(0)
        ax.add_collection3d(pc)
        c = (lo2 + hi2) / 2
        r = (hi2 - lo2).max() / 2 * 1.02
        ax.set_xlim(c[0] - r, c[0] + r)
        ax.set_ylim(c[1] - r, c[1] + r)
        ax.set_zlim(c[2] - r, c[2] + r)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev=14, azim=azim)
        ax.set_axis_off()
        ax.text2D(0.02, 0.03, title, transform=ax.transAxes, color="#111111",
                  fontsize=12)
        path = os.path.join(TMP, f"f{frames:05d}.png")
        fig.savefig(path, dpi=95, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        return path

    placed = {}
    total = len(STEPS)
    azim = -75.0
    for i, (name, label, colour, off) in enumerate(STEPS):
        tris, colour, _ = data[name]
        for k in range(9):                       # slide in
            f = k / 8.0
            shift = off * (1.0 - f)
            placed[name] = (tris, colour, shift)
            draw(placed, azim, f"krok {i+1}/{total}  -  {label}")
            frames += 1
        placed[name] = (tris, colour, 0.0)
        for k in range(4):                        # hold, camera drifts
            azim += 1.2
            draw(placed, azim, f"krok {i+1}/{total}  -  {label}")
            frames += 1

    for k in range(30):                           # final orbit
        azim += 1.6
        draw(placed, azim, "zlozene")
        frames += 1

    mp4 = os.path.join(OUT, "zlozenie.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                    "-i", os.path.join(TMP, "f%05d.png"), "-c:v", "libx264",
                    "-pix_fmt", "yuv420p", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
                    mp4], check=True)
    # stills: fully exploded and fully assembled
    snap = dict(placed)
    for name, label, colour, off in STEPS:
        snap[name] = (data[name][0], colour, off * 0.55)
    p1 = draw(snap, -60, "rozlozene")
    shutil.move(p1, os.path.join(OUT, "rozlozene.png"))
    p2 = draw(placed, -55, "zlozene")
    shutil.move(p2, os.path.join(OUT, "zlozene.png"))
    print(f"{frames} frames -> {mp4}")


if __name__ == "__main__":
    main()
