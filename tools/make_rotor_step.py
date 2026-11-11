#!/usr/bin/env python3
"""Build the rotor on its own, with the root corner fills, and export a STEP for FreeCAD.

The rotor in probe_cq.py lives in the assembly frame (axis at x 1200, z -149), which is
useless for hand editing. This rebuilds the same geometry from the same functions and puts
it in a sensible frame: axis on +Z, aft face (the one that prints on the bed) at z = 0.

The three lower root-corner fills are added here as real cylinders, not as a mesh patch, so
the STEP has clean cylindrical faces to select and fillet in FreeCAD.

    python3 tools/make_rotor_step.py [out_basename]
"""
import importlib.util
import math
import os
import sys

import cadquery as cq

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILL_R = 6.0
FILL_OUTER = 34.6           # clipped at the blade's own reach
CORNER_PHI = (76.0, 196.0, 316.0)   # lower corner of each blade, from the ray casts
HUB_AFT = 28.0              # hub spans 0..28 in the model's local frame


def find_lower_corners(stl_path):
    """The lower corner of each blade, measured in whatever frame the mesh is in."""
    import trimesh
    sys.path.insert(0, os.path.join(ROOT, "tools"))
    import fill_corners as fc
    m = trimesh.load(stl_path)
    out = []
    for centre, half in fc.blade_runs(m):
        found = []
        for side in (-1, 1):
            phi = (centre + side * (half - 1.5)) % 360.0
            zlo = None
            for rr in (32.6, 33.2, 34.0):
                zlo, zhi = fc.blade_z(m, phi, rr)
                if zlo is not None:
                    break
            if zlo is not None:
                found.append((phi, zlo))
        if found:
            out.append(min(found, key=lambda t: t[1])[0])
    return out


def load_model():
    spec = importlib.util.spec_from_file_location("pcq", os.path.join(ROOT, "cad", "probe_cq.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pcq"] = mod
    spec.loader.exec_module(mod)
    return mod


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "rotor_edit"
    mod = load_model()

    body = cq.Workplane("XY").add(mod.make_hub().val())
    for i in range(mod.BLADES):
        b = mod.make_blade().rotate((0, 0, 0), (0, 0, 1), i * 360.0 / mod.BLADES)
        body = body.union(b.val(), clean=True)
    body = body.union(
        cq.Workplane("XY").circle(mod.HUB_D / 2).workplane(offset=-40).circle(6).loft().val(),
        clean=True)

    # Find the corners in THIS frame. The print STL is the model's part after an assembly
    # placement, so its azimuths (76/196/316) do not apply here - hard-coding them put the
    # fills 40 deg off, next to the blades instead of at their corners.
    tmp = os.path.join(ROOT, "cad", "parts", "_scan.stl")
    cq.exporters.export(body, tmp, tolerance=0.05, angularTolerance=0.2)
    corners = find_lower_corners(tmp)
    print(f"lower corners in this frame: {[round(c,1) for c in corners]}")
    os.remove(tmp)

    # corner fills: from the aft face down the hub wall to the blade's underside
    fills = 0
    for phi in corners:
        a = math.radians(phi)
        cx, cy = mod.HUB_D / 2 * math.cos(a), mod.HUB_D / 2 * math.sin(a)
        # print z 0..4.44 is the model's 23.56..28 (the print frame is the model's, flipped)
        h = 4.45
        # exactly to the aft face: that IS the print's z 0, so the fill stands on the bed.
        # Overshooting by 0.3 mm put the whole model 0.3 mm below the bed after the flip.
        cyl = (cq.Workplane("XY").workplane(offset=HUB_AFT - h)
               .center(cx, cy).circle(FILL_R).extrude(h))
        clip = (cq.Workplane("XY").workplane(offset=HUB_AFT - h - 1.0)
                .circle(FILL_OUTER).extrude(h + 3.0))
        cyl = cyl.intersect(clip)
        body = body.union(cyl.val(), clean=False)     # keep the cylinder's own face
        fills += 1
    print(f"{fills} corner fills, r {FILL_R} mm, standing on the aft face")

    # frame: flip so the aft face is at z 0 (the print frame), axis on +Z
    solid = body.val()
    part = cq.Workplane("XY").add(solid)
    part = part.rotate((0, 0, 0), (1, 0, 0), 180)
    bb = part.val().BoundingBox()
    part = part.translate((0, 0, -bb.zmin))

    s = part.val()
    bb = s.BoundingBox()
    base = os.path.join(ROOT, "cad", "parts", out)
    os.makedirs(os.path.dirname(base), exist_ok=True)
    cq.exporters.export(part, base + ".step")
    cq.exporters.export(part, base + ".stl", tolerance=0.02, angularTolerance=0.1)
    print(f"{out}.step  {s.Volume()/1000:.2f} cm3  "
          f"{bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm  "
          f"z {bb.zmin:.2f}..{bb.zmax:.2f}  faces {len(s.Faces())}  valid {s.isValid()}")


if __name__ == "__main__":
    main()
