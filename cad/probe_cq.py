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
TE_MM = 0.5          # blunt trailing edge, full thickness (printable, no razor)
# Thickness/chord. The NACA 4412 (12 %) is a metal-blade number: at the tip that
# is 1.0 mm of ABS. Bending the blade out of the rotor plane as a tapered
# cantilever (thrust 8 N per blade, spread as annular area) gives 44 mm of tip
# deflection - 57 % of the span, i.e. the tip sags most of its own length.
# 20 % gives 9.6 mm at the design flow and 2.4 mm at 0.5 m/s, root stress falls
# from 6.2 to 2.2 MPa, and at Re 30-40k a thick section is the better foil
# anyway: the thin one separates.
THICKNESS = 0.20
STATIONS = [(0.20, 34.8, 38.7), (0.35, 22.3, 25.9), (0.50, 16.2, 19.9),
            (0.65, 12.6, 16.6), (0.80, 10.3, 14.5), (1.00, 8.3, 12.6)]
MAGCUP_D = 70.0; MAGCUP_H = 18.0; CUP_BODY = 10.0; WALL_T = 4.0
MAG_D = 10.0; MAG_H = 5.0; MAG_N = 8
POD_OD = 110.0; POD_ID = 96.0; POD_LEN = 120.0
CAGE_LEN = 200.0; CAGE_OD = 130.0; CAGE_WALL = 4.0; CAGE_SLOTS = 12
ARM_OD = 28.0; BOX_Z = 1710.0   # underside of the dry box
POLE_TOP = 2600.0
POLE_OD = 60.0; POLE_H = 2600.0
ARM_LEN = 1200.0

# ---------------- NACA 4412 (finite TE for kernel stability) ---------------
def naca4_pts(n=64, te_half=0.0, t=THICKNESS):
    """te_half = minimum half-thickness at the trailing edge, as a FRACTION of
    the chord. The raw NACA 4412 closes to 0.12% of chord (0.02 mm at the tip),
    which is a razor the slicer cannot print and the first reed will fray.
    Pass 0.25/chord for a 0.5 mm blunt TE."""
    m,p = 0.04, 0.4
    def yt(x):
        # the TE floor has to vanish at the leading edge, or the same max() that
        # blunts the tail also gives the nose a 0.5 mm flat face - and at 20 %
        # thickness that folded the profile onto itself (2 non-manifold edges
        # at r 56 mm). x**4 keeps the nose exactly sharp and the tail square.
        return max(5*t*(0.2969*math.sqrt(x)-0.1260*x-0.3516*x*x+0.2843*x**3-0.1016*x**4),
                   te_half * x**4)
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
    sections = []
    for rf, chord, twist in STATIONS:
        n_pts = naca4_pts(64, te_half=(TE_MM / 2.0) / chord, t=THICKNESS)
        r = ROTOR_R * rf
        qc = 0.25
        th = math.radians(twist)
        pts3d = []
        for x_frac, y_frac in n_pts:
            # chordwise u (tangential, in the rotor plane), thickness v (axial)
            u = (x_frac - qc) * chord
            v = y_frac * chord
            # twist about the radial span axis (X): u rotates into the axial dir
            y_l = u * math.cos(th) - v * math.sin(th)
            z_l = u * math.sin(th) + v * math.cos(th)
            # span along +X at this station
            pts3d.append((r, y_l, z_l + HUB_LEN/2 - 5.4))
        wire = cq.Wire.makePolygon([cq.Vector(*p) for p in pts3d + [pts3d[0]]])
        sections.append(wire)
    blade = cq.Solid.makeLoft(sections, ruled=True)
    return cq.Workplane(obj=blade)

# ---------------- hub + shaft + cups ---------------------------------------
def make_hub():
    # extrude() is one-directional on purpose: "both=True" made this Ø64 hub
    # 92 mm long instead of the 46 the BOM (A02) specifies - half the rotor's
    # volume and 46 mm of axial envelope that nothing needed.
    hub = cq.Workplane("XY").circle(HUB_D/2).circle(5/2).extrude(HUB_LEN)
    # Radial set screws, at 60 and 180 deg so they land between the blades.
    # The wall is 29.5 mm thick (Ø64 hub, Ø5 shaft), so an M4x8 grub screw in a
    # plain hole never reaches the shaft - it just rattles in a 30 mm bore. The
    # screw has to be long enough to bridge it: M4x30 from the OD, threaded
    # through a heat-set insert seated at the mouth, tip on a filed flat.
    for ang in (60, 180):
        bore = (cq.Workplane("YZ").circle(4.5/2).extrude(HUB_D/2+2)
                .rotate((0,0,0),(0,0,1), ang).translate((0,0,HUB_LEN-15)))
        hub = hub.cut(bore)
        seat = (cq.Workplane("YZ").circle(6.4/2).extrude(10)
                .rotate((0,0,0),(0,0,1), ang).translate((-1,0,HUB_LEN-15)))
        hub = hub.cut(seat)
    return hub

def make_shaft():
    # 78 mm, from the hub's front face (0) to the cup's pin boss (78). The old
    # 115 mm version reached 37 mm into what is now the nose cone and shared
    # 275 mm3 with it.
    return cq.Workplane("XY").circle(2.5).extrude(78)

def make_cup(flavour="wet"):
    """Solid disc with 8 blind magnet pockets on the +Z face and a bore for the
    shaft. Pockets are real pockets: the magnet sits 5 mm deep with 0.2 mm of
    epoxy over it, not floating in an open dish.

    Body is CUP_BODY (10 mm) thick so the 5.2 mm pocket leaves 4.8 mm of plastic
    behind it. The centre carries a Ø14 clamp boss on the -Z face, which the Ø5
    shaft passes through; a Ø2 cross pin through boss and shaft is the drive, so
    no printed thread sits anywhere in the torque path.
    """
    cup = cq.Workplane("XY").circle(MAGCUP_D / 2).extrude(CUP_BODY)
    cup = cup.union(cq.Workplane("XY").circle(7).extrude(6).translate((0, 0, -6)))
    # Ø5 through bore
    cup = cup.cut(cq.Workplane("XY").circle(2.5).extrude(40).translate((0, 0, -20)))
    # Ø2.1 cross pin hole through the clamp boss, 4 mm from its upstream end
    cup = cup.cut(cq.Workplane("YZ").circle(1.05).extrude(24).translate((-12, 0, -3)))
    if flavour == "dry":
        # the dry cup rides on the dry shaft and turns around the bulkhead's
        # Ø20 dry bearing boss, so its centre is a Ø22 clearance bore - the load
        # path is the boss, not the cup's plastic.
        cup = cup.cut(cq.Workplane("XY").circle(11).extrude(CUP_BODY))
    # 8 blind pockets, cut from the +Z face
    for i in range(MAG_N):
        th = 2 * math.pi * i / MAG_N
        r = MAGCUP_D / 2 - MAG_D / 2 - 2
        pocket = (cq.Workplane("XY").circle(MAG_D / 2 + 0.1).extrude(MAG_H + 0.2)
                  .translate((r * math.cos(th), r * math.sin(th), CUP_BODY - MAG_H - 0.2)))
        cup = cup.cut(pocket)
    return cup

# ---------------- generator pod with nose bearing blocks --------------------


def make_magnets(dry=False):
    """8 discrete N52 discs, each sitting in its own pocket."""
    out = None
    for i in range(MAG_N):
        th = 2 * math.pi * i / MAG_N
        r = MAGCUP_D / 2 - MAG_D / 2 - 2
        m = (cq.Workplane("XY").circle(MAG_D / 2).extrude(MAG_H)
             .translate((r * math.cos(th), r * math.sin(th),
                         CUP_BODY - MAG_H - 0.2)))
        out = m if out is None else out.union(m)
    return out

def make_generator():
    # GB2208-class outrunner: Ø27.5 x 23 mm body, 3 mm shaft
    body = cq.Workplane("XY").circle(27.5/2).extrude(23)
    shaft = cq.Workplane("XY").circle(1.5).extrude(12).translate((0, 0, -12))
    return body.union(shaft)

def make_pod():
    """Barrel + integrated bulkhead, printed as ONE part. Nothing pierces the
    barrier, so there is no fastener to seal and no O-ring on the coupling face.

    local Z 0 = world 85 (assembly translate Z_POD).
      -4..0        bulkhead Ø110 x WALL_T - this 4 mm disc IS the magnet wall,
                   so the face gap stays wall + 2 x 0.2 = 4.4 mm
      -14..-4      four bosses at r 45 on the WET face: blind M4 heat-set
                   inserts, opened from the wet side, so no thread reaches the
                   dry volume
       0..10       reinforcement rib r 40..48 on the dry face - it carries the
                   load from the four spider bosses into the barrel without
                   thinning the magnet wall
       0..5        695ZZ seat, Ø13 H7 x 5, pressed in from the dry face
       0..POD_LEN   barrel Ø110 / Ø96
     118.2..120    O-ring groove r 50.8..53.0, 2.2 x 1.8, on the downstream face
     108..120      six lugs r 48..58 with Ø4.5 holes; upstream edge rounded
                   (R6.5 cylinder) so the flow slides past instead of hitting a
                   flat block
    """
    tube = cq.Workplane("XY").circle(POD_OD / 2).extrude(POD_LEN)
    tube = tube.cut(cq.Workplane("XY").circle(POD_ID / 2).extrude(POD_LEN + 20)
                    .translate((0, 0, -10)))
    wall = cq.Workplane("XY").circle(POD_OD / 2).extrude(WALL_T).translate((0, 0, -WALL_T))
    rib = cq.Workplane("XY").circle(POD_ID / 2).circle(40).extrude(10)
    pod = tube.union(wall).union(rib)
    # dry bearing boss: Ø20 x 10 standing on the bulkhead's dry face. The 695ZZ
    # (5x13x4) presses into a Ø13 H7 x 5 seat cut into this boss from the dry
    # side, so 5 mm of plastic plus the 4 mm wall sit behind it. The dry cup's
    # own bearing is this boss, not a seat in the thin bulkhead.
    pod = pod.union(cq.Workplane("XY").circle(10).extrude(10))
    pod = pod.cut(cq.Workplane("XY").circle(6.5).extrude(5))
    # four spider bosses on the wet face
    for i in range(4):
        a = math.radians(45 + 90 * i)
        pod = pod.union(cq.Workplane("XY").circle(5.5).extrude(10)
                        .translate((45 * math.cos(a), 45 * math.sin(a), -14)))
    # O-ring groove on the downstream face
    # Groove for an NBR70 Ø100 x 2.5 ring: 3.0 wide x 1.8 deep. It was 2.2 wide,
    # which gives 2.2*1.8 = 4.0 mm2 of groove for 4.9 mm2 of cord rubber - the
    # ring would have had to extrude out of the joint. 3.0 x 1.8 = 5.4 mm2 holds
    # the displaced volume, mean Ø102.8 against a 102.5 cord mean is ~0 stretch,
    # squeeze (2.5-1.8)/2.5 = 28%, and both lands stay over 1.8 mm.
    pod = pod.cut(cq.Workplane("XY").circle(52.9).circle(49.9).extrude(1.8)
                  .translate((0, 0, POD_LEN - 1.8)))
    # six lugs: flat plate + rounded upstream edge, then drill
    for i in range(6):
        plate = cq.Workplane("XY").box(12, 14, 6).translate((52, 0, POD_LEN - 3))
        round_edge = cq.Workplane(obj=cq.Solid.makeCylinder(
            6.5, 14, cq.Vector(52, -7, POD_LEN - 6), cq.Vector(0, 1, 0)))
        lug = (plate.union(round_edge)
               .cut(cq.Workplane(obj=cq.Solid.makeCylinder(
                   2.25, 26, cq.Vector(52.5, -13, POD_LEN - 8), cq.Vector(0, 1, 0)))))
        pod = pod.union(lug.rotate((0, 0, 0), (0, 0, 1), 60 * i))
    return pod

# ---------------- sensor cage with 12 radial slots -------------------------

def make_coupling_wall():
    """Solid Ø106 x 4 disc - the pressure barrier the magnets work through.
    Nothing pierces it: no shaft hole, only the O-ring groove on the rim."""
    disc = cq.Workplane("XY").circle((POD_OD - 4) / 2).extrude(WALL_T)
    groove = (cq.Workplane("XY").circle((POD_OD - 4) / 2)
              .circle((POD_OD - 4) / 2 - 2.2).extrude(1.8))
    return disc.cut(groove.translate((0, 0, WALL_T - 1.8)))


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
    # arm: built along Z, then laid out along +X (89 deg from Z -> nearly horizontal)
    arm = cq.Workplane("XY").circle(ARM_OD/2).extrude(ARM_LEN+40)
    arm = arm.rotate((0,0,0),(0,1,0), 85).translate((0,0,60))
    elbow = (cq.Workplane("XY").circle((ARM_OD+8)/2).extrude(ARM_OD+8)
             .translate((ARM_LEN-(ARM_OD+8)/2, 0, 60+ARM_LEN*math.tan(math.radians(5)))))
    # hollow Ø28x2 tube: carries the pod AND routes the cable inside it
    drop_h = 60 + ARM_LEN*math.tan(math.radians(5)) + 355
    drop  = (cq.Workplane("XY").circle(14).circle(12)
             .extrude(drop_h).translate((ARM_LEN,0,-355)))
    strut = (cq.Workplane("YZ")
             .circle((ARM_OD-10)/2).extrude(260)
             .rotate((0,0,0),(0,0,1),90)
             .translate((ARM_LEN,0,60+ARM_LEN*math.tan(math.radians(5))-6)))
    box   = cq.Workplane("XY").box(160,190,80).translate((0,0,1750))
    lid   = cq.Workplane("XY").box(162,192,6).translate((0,0,1750+43))
    ante  = cq.Workplane("XY").circle(3).extrude(330).translate((0,0,1750+40))
    tip   = cq.Workplane("XY").circle(4.5).extrude(9).translate((0,0,1750+40+322))
    cable = cq.Workplane("XY").circle(4.5).extrude(1750-40-90).translate((-(POLE_OD/2+5),0,90))
    # collar clamp: ring AROUND the barrel (no penetration), with one boss on top
    clamp = (cq.Workplane("XZ").circle(63).circle(56).extrude(44)
             .translate((ARM_LEN, -22, -420)))
    boss = (cq.Workplane("XY").circle(16).extrude(14)
            .translate((ARM_LEN, 0, -369)))
    clamp = clamp.union(boss)
    return (pole, collar, arm, elbow, drop, strut, box, lid, ante, tip, cable, clamp)

# ---------------- wet-side bearing carrier (A04, A05) ----------------------
def make_wet_carrier():
    """STATIC spider, bolted to the bulkhead's wet face. It carries the wet shaft
    in two plain bushings and traps it in both directions; the magnets transmit
    torque and nothing else.

    CAGE, not a flat spider: the longerons run at r 42-48 (outside the Ø70 magnet
    cup) and the spokes sit in the band in front of the cup (Z 63-71), so no part
    of this static body shares an axial band with a rotating cup at a radial band
    it occupies. A flat spider put the three arms through the cup body - measured
    3963 mm3 of interference at 0.25 mm resolution, i.e. the cup could not turn.
    """
    # boss: 47..61, Ø18, carries the two iglidur bushings; Ø5 shaft bore clear through
    boss = (cq.Workplane("XY").circle(9).extrude(14).translate((0, 0, 47))
            .cut(cq.Workplane("XY").circle(2.5).extrude(30).translate((0, 0, 40))))
    b1 = cq.Workplane("XY").circle(3.5).circle(2.5).extrude(5).translate((0, 0, 48))
    b2 = cq.Workplane("XY").circle(3.5).circle(2.5).extrude(5).translate((0, 0, 56))
    boss = boss.cut(b1).cut(b2)
    # three spokes 61..69, r 8..48, cut clear of the shaft collar (r 7, 61..65)
    # and of the cup's Ø14 clamp boss (r 7, 65..71)
    arms = None
    for i in range(3):
        a = (cq.Workplane("XY").box(48, 9, 8)
             .translate((24, 0, 65))
             .rotate((0, 0, 0), (0, 0, 1), i * 120))
        arms = a if arms is None else arms.union(a)
    arms = arms.cut(cq.Workplane("XY").circle(8.0).extrude(24).translate((0, 0, 57)))
    # ring 65..71 at r 42..48 sits on the four bulkhead bosses (71..81)
    ring = cq.Workplane("XY").circle(48).circle(42).extrude(6).translate((0, 0, 65))
    body = boss.union(arms).union(ring)
    # 4 bolt ears at 45/135/225/315 deg (bisecting the arms), M4 clearance
    for i in range(4):
        a = math.radians(45 + 90 * i)
        ear = (cq.Workplane("XY").circle(5.5).extrude(6)
               .translate((45 * math.cos(a), 45 * math.sin(a), 65)))
        body = body.union(ear)
    for i in range(4):
        a = math.radians(45 + 90 * i)
        hole = (cq.Workplane("XY").circle(2.1).extrude(20)
                .translate((45 * math.cos(a), 45 * math.sin(a), 63)))
        body = body.cut(hole)
    return body


def make_shaft_collars():
    """Two collars sandwich the spider boss: the shaft cannot walk either way."""
    up = cq.Workplane("XY").circle(7).extrude(6).translate((0, 0, 41))
    dn = cq.Workplane("XY").circle(7).extrude(6).translate((0, 0, 77))
    return up.union(dn)


def make_nose_cone():
    """Sheds filamentous algae outward instead of catching it on a ring."""
    return cq.Workplane("XY").circle(32).workplane(offset=-40).circle(6).loft()

def make_sensors():
    # all in cage-local coordinates, inside radius 61 (cage inner wall)
    # E201 pH electrode: Ø12.5 x 160 (LaskaKit spec)
    ph = cq.Workplane("XY").circle(6.25).extrude(160).translate((38, 0, 0))
    # SEN0237 DO probe: Ø12 x 130 galvanic
    do = cq.Workplane("XY").circle(6).extrude(130).translate((-38, 0, 0))
    # DS18B20 stainless probe: Ø6 x 50
    ntc = cq.Workplane("XY").circle(3).extrude(50).translate((0, -44, 20))
    # SEN0189 turbidity head: 38 x 28 x 10
    turb = cq.Workplane("XY").box(38, 28, 10).translate((0, 36, 70))
    # SEN0244 TDS probe board: 30 x 8 x 60
    tds = cq.Workplane("XY").box(30, 8, 60).translate((0, 0, 60))
    # MS5837-class carrier PCB 15 x 15 x 3 (level sensor, mounted through cage floor)
    prs = cq.Workplane("XY").box(15, 15, 3).translate((22, -22, 6))
    return ph.union(do).union(ntc).union(turb).union(tds).union(prs)


def fit_report():
    """Check every sensor envelope against the cage interior."""
    inner_r = CAGE_OD / 2 - CAGE_WALL
    items = {
        "pH E201 (12.5x160)":   (6.25, 160, 38, 0),
        "DO SEN0237 (12x130)":  (6.0, 130, -38, 0),
        "DS18B20 (6x50)":       (3.0, 50, 0, -44),
        "turbidity (38x28x10)": (19.0, 10, 0, 36),
        "TDS board (30x8x60)":  (15.0, 60, 0, 0),
        "level PCB (15x15x3)":  (10.6, 3, 22, -22),
    }
    print("\n  sensor fit inside cage (inner radius %.1f mm, length %.0f mm)" % (inner_r, CAGE_LEN))
    ok = True
    for name, (r, h, ox, oy) in items.items():
        radial = (ox ** 2 + oy ** 2) ** 0.5 + r
        fits_r = radial <= inner_r
        fits_h = h <= CAGE_LEN
        ok = ok and fits_r and fits_h
        print("    %-24s radial %5.1f / %5.1f %s | length %3.0f / %3.0f %s"
              % (name, radial, inner_r, "OK " if fits_r else "HIT",
                 h, CAGE_LEN, "OK" if fits_h else "HIT"))
    print("    RESULT:", "ALL FIT" if ok else "CONFLICT - change cage")
    return ok


def make_cage_adapter():
    # Ø110 -> Ø130 transition, 20 mm
    return (cq.Workplane("XY").circle(55).workplane(offset=20).circle(65)
            .loft(ruled=True))


def _bolt(x, y, z, d=6, h=30, axis="Z"):
    s = cq.Solid.makeCylinder(d / 2, h, cq.Vector(x, y, z),
                              cq.Vector(0, 0, 1) if axis == "Z" else cq.Vector(1, 0, 0))
    head = cq.Solid.makeCylinder(d * 0.85, 5, cq.Vector(x, y, z + h),
                                 cq.Vector(0, 0, 1) if axis == "Z" else cq.Vector(1, 0, 0))
    return cq.Workplane(obj=s).union(cq.Workplane(obj=head))


def make_joints():
    """Every junction gets visible hardware - nothing is 'just pushed in'."""
    out = None

    def add(shape):
        nonlocal out
        out = shape if out is None else out.union(shape)

    # 1. dry box -> pole: saddle plate + U-bolt band around the pole
    band = (cq.Workplane("XY").circle((POLE_OD + 10) / 2).circle(POLE_OD / 2 + 1)
            .extrude(40).translate((0, 0, BOX_Z - 30)))
    plate = cq.Workplane("XY").box(60, 190, 8).translate((40, 0, BOX_Z - 30))
    add(band); add(plate)
    for dy in (-70, 70):
        add(_bolt(70, dy, BOX_Z - 30, 6, 26, "X"))

    # 2. antenna -> pole: bracket + clamp
    ant = (cq.Workplane("XY").circle((POLE_OD + 10) / 2).circle(POLE_OD / 2 + 1)
           .extrude(24).translate((0, 0, POLE_TOP - 40)))
    add(ant)
    add(cq.Workplane("XY").box(40, 10, 6).translate((30, 0, POLE_TOP - 28)))
    add(_bolt(45, 0, POLE_TOP - 28, 5, 22, "X"))

    # 3. arm -> pole collar: gusset + 4 bolts
    arm_z = 60 + 20 * math.sin(math.radians(85))
    add(cq.Workplane("XY").box(34, 90, 26).translate((15, 0, arm_z)))
    for dy in (-30, 30):
        for dz in (-8, 8):
            add(_bolt(32, dy, arm_z + dz, 8, 34, "X"))

    # 4. drop tube -> arm end: elbow clamp, 2 bolts
    elbow_z = 60 + ARM_LEN * math.tan(math.radians(5))
    add(cq.Workplane("XY").circle(19).circle(14).extrude(26)
        .translate((ARM_LEN - 13, 0, elbow_z)))
    for dx in (-8, 8):
        add(_bolt(ARM_LEN - 13 + dx, 0, elbow_z + 26, 6, 24, "Z"))

    # 5. pod collar clamp: 4 bolts around the collar
    for ang in (45, 135, 225, 315):
        import math as _m
        x = ARM_LEN + 63 * _m.cos(_m.radians(ang))
        z = -420 + 63 * _m.sin(_m.radians(ang))
        add(_bolt(x, 0, z, 6, 30, "Y"))

    return out

def make_pod_seal():
    # O-ring groove: annular cut at rim, 2.2 wide x 1.8 deep
    ring = (cq.Workplane("XY").circle((POD_OD-4)/2).circle((POD_OD-4)/2-2.2)
            .extrude(1.8))
    # cable gland boss Ø18 x 12 on the pod wall
    boss = cq.Workplane("XY").circle(9).extrude(12).translate((POD_OD/2-6, 0, 70))
    return ring.union(boss)

# ---------------- anchor hardware (H01, H03, H10) --------------------------
def make_anchor():
    tip = cq.Solid.makeCone(34, 6, 60).translate(cq.Vector(0,0,-860))
    screw = (cq.Workplane("XY").circle(34).extrude(800).translate((0,0,-800))
             .union(cq.Workplane(obj=tip)))
    sleeve = cq.Workplane("XY").circle(26).circle((POLE_OD/2)+0.4).extrude(300)
    a1 = cq.Workplane("XY").circle(8).extrude(300).translate((-500,  900, -300))
    a2 = cq.Workplane("XY").circle(8).extrude(300).translate((-500, -900, -300))
    return screw.union(sleeve).union(a1).union(a2)

def make_guys():
    # two 3mm Dyneema lines, drawn exactly between pole top and the anchors
    top = cq.Vector(0, 0, POLE_H-150)
    out = None
    for sy in (1, -1):
        anc = cq.Vector(-500, sy*900, -300)
        d = anc - top
        cyl = cq.Solid.makeCylinder(1.5, d.Length, top, d.normalized())
        wp = cq.Workplane(obj=cyl)
        out = wp if out is None else out.union(wp)
    return out

# ---------------- safety cable (H11) ---------------------------------------
def make_safety_cable():
    return (cq.Workplane("XY").circle(1.5).extrude(520)
            .rotate((0,0,0),(0,1,0), 90).translate((ARM_LEN-80, 0, -420)))

def make_cable_run():
    # visible part of the cable: pod gland exit, around the barrel, into the collar
    pts = [(ARM_LEN+58, -72, -420), (ARM_LEN+72, -50, -405),
           (ARM_LEN+72, -10, -390), (ARM_LEN+18, 0, -378)]
    out = None
    for a, b in zip(pts, pts[1:]):
        va, vb = cq.Vector(*a), cq.Vector(*b)
        d = vb - va
        cyl = cq.Solid.makeCylinder(4, d.Length, va, d.normalized())
        wp = cq.Workplane(obj=cyl)
        out = wp if out is None else out.union(wp)
    return out

# ---------------- assembly -------------------------------------------------
parts = {}
# rotor: 3 blades at 120deg intervals + hub, instances by rebuilding each blade
parts["rotor"] = cq.Workplane("XY").add(make_hub().val())
for i in range(BLADES):
    b = make_blade().rotate((0,0,0),(0,0,1), i*120)
    parts["rotor"] = parts["rotor"].union(b.val(), clean=True)
# nose cone is PART OF THE ROTOR, not a separate bolt-on: a Ø64 -> Ø12 cone over
# 40 mm on the hub's upstream face. As a separate part placed at Z -23 it shared
# 44355 mm3 with the hub, and every fastening option for it sat in the blade
# swept volume. Merged, there is no joint at all and nothing to seal.
parts["rotor"] = parts["rotor"].union(
    cq.Workplane("XY").circle(HUB_D/2).workplane(offset=-40).circle(6).loft().val(), clean=True)
# ---- explicit axial layout (local Z, before the pod is laid horizontal) ----
# upstream -> downstream: weed guard | rotor | carrier | wet cup | WALL | pod | adapter | cage
Z_SHAFT   = 0     # shaft spans -37..78 (115 mm), hub grips at -31, cup at 67
Z_CARRIER = 15    # wet bearing carrier 47..71
Z_WETCUP  = 71    # wet cup body 71..81, magnet face on the bulkhead face
Z_POD     = 85    # pod: wall 80..85, barrel 85..205
Z_DRYCUP  = 85    # dry magnet cup inside the pod, right behind the wall
Z_ADAPTER = 205   # transition cone 205..225
Z_CAGE    = 225   # cage 225..425
Z_GUARD   = -50   # weed guard ring, upstream of the blade plane

parts["shaft"]       = make_shaft().translate((0,0,Z_SHAFT))
parts["wet_carrier"] = make_wet_carrier()
# the two Ø14 collars are gone: the shaft is trapped by the hub's aft face on
# one side of the spider boss and by the cup's clamp boss on the other, with a
# 1 mm PTFE thrust washer at -46..-47. Nothing rides on a grub screw in shear.
parts["thrust_washer"] = cq.Workplane("XY").circle(7).circle(2.5).extrude(1).translate((0,0,46))
# bought Ø5 shaft collar (A09, M3 grub): the rotating stack is trapped between
# this collar and the hub's aft face - the magnet pull loads the collar, never
# the plastic of the static spider.
parts["shaft_collar"] = cq.Workplane("XY").circle(7).circle(2.5).extrude(4).translate((0,0,61))
parts["magcup_wet"]  = make_cup().translate((0,0,Z_WETCUP))
parts["pod"]         = make_pod().translate((0,0,Z_POD))
# mirror("XY") flips Z, which is what a part BUILT along Z needs; mirror("XZ")
# flips Y and is a no-op on a body of revolution - it silently leaves the cup
# facing the wrong way, with its magnet pockets pointing into the cage.
parts["magcup_dry"]  = make_cup("dry").mirror("XY").translate((0,0,Z_DRYCUP + CUP_BODY))
parts["joints"] = make_joints()
# same frame as the cup: built along Z, mirrored like cup A, no extra rotation
parts["magnets_wet"] = make_magnets().translate((0,0,Z_WETCUP))
parts["magnets_dry"] = make_magnets(dry=True).mirror("XY").translate((0,0,Z_DRYCUP + CUP_BODY))
parts["generator"] = make_generator().translate((0,0,Z_POD+60))
parts["cage_adapter"]= make_cage_adapter().translate((0,0,Z_ADAPTER))
parts["cage"]        = make_cage().translate((0,0,Z_CAGE))
parts["sensors"]     = make_sensors().translate((0,0,Z_CAGE))
parts["anchor"] = make_anchor()
parts["guys"] = make_guys()
parts["cable_run"] = make_cable_run()
parts["safety_cable"] = (cq.Workplane("XY").circle(1.5).extrude(140)
    .rotate((0,0,0),(0,1,0),90).translate((ARM_LEN-130, 0, -420)))
site = make_site()
site_names = ["pole","collar","arm","elbow","drop","strut","box","lid","antenna","antenna_tip","cable","clamp"]
for name, shape in zip(site_names, site):
    parts[f"site_{name}"] = shape


# ---------------- assembly placement --------------------------------------
# Pod chain is built vertically in local Z; hang it horizontal at the arm end,
# rotor upstream (-X), cage downstream (+X), 420mm underwater.
# Transform: rotate about Y by +90 deg (+Z -> +X), then translate to arm tip.
# pod barrel centred under the drop tube; rotor sticks out upstream (rotating
# parts must never sit where the clamp/tube lands: measured overlap was 102 cm3)
POD_TIP = (ARM_LEN, -142, -420)
pod_chain = ["rotor","shaft","magcup_wet","magcup_dry","pod","cage",
             "wet_carrier","thrust_washer","shaft_collar","sensors","cage_adapter","generator","joints","magnets_wet","magnets_dry"]
for name in pod_chain:
    # +Z -> +X (lay the pod horizontal), then +X -> +Y so the axis follows the
    # river flow, which runs parallel to the bank; the arm crosses it at 90 deg
    parts[name] = (parts[name]
                   .rotate((0,0,0),(0,1,0),90)
                   .rotate((0,0,0),(0,0,1),90)
                   .translate(POD_TIP))

# assembly ----------------------------------------------------------
COLORS = {
    "rotor": (1.00, 0.45, 0.10), "magcup_wet": (0.35, 0.35, 0.38),
    "magcup_dry": (0.35, 0.35, 0.38), "shaft": (0.55, 0.55, 0.58),
    "wet_carrier": (0.45, 0.50, 0.58), "thrust_washer": (0.90, 0.90, 0.60),
    "pod": (0.10, 0.42, 0.30),
    "cage_adapter": (0.14, 0.46, 0.34), "cage": (0.13, 0.33, 0.72),
    "sensors": (0.95, 0.95, 0.90), "anchor": (0.70, 0.70, 0.72),
    "guys": (0.30, 0.30, 0.32), "safety_cable": (0.70, 0.70, 0.72),
    "site_pole": (0.22, 0.22, 0.24), "site_collar": (0.12, 0.12, 0.14),
    "site_arm": (0.45, 0.45, 0.48), "site_drop": (0.45, 0.45, 0.48),
    "site_strut": (0.45, 0.45, 0.48), "site_clamp": (0.40, 0.40, 0.43),
    "site_box": (0.78, 0.72, 0.45), "site_lid": (0.68, 0.62, 0.38),
    "site_antenna": (0.08, 0.08, 0.08), "site_antenna_tip": (0.75, 0.10, 0.10),
    "site_cable": (0.10, 0.10, 0.10),
}

assy = cq.Assembly(name="sub_mission_probe")
for name, shape in parts.items():
    try:
        rgb = COLORS.get(name, (0.80, 0.80, 0.80))
        assy.add(shape, name=name, color=cq.Color(*rgb))
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
fit_report()
print("saved assembly:", os.path.join(OUT, "probe_assembly.step"))
