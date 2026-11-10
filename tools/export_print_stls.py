#!/usr/bin/env python3
"""Export the print-ready parts from the assembly into print/.

cad/probe_cq.py exports every part in the ASSEMBLY frame (rotated 90 deg about Y
then Z, translated to the arm tip), which no slicer wants: the part arrives
1.2 m off the origin with its axis along Y. This script undoes that transform,
optionally flips a part so its print face is down, then stands it on z=0 and
centres it on the SHAFT AXIS (not on the bounding-box centre - a three-blade
rotor's bbox centre sits well off the axis, and centring on it puts the bore
eccentric on the plate).

    python3 tools/export_print_stls.py

Run it after every rebuild of cad/probe_cq.py. It refuses to export a part that
is not watertight, and it prints volume + footprint so the slicer numbers can
be sanity-checked against the model.
"""
import os
import sys

import numpy as np
import trimesh

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CQ = os.path.join(ROOT, "cad", "cq")
OUT = os.path.join(ROOT, "print")

# assembly placement applied in probe_cq.py
T = np.array([1200.0, -142.0, -420.0])


def _ry(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def _rz(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


BACK = _ry(-np.pi / 2) @ _rz(-np.pi / 2)

# source part -> (file name, flip 180 deg about X so the print face is down)
PARTS = [
    ("rotor", "01_rotor_vrtula.stl", True),          # aft face down, cone up
    ("pod", "02_barel_pod.stl", False),              # bulkhead down, O-ring up
    ("magcup_wet", "03_magnetovy_pohar_mokry.stl", False),   # pockets up
    ("magcup_dry", "04_magnetovy_pohar_suchy.stl", True),    # pockets up
    ("wet_carrier", "05_nosic_hriadela_klietka.stl", False),  # boss down
    ("cup_washer", "06_podlozka_pohara.stl", False),         # flat ring, print flat
]


def export():
    os.makedirs(OUT, exist_ok=True)
    bad = []
    for src, dst, flip in PARTS:
        m = trimesh.load(os.path.join(CQ, src + ".stl"))
        m.vertices = (m.vertices - T) @ BACK.T
        if flip:
            m.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
        m.apply_translation([0, 0, -m.bounds[0][2]])
        v = m.vertices
        bed = v[np.abs(v[:, 2]) < 0.05]
        if len(bed) < 3:
            raise SystemExit(f"{src}: nothing lies on z=0, cannot orient it")
        axis_x, axis_y = bed[:, 0].mean(), bed[:, 1].mean()
        m.apply_translation([-axis_x, -axis_y, 0])
        if not m.is_watertight:
            bad.append(src)
        m.export(os.path.join(OUT, dst))
        b = m.bounds
        print(f"{dst:34s} {abs(m.volume)/1000:7.1f} cm3  "
              f"{b[1][0]-b[0][0]:6.1f} x {b[1][1]-b[0][1]:6.1f} x {b[1][2]-b[0][2]:6.1f}")
    guide = os.path.join(ROOT, "docs", "PRINT_GUIDE.txt")
    if os.path.exists(guide):
        import shutil
        shutil.copyfile(guide, os.path.join(OUT, "README.txt"))
        print("README.txt <- docs/PRINT_GUIDE.txt")
    if bad:
        sys.exit("NOT watertight, not printable: " + ", ".join(bad))


if __name__ == "__main__":
    export()
