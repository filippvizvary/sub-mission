#!/usr/bin/env python3
"""Export a part in ITS OWN frame: axis on +Z through the origin, sitting on z=0.

Why this exists: parts in probe_cq.py live in the assembly frame, where the pod lies
horizontal and the rotor's axis is the line x=1200, z=-149 along -Y. Every attempt to
select topology there ended in radius filters that matched nothing, because "radius from
the world origin" is meaningless for a part that sits a metre away from it. Work in the
part's own frame and face/edge selection becomes trivial.

    python3 tools/export_part_step.py rotor rotor_clamp cup_clamp_wet

Writes cad/parts/<name>.step and cad/parts/<name>.stl, both centred on the part's axis.
"""
import importlib.util
import math
import os
import sys
import contextlib
import io

import cadquery as cq

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "cad", "parts")


def load_model():
    """Build probe_cq.py without letting its assembly checks print over everything."""
    src = open(os.path.join(ROOT, "cad", "probe_cq.py")).read()
    spec = importlib.util.spec_from_file_location("pcq", os.path.join(ROOT, "cad", "probe_cq.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["pcq"] = mod
    with contextlib.redirect_stdout(io.StringIO()):
        spec.loader.exec_module(mod)
    return mod


def axis_of(wp):
    """Find the part's axis from its cylindrical faces.

    The largest-radius cylinder that is coaxial with the bore is the safest bet: on this
    pod it is the hub's Ø64 or a clamp's Ø22 sleeve. Returns (point, direction).
    """
    solid = wp.val()
    cands = []
    for f in solid.Faces():
        if f.geomType() != "CYLINDER":
            continue
        try:
            r = f.radius()
            ax = f.axisOfRotation()
        except Exception:
            continue
        cands.append((r, ax.get("location"), ax.get("direction")))
    if not cands:
        raise SystemExit("no cylindrical face - cannot find the axis automatically")
    # the bore of every rotating part is coaxial, so group by direction+line and take the
    # group with the biggest face count
    groups = {}
    for r, loc, d in cands:
        key = (round(abs(d.x), 3), round(abs(d.y), 3), round(abs(d.z), 3))
        groups.setdefault(key, []).append((r, loc, d))
    key = max(groups, key=lambda k: len(groups[k]))
    r, loc, d = max(groups[key], key=lambda t: t[0])
    return loc, d


def to_part_frame(solid):
    """Move so the axis is +Z through the origin."""
    loc, d = axis_of(solid)
    # direction is axis-aligned in this model; pick the dominant component
    comps = [abs(d.x), abs(d.y), abs(d.z)]
    axis = comps.index(max(comps))
    part = solid
    if axis == 1:                      # along Y -> rotate about X
        part = part.rotate((0, 0, 0), (1, 0, 0), -90 if d.y > 0 else 90)
        shift = (-loc.x, 0.0, loc.y if d.y > 0 else -loc.y)
    elif axis == 0:                    # along X -> rotate about Y
        part = part.rotate((0, 0, 0), (0, 1, 0), 90 if d.x > 0 else -90)
        shift = (0.0, -loc.y, -loc.x if d.x > 0 else loc.x)
    else:
        shift = (-loc.x, -loc.y, 0.0)
    bb = part.val().BoundingBox()
    shift = (shift[0], shift[1], -bb.zmin)
    return part.translate(shift), (2 * max(bb.xlen, bb.ylen) / 2.0)


# Parts are built at the origin and then PLACED in the assembly. Undo the placement here
# instead of trying to re-detect the axis from the geometry: the model's own frame is the
# ground truth, and it is exact.
UNPLACE = {
    "rotor": (0.0, 0.0, 7.0),      # built 0..28, then shifted -7 for the axial layout
}


def main(names):
    os.makedirs(OUT, exist_ok=True)
    mod = load_model()
    for name in names:
        if name not in mod.parts:
            print(f"{name}: not a part in probe_cq.py")
            continue
        wp = mod.parts[name]
        dx, dy, dz = UNPLACE.get(name, (0.0, 0.0, 0.0))
        part = wp.translate((dx, dy, dz))
        s = part.val()
        bb = s.BoundingBox()
        stem = os.path.join(OUT, name)
        cq.exporters.export(part, stem + ".step")
        cq.exporters.export(part, stem + ".stl", tolerance=0.02, angularTolerance=0.1)
        print(f"{name:22s} {s.Volume()/1000:7.2f} cm3  "
              f"{bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:6.1f} mm  "
              f"faces {len(s.Faces())}  valid {s.isValid()}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["rotor"])
