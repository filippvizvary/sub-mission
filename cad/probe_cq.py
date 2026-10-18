#!/usr/bin/env python3
"""
sub-mission probe — CadQuery parametric build
Full assembly: rotor + shaft + bearings + magnetic cups + gen pod
+ sensor cage + arm/pole/drop-tube + dry box + antenna.
Every part is a watertight OCC solid; STEP + STL per part + full assembly.

Haven, 2026-10-19. Build order: blade (loft, quarter-chord pivot,
matched 64-segment profiles) -> hub+shaft -> cups (revolve) ->
pod (revolve+bore) -> cage (extrude + radial cuts) -> site structure.
"""
import cadquery as cq
from cadquery import Vector as V
import math, os, shutil

OUT = "/home/filip/sub-mission/cad/cq"
shutil.rmtree(OUT, ignore_errors=True)
os.makedirs(OUT, exist_ok=True)

# ---------------- parameters ----------------
ROTOR_R = 110.0
HUB_D, HUB_LEN = 64.0, 46.0
BLADES = 3
STATIONS = [ # (r_frac, chord_mm, twist_deg about quarter-chord)
  (0.20, 42, 28),
  (0.40, 38, 20),
  (0.55, 34, 12),
  (0.70, 30,  6),
  (0.85, 24,  3),
  (1.00, 17,  2),
]
MAGCUP_D = 42.0; MAGCUP_H = 14.0; WALL_T = 5.0
MAG_D = 8.0; MAG_H = 5.0; MAG_N = 8
POD_OD = 110.0; POD_ID = 96.0; POD_LEN = 120.0
CAGE_LEN = 150.0; CAGE_OD = 130.0; CAGE_WALL = 4.0; CAGE_SLOTS = 12
ARM_OD = 28.0; POLE_OD = 60.0; POLE_H = 2600.0
ARM_LEN = 1200.0

# ---------------- NACA 4412 (finite TE for kernel stability) ---------------
def naca4412_pts(n=64):
    m,p,t = 0.04, 0.4, 0.12
    def yt(x):
        return 5*t*(0.2969*math.sqrt(x)-0.1260*x-0.3516*x*x+0.2843*x**3-0.1016*x**4)
    def yc(x):
        return m/(p*p)*(2*p*x-x*x) if x<p else m/((1-p)**2)*((1-2*p)+2*p*x-x*x)
    def dyc(x):
        return 2*m/(p*p)*(p-x) if x<p else 2*m/((1-p)**2)*(p-x)
    up=[]; lo=[]
    for i in range(n+1):
        x=0.5*(1-math.cos(math.pi*i/n))
        th=math.atan(dyc(x))
        up.append((x - yt(x)*math.sin(th), yc(x)+yt(x)*math.cos(th)))
        lo.append((x + yt(x)*math.sin(th), yc(x)-yt(x)*math.cos(th)))
    # closed loop: LE start, run upper to TE, back along lower, keep both TE pts distinct
    return up + lo[::-1]

# ---------------- blade: loft between matched-section NACA profiles ---------
def make_blade():
    n_pts = naca4412_pts(64)
    sections = []
    for rf, chord, twist in STATIONS:
        r = ROTOR_R * rf
        qc = 0.25
        th = math.radians(twist)
        # build profile directly in 3D: chord along Z (rotation plane normal),
        # thickness along X, span along +Y, quarter-chord at origin before twist
        pts3d = []
        for x_frac, y_frac in n_pts:
            # chordwise u, thickness v, quarter-chord pivot
            u = (x_frac - qc) * chord
            v = y_frac * chord
            # twist about the span axis (Y): rotate (u,v) in the XZ plane
            # local frame before twist: chord dir = +Z, thickness dir = +X
            x_l = v
            z_l = u
            # rotation about +Y by pitch angle
            x_r =  x_l*math.cos(th) + z_l*math.sin(th)
            z_r = -x_l*math.sin(th) + z_l*math.cos(th)
            pts3d.append((x_r, r, z_r))
        # closed wire: first point repeated
        wire = cq.Wire.makePolygon([cq.Vector(*p) for p in pts3d + [pts3d[0]]])
        wire = cq.Wire.makePolygon([cq.Vector(*p) for p in pts3d + [pts3d[0]]])
        sections.append(wire)
    blade = cq.Solid.makeLoft(sections, ruled=True)
    return cq.Workplane(obj=blade)

# ---------------- hub + shaft + cups ---------------------------------------
def make_hub():
    hub = cq.Workplane("XY").circle(HUB_D/2).circle(5/2).extrude(HUB_LEN, both=True)
    # radial bores for M4 set-screw inserts (2 at 90deg, 15mm from aft face)
    for ang in (0,90):
        bore = (cq.Workplane("YZ")
                .circle(4.4/2)
                .extrude(HUB_D/2+2)
                .rotate((0,0,0),(0,0,1), ang))
        hub = hub.cut(bore.translate((0,0,-HUB_LEN/2+15)))
    return hub

def make_shaft():
    return cq.Workplane("XY").circle(2.5).extrude(115).translate((0,0,-HUB_LEN/2-26))

def make_cup(dry=False):
    # solid disc, then pocket the magnet ring
    cup = cq.Workplane("XY").circle((MAGCUP_D+6)/2).extrude(MAGCUP_H)
    pocket = cq.Workplane("XY").circle(MAGCUP_D/2).extrude(MAGCUP_H-3).translate((0,0,3))
    cup = cup.cut(pocket)
    for i in range(MAG_N):
        th = 2*math.pi*i/MAG_N
        r = MAGCUP_D/2 - MAG_D
        p = (cq.Workplane("XY")
             .circle(MAG_D/2 + 0.05).extrude(MAG_H+0.1)
             .translate((r*math.cos(th), r*math.sin(th), 4)))
        cup = cup.cut(p)
    return cup

# ---------------- generator pod with nose bearing blocks --------------------
def make_pod():
    # main barrel + tail cone
    barrel = cq.Workplane("XY").circle(POD_OD/2).extrude(POD_LEN)
    cone   = (cq.Workplane("XY")
              .circle(POD_OD/2)
              .workplane(offset=POD_LEN)
              .circle(1.0)
              .loft(combine="s"))
    pod = barrel.union(cq.Workplane("XY")
              .circle(POD_OD/2)
              .workplane(offset=POD_LEN)
              .transformed().circle(POD_OD/2).loft(combine="s") if False else barrel)
    # tail cone done properly
    tail = (cq.Workplane("XY")
            .add(cq.Solid.makeCone(POD_OD/2, POD_OD*0.18, POD_OD*0.55))
            .translate((0,0,POD_LEN)))
    pod = barrel.union(tail)
    # 5mm solid front wall (this is the mag-coupled barrier)
    wall = cq.Workplane("XY").circle((POD_OD-4)/2).extrude(-WALL_T)
    pod = pod.union(wall)
    # bore
    pod = pod.cut(cq.Workplane("XY").circle(POD_ID/2).extrude(POD_LEN+POD_OD))
    # nose bearing blocks (two PEEK bushings modelled as bosses)
    boss1 = cq.Workplane("XY").circle(22/2).extrude(14).translate((0,0,-30))
    boss2 = cq.Workplane("XY").circle(22/2).extrude(10).translate((0,0,-12))
    pod = pod.union(boss1).union(boss2)
    return pod

# ---------------- sensor cage with 12 radial slots -------------------------
def make_cage():
    outer = cq.Workplane("XY").circle(CAGE_OD/2).extrude(CAGE_LEN)
    inner = cq.Workplane("XY").circle((CAGE_OD-2*CAGE_WALL)/2).extrude(CAGE_LEN+2).translate((0,0,-1))
    cage = outer.cut(inner)
    for i in range(CAGE_SLOTS):
        th = 2*math.pi*i/CAGE_SLOTS
        slot = (cq.Workplane("XY")
                .box(CAGE_OD, 8, CAGE_LEN*0.7)
                .translate((0,0,CAGE_LEN/2)))
        cage = cage.cut(slot.rotate((0,0,0),(0,0,1), math.degrees(th)))
    # end openings
    cage = cage.cut(cq.Workplane("XY").circle(CAGE_OD*0.5/2).extrude(3).translate((0,0,-1)))
    cage = cage.cut(cq.Workplane("XY").circle(CAGE_OD*0.5/2).extrude(3).translate((0,0,CAGE_LEN-2)))
    return cage

# ---------------- site structure -------------------------------------------
def make_site():
    pole = cq.Workplane("XY").circle(POLE_OD/2).extrude(POLE_H)
    collar = cq.Workplane("XY").circle((POLE_OD+16)/2).extrude(44).translate((0,0,38))
    # arm (slight 5deg rise)
    arm = (cq.Workplane("YZ")
           .circle(ARM_OD/2).extrude(ARM_LEN+40)
           .rotate((0,0,0),(0,0,1), 90)
           .rotate((0,0,0),(0,-1,0), 5))
    arm = arm.translate((0,0,60))
    elbow = cq.Workplane("XY").sphere((ARM_OD+8)/2).translate((ARM_LEN, 0, 60+ARM_LEN*math.tan(math.radians(5))))
    drop  = (cq.Workplane("XY")
             .circle((ARM_OD-6)/2)
             .extrude(60+ARM_LEN*math.tan(math.radians(5))+420)
             .translate((ARM_LEN,0,-420)))
    strut = (cq.Workplane("YZ")
             .circle((ARM_OD-10)/2).extrude(260)
             .rotate((0,0,0),(0,0,1),90)
             .translate((ARM_LEN,0,60+ARM_LEN*math.tan(math.radians(5))-6)))
    box   = cq.Workplane("XY").box(160,190,80).translate((0,0,1750))
    lid   = cq.Workplane("XY").box(162,192,6).translate((0,0,1750+43))
    ante  = cq.Workplane("XY").circle(3).extrude(330).translate((0,0,1750+40))
    tip   = cq.Workplane("XY").sphere(4.5).translate((0,0,1750+40+330))
    cable = cq.Workplane("XY").circle(4.5).extrude(1750-40-90).translate((-(POLE_OD/2+5),0,90))
    return (pole, collar, arm, elbow, drop, strut, box, lid, ante, tip, cable)

# ---------------- assembly -------------------------------------------------
parts = {}
# rotor: 3 blades at 120deg intervals + hub, instances by rebuilding each blade
parts["rotor"] = cq.Workplane("XY").add(make_hub().val())
for i in range(BLADES):
    b = make_blade().rotate((0,0,0),(0,0,1), i*120)
    parts["rotor"] = parts["rotor"].union(b.val(), clean=True)
parts["shaft"] = make_shaft()
parts["magcup_wet"] = make_cup().mirror("XZ").translate((0,0,HUB_LEN/2+6+2+WALL_T+MAGCUP_H*2+4))
parts["magcup_dry"] = make_cup().translate((0,0,HUB_LEN/2+6+WALL_T))
parts["pod"] = make_pod().translate((0,0,HUB_LEN/2+6))
parts["cage"] = make_cage().translate((0,0,HUB_LEN/2+6+POD_LEN+WALL_T+60))
site = make_site()
site_names = ["pole","collar","arm","elbow","drop","strut","box","lid","antenna","antenna_tip","cable"]
for name, shape in zip(site_names, site):
    parts[f"site_{name}"] = shape

# full assembly: pod chain raised to drop-tube end at arm tip, then the site at origin
assy = cq.Assembly()
for name, shape in parts.items():
    try:
        assy.add(shape, name=name)
    except Exception as e:
        print("add failed:", name, e)

# ---------------- export ---------------------------------------------------
report = []
for name, shape in parts.items():
    try:
        sol = shape.val() if hasattr(shape,"val") else shape
        valid = sol.isValid()
        try:
            closed = sol.isClosed()
        except Exception:
            subs = sol.Solids() if hasattr(sol,'Solids') else []
            if subs:
                closed = all(s.Closed() for s in subs)   # note: capital C in cq
            else:
                closed = None
        vol = round(sol.Volume(),1)
        cq.exporters.export(shape, os.path.join(OUT, f"{name}.step"))
        cq.exporters.export(shape, os.path.join(OUT, f"{name}.stl"))
        report.append((name, valid, closed, vol))
    except Exception as e:
        report.append((name, "FAIL", None, str(e)[:120]))

# assembly STEP
assy.save(os.path.join(OUT, "probe_assembly.step"))
print("\n=== part report ===")
for r in report:
    print(f"  {r[0]:22s} valid={r[1]} closed={r[2]} vol_mm3={r[3]}")
print("saved assembly:", os.path.join(OUT, "probe_assembly.step"))
