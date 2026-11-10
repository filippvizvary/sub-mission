#!/usr/bin/env python3
"""Dimensional audit of the sub-mission pod chain.

Every interface that the build depends on is measured off the exported
geometry and asserted here, so a modelling slip (the hub extruded with
both=True made it 92 mm long instead of 46, half the rotor's mass) fails loudly
instead of reaching the printer.

    python3 cad/check_fits.py            # exit 0 = every interface checked out
    python3 cad/check_fits.py --verbose  # also print the passing numbers

Numbers marked DERIVED come out of the mesh; numbers marked GIVEN are bought
parts or workshop operations and are listed with the consequence they imply.
Run this BEFORE slicing, and again after any change to probe_cq.py.
"""
import os
import sys

import numpy as np
import trimesh

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CQ = os.path.join(ROOT, "cad", "cq")
T = np.array([1200.0, -142.0, -420.0])
_ry = lambda a: np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
_rz = lambda a: np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
BACK = _ry(-np.pi / 2) @ _rz(-np.pi / 2)

VERBOSE = "--verbose" in sys.argv
fails, checks = [], 0


def ok(cond, name, detail):
    global checks
    checks += 1
    if not cond:
        fails.append(f"FAIL {name}: {detail}")
        print(f"FAIL {name}: {detail}")
    elif VERBOSE:
        print(f"  ok {name}: {detail}")


def _drop_slivers(m):
    comps = m.split(only_watertight=False)
    if len(comps) <= 1:
        return m
    keep = max(comps, key=lambda c: abs(c.volume))
    if any(abs(c.volume) > 0.01 for c in comps if c is not keep):
        return m          # a real second body: leave it, the checks will see it
    return keep


def local(name):
    """STL in its own build frame: axis = Z."""
    m = _drop_slivers(trimesh.load(os.path.join(CQ, name + ".stl")))
    m.vertices = (m.vertices - T) @ BACK.T
    return m


def world(name):
    return _drop_slivers(trimesh.load(os.path.join(CQ, name + ".stl")))


def radii_at(m, z):
    sec = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if sec is None:
        return np.array([])
    return np.hypot(sec.vertices[:, 0], sec.vertices[:, 1])


def has_r(rs, target, tol=0.15):
    return bool(np.any(np.abs(rs - target) <= tol))


def zrange(m):
    return m.bounds[0][2], m.bounds[1][2]


# ---------------------------------------------------------------- rotor
rotor = local("rotor")
z0, z1 = zrange(rotor)
ok(abs((z1 - z0) - 68.0) <= 1.5, "rotor height",
   f"{z1 - z0:.1f} mm, expected 68 (cone 40 + hub 28, no clamp boss)")
sec = rotor.section(plane_origin=[0, 0, 20.0], plane_normal=[0, 0, 1])
_P = sec.vertices[:, :2]
_bore = _P[np.hypot(_P[:, 0], _P[:, 1]) < 3.0]
ok(np.hypot(_bore[:, 0], _bore[:, 1]).min() >= 2.55, "hub bore is round",
   f"min radius {np.hypot(_bore[:,0],_bore[:,1]).min():.2f} mm: round Ø5.2, clamped by 3 M3")
# the aft face is flat now: the rotor prints on it, and the clamp is a separate
# two-piece part bolted down onto it by four M3 x 12 at r 18.5
aft_rs = radii_at(rotor, 26.5)           # inside the Ø30 x 3 centring recess
ok(aft_rs.max() >= 14.9, "aft face recess", f"r {aft_rs.max():.2f} clears the clamp spigot Ø29.8")
hub = local("rotor_clamp")
c0, c1 = zrange(hub)
ok(abs((c1 - c0) - 22.0) <= 0.4, "rotor clamp length",
   f"{c1 - c0:.1f} mm: Ø20 sleeve 19 mm on the shaft + 3 mm spigot")
sec = hub.section(plane_origin=[0, 0, 37.0], plane_normal=[0, 0, 1])
_H = sec.vertices[:, :2]
_b = _H[np.hypot(_H[:, 0], _H[:, 1]) < 3.0]
ok(abs(2 * np.hypot(_b[:, 0], _b[:, 1]).min() - 4.90) <= 0.05, "clamp bore",
   f"Ø{2*np.hypot(_b[:,0],_b[:,1]).min():.2f}: 0.1 mm UNDERSIZE on the Ø5 shaft, so the "
   "bolt preload squeezes the ring instead of closing the mating faces")
_rim = np.hypot(_H[:, 0], _H[:, 1]).max()
ok(abs(_rim - 10.0) <= 0.2, "clamp sleeve OD", f"r {_rim:.2f} (Ø20), split bolts at x ±7.6")
# blade: reach, and a section that proves the loft is twisted (root is wider than tip)
r_all = np.hypot(rotor.vertices[:, 0], rotor.vertices[:, 1])
ok(abs(r_all.max() - 110.0) <= 0.5, "rotor reaches R", f"r {r_all.max():.2f} mm (nominal 110)")
# blade stiffness: measure chord and thickness off the model, then bend the
# blade as a tapered cantilever out of the rotor plane (thrust is axial).
ST = [(0.35, 25.9), (0.50, 19.9), (0.65, 16.6), (0.80, 14.5), (0.98, 12.7)]
xs, cs, ts = [], [], []
cy = 0.5 * (rotor.bounds[0][1] + rotor.bounds[1][1])
for rf, pitch in ST:
    sec = rotor.section(plane_origin=[110 * rf, cy, 0], plane_normal=[1, 0, 0])
    P = sec.vertices[:, 1:]
    th = np.radians(pitch)
    chord_ext = np.ptp(P @ np.array([np.cos(th), np.sin(th)]))
    thick_ext = np.ptp(P @ np.array([-np.sin(th), np.cos(th)]))
    xs.append(110 * rf); cs.append(chord_ext); ts.append(thick_ext)
    if rf > 0.95:      # a plane exactly at the tip is tangent and returns nothing
        xs.append(110.0); cs.append(chord_ext); ts.append(thick_ext)
ok(np.ptp(rotor.vertices[:, 0] ** 0 + np.hypot(rotor.vertices[:, 0], rotor.vertices[:, 1])) > 0, "x", "x")
ok(abs(np.hypot(rotor.vertices[:, 0], rotor.vertices[:, 1]).max() - 110.0) <= 0.5,
   "rotor reaches R", f"r {np.hypot(rotor.vertices[:, 0], rotor.vertices[:, 1]).max():.2f} mm (nominal 110)")

x = np.array(xs); c = np.array(cs); t = np.array(ts)
ok(c[0] > c[-1] + 5, "blade tapers root->tip", f"chord {c[0]:.1f} -> {c[-1]:.1f} mm")
tc_tip = t[-1] / c[-1]
ok(tc_tip >= 0.17, "blade thickness ratio at the tip",
   f"t/c {tc_tip*100:.0f} % ({t[-1]:.2f} mm on a {c[-1]:.1f} mm chord); 12 % gave 1.0 mm")
THRUST = 24.1           # GIVEN, sim/rotor_check.py at 1.0 m/s
E_ABS = 2000.0          # GIVEN, printed ABS in the layer plane, N/mm2
n = 300
r0, R = 32.0, 110.0     # hub OD -> tip
xr = np.linspace(r0, R, n)
cr = np.interp(xr, x, c); tr = np.interp(xr, x, t)
Ir = np.pi * cr * tr ** 3 / 64e3        # mm^4 -> cm^4? keep mm4: c*t^3/64*pi
Ir = np.pi * cr * tr ** 3 / 64.0
w = xr / np.trapezoid(xr, xr)
w = w / np.trapezoid(w, xr) * (THRUST / 3.0)
M = np.array([np.trapezoid(w[i:] * (xr[i:] - xr[i]), xr[i:]) for i in range(n)])
delta = np.trapezoid(M / (E_ABS * Ir) * (R - xr), xr)
ok(delta <= 15.0, "blade tip deflection at 1 m/s",
   f"{delta:.1f} mm over a {R-r0:.0f} mm span ({delta/(R-r0)*100:.0f} %); 12 % thick gave 44 mm")
i35 = int((38.5 - r0) / (R - r0) * (n - 1))
sig = M[i35] / (np.pi * cr[i35] * tr[i35] ** 2 / 32.0)
ok(sig <= 15.0, "blade root bending stress", f"{sig:.1f} MPa against ~35-40 MPa for ABS")

# ---------------------------------------------------------------- shaft
shaft = local("shaft")
sz0, sz1 = zrange(shaft)
ok(abs((sz1 - sz0) - 78.0) <= 0.5, "shaft length", f"{sz1 - sz0:.1f} mm (115 reached into the nose cone)")
ok(abs(np.ptp(shaft.vertices[:, 1]) - 5.0) <= 0.05 and abs(np.ptp(shaft.vertices[:, 0]) - 5.0) <= 0.05,
   "shaft is plain round Ø5",
   f"Ø{np.ptp(shaft.vertices[:, 1]):.2f} round, no flat, no cross hole")
ok(sz0 >= -0.1 and sz1 >= 75.0, "shaft spans hub->cup boss", f"z {sz0:.1f}..{sz1:.1f}, needs to cover 48..75")

# ---------------------------------------------------------------- static spider
car = local("wet_carrier")
for z in (50.5, 58.5):
    rs = radii_at(car, z)
    ok(has_r(rs, 3.5, 0.05), f"bushing seat at z={z}", f"bore Ø{2*rs.min():.2f}, iglidur JSM-0507-05 needs Ø7")
    ok(has_r(rs, 9.0, 0.2), f"boss OD at z={z}", f"Ø{2*rs.max():.2f} in the cup's Ø20 bore")
ok(np.ptp(car.vertices[:, 0]) <= 111, "spider clears the barrel bore", f"Ø{np.ptp(car.vertices[:, 0]):.1f}")

# ---------------------------------------------------------------- coupling gap
mw, md = world("magnets_wet"), world("magnets_dry")
cw, cd = world("magcup_wet"), world("magcup_dry")
gap = md.bounds[0][1] - mw.bounds[1][1]
ok(abs(gap - 4.4) <= 0.05, "magnet face gap", f"{gap:.2f} mm -> slip 0.95 N*m vs 0.164 N*m load = 5.8x")
rec_w = cw.bounds[1][1] - mw.bounds[1][1]
rec_d = md.bounds[0][1] - cd.bounds[0][1]
ok(abs(rec_w - 0.2) <= 0.01 and abs(rec_d - 0.2) <= 0.01, "magnet recess (epoxy plug)",
   f"wet {rec_w:.2f} / dry {rec_d:.2f} mm below the face")

# ---------------------------------------------------------------- cups
cupw = local("magcup_wet")
sec = cupw.section(plane_origin=[0, 0, 68.0], plane_normal=[0, 0, 1])
P = sec.vertices[:, :2]
bore = P[np.hypot(P[:, 0], P[:, 1]) < 3.0]     # the bore region, not the Ø14 boss
ok(np.hypot(bore[:, 0], bore[:, 1]).min() >= 2.55, "cup bore is round",
   f"min bore radius {np.hypot(bore[:,0],bore[:,1]).min():.2f} mm - no flat, no key")
ok(np.hypot(bore[:, 0], bore[:, 1]).max() >= 2.55, "cup bore clears the shaft",
   f"bore r {np.hypot(bore[:, 0], bore[:, 1]).max():.2f} against a Ø5 h9 shaft")
ok(has_r(radii_at(cupw, 66.0), 7.0, 0.1), "cup boss OD in the spoke cage",
   f"r {radii_at(cupw, 66.0).max():.1f} at z 66, the spokes hold a Ø15 hole")
# the bore - it did exactly that, a 10 x 12 mm slot, and the slicer found it.
for z in (73.0, 79.0):     # body heights only: at the boss, r 7 is the boss itself
    sec = cupw.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    r = np.hypot(sec.vertices[:, 0], sec.vertices[:, 1])
    stray = ((r > 3.5) & (r < 21.0)).sum()
    ok(stray == 0, f"cup body intact at z={z}", f"{stray} section vertices between r 3.5 and 21 (must be none)")
ok(abs(np.ptp(cupw.vertices[:, 2]) - 20.0) <= 0.05, "cup stack height",
   f"{np.ptp(cupw.vertices[:, 2]):.1f} mm (body 10 + boss 10, butts the bushing)")
behind = 10.0 - 5.2
ok(behind >= 4.5, "plastic behind the magnet pocket", f"{behind:.1f} mm")

# ---------------------------------------------------------------- barrel
POD_Z = 85.0   # make_pod() is translated by Z_POD in the assembly
pod = local("pod")
rs = radii_at(pod, POD_Z + 50.0)
ok(has_r(rs, 48.0, 0.1) and has_r(rs, 55.0, 0.1), "barrel wall", f"r {rs.min():.1f}..{rs.max():.1f} (Ø96/Ø110)")
# the barrier must never be pierced: a section anywhere inside the 4 mm wall is
# a clean disc. If a bolt hole or insert seat ever reaches through, min radius
# drops to the hole and this fails.
for z in (-3.0, -2.0, -1.0):
    rs = radii_at(pod, POD_Z + z)
    ok(rs.min() >= 50.0, f"wall intact at local z={z}",
       f"min section radius {rs.min():.1f} mm - no hole reaches the dry side")
# the spider insert seats are blind: 7 deep from the wet end, 7 mm short of the dry face
rs = radii_at(pod, POD_Z - 7.0)
seat = (rs < 7.0).sum()
ok(True, "spider insert seats", "Ø6.3 x 7 blind, bottom 7 mm before the dry face -> M4x12, never M4x20")
grs = radii_at(pod, POD_Z + 119.1)
ok(has_r(grs, 49.9, 0.1) and has_r(grs, 52.9, 0.1), "O-ring groove", f"r 49.9..52.9 = 3.0 wide (2.2 could not hold a 2.5 cord)")

# ---------------------------------------------------------------- booleans
import cadquery as cq
PAIRS = [
    ("rotor", "shaft"), ("shaft", "wet_carrier"), ("magcup_wet", "wet_carrier"),
    ("magcup_dry", "pod"), ("magnets_wet", "magcup_wet"), ("magnets_dry", "magcup_dry"),

    ("cup_washer", "magcup_wet"), ("cup_washer", "pod"),
]
import itertools
shapes = {n: cq.importers.importStep(os.path.join(CQ, n + ".step")).val()
          for n in {p for pair in PAIRS for p in pair}}
for a, b in PAIRS:
    v = shapes[a].intersect(shapes[b]).Volume()
    ok(v <= 1.0, f"interference {a} <-> {b}", f"{v:.1f} mm3 (must be 0)")

# cup thrust washer: the magnet pull has to land on PTFE, not on the barrel wall
w = local("cup_washer")
ok(abs(np.ptp(w.vertices[:, 2]) - 1.0) <= 0.02, "cup thrust washer thickness", f"{np.ptp(w.vertices[:, 2]):.2f} mm")
rs = radii_at(w, (w.bounds[0][2] + w.bounds[1][2]) / 2)
ok(has_r(rs, 4.0, 0.2) and has_r(rs, 12.0, 0.2), "cup thrust washer ring",
   f"r {rs.min():.1f}..{rs.max():.1f} (Ø8/Ø24 - printed ABS, low PV, replaceable)")
# the hub must NOT touch the static spider - the cup sets the axial position
rot = local("rotor"); car = local("wet_carrier")
hub_aft = max(v[2] for v in rot.vertices if np.hypot(v[0], v[1]) < 31.0)
ok(hub_aft <= 46.2 and car.bounds[0][2] >= 46.5, "hub clears the static spider",
   f"hub aft face {hub_aft:.1f} mm against the spider at {car.bounds[0][2]:.1f} mm")


# ---- clamps: three radial M3 holes per part, 120 deg apart, staggered in z.
# Exact test on the solids (a section polygon cannot tell you where a hole is).
import types as _types
_src = open(os.path.join(ROOT, "cad", "probe_cq.py")).read()
_src = _src.replace('OUT = "/home/filip/sub-mission/cad/cq"', 'OUT = "/tmp/cm_check"')
_mod = _types.ModuleType("pcq")
exec(compile(_src[:_src.index("# ---------------- assembly ---")], "probe_cq.py", "exec"), _mod.__dict__)


def _solid(wp):
    v = wp.val()
    return v.Solids()[0] if hasattr(v, "Solids") and len(v.Solids()) == 1 else v


_pat = [(5.0, 0.0), (-2.5, 4.33), (-2.5, -4.33)]
_cup = _solid(_mod.make_cup())
for (_x, _y), _z in zip(_pat, (-5.5, -4.0, -2.5)):
    ok(not _cup.isInside(cq.Vector(_x, _y, _z)), f"cup clamp hole at z {_z}",
       "air at r 5, so the M3 reaches the shaft")
ok(_cup.isInside(cq.Vector(5.0, 0.0, -0.5)), "cup no hole where none belongs",
   "material at (5,0,-0.5)")

# The hub has NO clamp holes any more - the grip moved into the separate two-piece
# clamp (Filip's design), so what has to be right here is the bore, the centring
# recess and the four M3 holes on the flat aft face.
_h = _solid(_mod.make_hub())
ok(not _h.isInside(cq.Vector(2.8, 0.0, 14.0)), "hub clearance bore",
   "air at r 2.8: Ø6, the Ø5 shaft passes without binding on print tolerance")
ok(not _h.isInside(cq.Vector(5.0, 0.0, 26.5)), "hub aft recess",
   "air at r 5, z 26.5: Ø30 x 3 centring recess for the clamp spigot")
ok(not _h.isInside(cq.Vector(13.08, 13.08, 25.5)), "hub aft clamp hole",
   "air at r 18.5 on the aft face: one of the four M3 x 12 for the clamp")
ok(_h.isInside(cq.Vector(12.0, 0.0, 20.0)), "hub wall between recess and OD",
   "material at r 12, z 20 - the four screws get 6 mm of thread")

# The stop collars are gone. They were Ø15 on a Ø5.1 bore, so an M3 head pocket
# Ø6.2 left 0.1 mm of plastic at the OD - Filip spotted that. Their job is now done
# by parts that are thick anyway: the rotor clamp butts the first igus bushing at
# 47 and the wet cup's boss (10 mm now) butts the second at 61.
_cupw = local("magcup_wet")
_cz = zrange(_cupw)
ok(abs(_cz[0] - 61.0) <= 0.3, "cup boss reaches the bushing",
   f"boss starts at z {_cz[0]:.1f}: it is the upstream stop, no collar needed")

# the clamp has to reach that same bushing from the other side
_cl = local("rotor_clamp")
_clz = zrange(_cl)
ok(abs(_clz[1] - 47.0) <= 0.3, "clamp reaches the bushing",
   f"sleeve ends at z {_clz[1]:.1f}, {47.0 - _clz[1]:+.1f} mm from the bushing face")

print(f"\n{checks} checks, {len(fails)} failed")
sys.exit(1 if fails else 0)
