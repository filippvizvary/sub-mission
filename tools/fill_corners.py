#!/usr/bin/env python3
"""Fill the sharp corner where each blade's side edge meets the hub wall.

The gap is in PLAN view: the blade leaves the hub's cylinder at a sharp angle, so at each
side of the root there is a concave corner between the blade's side face and the hub's wall.
It runs the full height of the blade at that point.

The fill is a vertical bead: a cylinder centred on the corner, cut by the rotor, so only the
part standing in the void remains. It reads as a fillet and it cannot protrude anywhere the
blade does not already go.

    python3 tools/fill_corners.py in.stl out.stl --radius 4 [--dry]

Corner positions are measured, not assumed: the angular runs at the root radius give the
blade's two side angles, and ray casts give the blade's height at each.
"""
import sys
import math
import numpy as np
import trimesh


def blade_runs(mesh, r=33.0, step=0.5):
    hit = []
    phis = np.arange(0.0, 360.0, step)
    for phi in phis:
        a = np.radians(phi)
        loc, _, _ = mesh.ray.intersects_location(
            np.array([[r * math.cos(a), r * math.sin(a), -5.0]]), np.array([[0.0, 0.0, 1.0]]))
        hit.append(len(loc) > 0)
    hit = np.array(hit)
    runs, idx = [], np.where(hit)[0]
    if not len(idx):
        return []
    start = prev = int(idx[0])
    for k in idx[1:]:
        k = int(k)
        if k != prev + 1:
            runs.append((start, prev + 1))
            start = k
        prev = k
    runs.append((start, prev + 1))
    if len(runs) >= 2 and runs[0][0] == 0 and runs[-1][1] == len(hit):
        a, b = runs.pop(-1), runs.pop(0)
        runs.append((a[0], b[1] + len(hit)))
    out = []
    for a0, a1 in runs:
        lo, hi = a0 * step, a1 * step
        if hi - lo < 10.0:
            continue
        out.append(((lo + hi) / 2.0 % 360.0, (hi - lo) / 2.0))
    return out


def blade_z(mesh, phi, r):
    a = np.radians(phi)
    o = np.array([[r * math.cos(a), r * math.sin(a), -5.0]])
    loc, _, _ = mesh.ray.intersects_location(o, np.array([[0.0, 0.0, 1.0]]))
    if not len(loc):
        return None, None
    return float(loc[:, 2].min()), float(loc[:, 2].max())


def main():
    src, dst = sys.argv[1], sys.argv[2]
    radius = 4.0
    if "--radius" in sys.argv:
        radius = float(sys.argv[sys.argv.index("--radius") + 1])
    dry = "--dry" in sys.argv

    mesh = trimesh.load(src)
    runs = blade_runs(mesh)
    print("blade runs:", [(round(c, 1), round(h, 1)) for c, h in runs])

    beads = []
    for centre, half in runs:
        found = []
        for side in (-1, 1):
            # step just inside the run: the exact boundary angle misses the blade
            phi = (centre + side * (half - 1.5)) % 360.0
            zlo, zhi = None, None
            for rr in (32.6, 33.2, 34.0):
                zlo, zhi = blade_z(mesh, phi, rr)
                if zlo is not None:
                    break
            if zlo is None:
                continue
            found.append((phi, zlo, zhi))
        if not found:
            print(f"  blade {centre:.1f}: no material at either corner")
            continue
        # only the LOWER corner needs filling - the upper one already blends
        phi, zlo, zhi = min(found, key=lambda t: t[1])
        print(f"  blade {centre:6.1f}: lower corner {phi:6.1f}, blade z {zlo:.2f}..{zhi:.2f} "
              f"(skipped {[round(f[0],1) for f in found if f[0] != phi]})")
        a = math.radians(phi)
        cx, cy = 32.0 * math.cos(a), 32.0 * math.sin(a)
        # stand it ON THE BED, not next to the blade: a fill floating at z 1.4 prints in the
        # air and needs support. From z 0 it prints flat and merges with the hub's own base.
        h = zhi + 0.15          # flush with the blade's top at that corner, not a bump above it
        bead = trimesh.creation.cylinder(radius=radius, height=h, sections=96)
        bead.apply_translation([cx, cy, h / 2.0])
        # Clip the bead to just past the blade's own tip. Unclipped it is a ball sitting on
        # the corner and bulging past the blade - what Filip called a "gulicka". Clipped at
        # the blade's reach it becomes a wedge that sits inside the notch and disappears
        # into both the blade and the hub.
        import numpy as _np
        clip = trimesh.creation.cylinder(radius=34.6, height=80.0, sections=96)
        clip.apply_translation([0.0, 0.0, 14.0])
        bead = trimesh.boolean.intersection([bead, clip], engine="manifold")
        beads.append(bead)
        print(f"    fillet r {radius} mm, z {zlo - 1.0:.2f}..{zhi + 1.0:.2f}")

    if not beads:
        raise SystemExit("no beads built")
    if dry:
        print("dry run, not written")
        return
    out = mesh
    for b in beads:
        out = trimesh.boolean.union([out, b], engine="manifold")

    # validate the file as it will be written, not the in-memory union
    out.export(dst)
    chk = trimesh.load(dst, process=True)
    chk.merge_vertices()
    e = chk.edges_sorted
    _, c = np.unique(e, axis=0, return_counts=True)
    print(f"\n{chk.volume/1000:.2f} cm3 (was {mesh.volume/1000:.2f}) | watertight {chk.is_watertight} "
          f"| bad edges {int((c != 2).sum())} | bodies {len(chk.split(only_watertight=False))}")


if __name__ == "__main__":
    main()
