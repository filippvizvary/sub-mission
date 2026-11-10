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
HUB_D, HUB_LEN = 64.0, 28.0
CLAMP_R, CLAMP_LEN = 8.0, 14.0   # Ø16 x 14 clamp boss on the hub's aft face
HEAD_D, HEAD_H = 6.2, 1.9          # flat pad under the M3 head, MEASURED:
                                   # head is Ø5.90 x 1.90 with a flat underside,
                                   # so 1.9 deep puts it exactly flush with the boss OD
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
MAGCUP_D = 70.0; MAGCUP_H = 18.0; WALL_T = 4.0
MEMBRANE = 0.45          # 3 layers at 0.15: the magnet face, printed ON THE BED
MAG_D = 10.0; MAG_H = 5.0; MAG_N = 12   # 12 per cup: he has exactly 24, and 12
CUP_BODY = MAG_H + 0.2 + MEMBRANE   # pocket 5.2 + membrane = 5.65, not 10
                                     # over 12 lifts the coupling from 0.95 to
                                     # ~1.4 N*m without changing anything else
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
    """Ø64 x 28 rotor hub, FLAT aft face, no clamp boss.

    The boss is gone. Filip's call and the right one: a Ø16 column bonded to the
    body through one layer of layer adhesion is exactly the joint that creeps
    apart, and it forces the rotor to print as a Ø64 plate on a Ø16 stalk with a
    64 mm unsupported underside. Now the aft face is a flat disc that goes
    straight onto the build plate, the rotor is 68 mm tall instead of 82, and the
    shaft clamp is a separate two-piece part bolted to that face.

    The face carries: Ø6 clearance bore, a Ø30 x 3 centring recess for the clamp's
    spigot, and four Ø2.6 x 6 holes on r 18.5 for M3 x 12 (printed, tapped).
    """
    hub = (cq.Workplane("XY").circle(HUB_D / 2).extrude(HUB_LEN)
           .cut(cq.Workplane("XY").circle(3.0).extrude(HUB_LEN + 20).translate((0, 0, -10)))
           .cut(cq.Workplane("XY").circle(15.0).extrude(3.0).translate((0, 0, HUB_LEN - 3))))
    for ang in (45.0, 135.0, 225.0, 315.0):
        a = math.radians(ang)
        hub = hub.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
            1.3, 7.0, cq.Vector(18.5 * math.cos(a), 18.5 * math.sin(a), HUB_LEN - 7.0),
            cq.Vector(0, 0, 1))))
    return hub


def _clamp_body(L, R_F=24.0, n_bolts=2, screw="M3", kind="head"):
    """One half of a two-piece shaft clamp, built properly.

    The split bolts live in EARS that stick out radially from the sleeve, not in the
    flange face and not in the sleeve's curved wall. That is the only place where a
    screw can be introduced along its own axis without a roof of plastic in front of
    it, which is what every earlier version got wrong.

      flange   Ø48 x 5, four M3 x 16 into the cup or hub, head pockets Ø6.2 x 2.1
               opening on the z=5 face (3 mm of flange stays under them)
      sleeve   Ø22, bore Ø4.90 - 0.10 mm UNDER the Ø5 shaft, so bolt preload
               squeezes the bore instead of just closing the mating faces
      ears     one per side at x 11..21, y 0..7, full length; each carries n_bolts
               holes Ø3.4 with a hex pocket 6.4 AF x 2.5 on the outer face, which
               takes the screw head on one half and the M3 nut on the other
    """
    # flange 5 - exactly the version Filip approved. The 2 mm the deleted magnet cover
    # used to fill is his to solve at assembly; he asked me not to keep chasing it.
    body = cq.Workplane("XY").circle(R_F).extrude(5)
    # sleeve starts at 4.5, not 5: a plane exactly on the flange's face is a
    # coincident surface, and OCC leaves slivers there that put vertices inside
    # the bore and make the mesh non-watertight
    body = body.union(cq.Workplane("XY").circle(11).extrude(L - 4.5).translate((0, 0, 4.5)))
    body = body.cut(cq.Workplane("XY").circle(2.45).extrude(L + 20).translate((0, 0, -10)))
    # four M3 into the cup / hub
    for ang in (45.0, 135.0):
        a = math.radians(ang)
        x, y = 18.5 * math.cos(a), 18.5 * math.sin(a)
        body = body.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
            1.7, 20, cq.Vector(x, y, -8), cq.Vector(0, 0, 1))))
        body = body.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
            3.1, 2.1, cq.Vector(x, y, 5.1), cq.Vector(0, 0, -1))))
    # ears + split bolts
    # Even slots along the ear, one bolt per slot, sized so the 7.0 AF hex pockets can
    # never touch each other. Spacing them by "span/(n+1)" put them 4.7 mm apart with
    # 7.0 mm pockets - they merged into a scalloped slot, which is what Filip saw.
    hole_r = 1.7 if screw == "M3" else 1.2
    # the two halves do DIFFERENT jobs, so each gets its own pocket:
    #   head half  round Ø6.4 x 2.2 - a DIN 84 pan head is Ø6.0 x 1.9
    #   nut  half  hex 5.8 AF x 2.6 - his nut measures 5.4 across flats and 2.3 thick,
    #              i.e. a standard DIN 934, so 0.2 per side of clearance
    hex_af = 5.8 if screw == "M3" else 4.0
    # polygon(6, 7.0) gives 6.06 across flats, and that is the pocket's real height.
    # The pockets all sit ABOVE the flange (z 5 and up), which is why the flange no
    # longer needs a notch: the ear's outer face is in the open air from z 5 to the
    # top, so a nut drops straight in from the side.
    hex_h = (6.4 if kind == "head" else hex_af * math.cos(math.pi / 6))
    ear_z0 = 5.0
    gap = max(0.6, (L - ear_z0 - n_bolts * hex_h) / (n_bolts + 1))
    zs = [ear_z0 + gap + hex_h / 2 + i * (hex_h + gap) for i in range(n_bolts)]
    for sx in (-1, 1):
        # ear from z 4.5 - half a mm INTO the flange, not resting exactly on its face:
        # a tangent union makes the mesh non-manifold. The pockets still start above
        # z 5, so the flange stays solid and the ear's outer face is in open air.
        ear = (cq.Workplane("XY").box(13.5, 5, L - ear_z0 + 0.5)
               .translate((sx * 16.25, 2.5, ear_z0 - 0.5 + (L - ear_z0 + 0.5) / 2)))
        body = body.union(ear)
    for sx in (-1, 1):
        for z in zs:
            body = body.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
                hole_r, 40, cq.Vector(sx * 15.75, 0, z), cq.Vector(0, 1, 0))))
            # pocket from the ear's outer face
            if kind == "head":
                body = body.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
                    3.2, 2.4, cq.Vector(sx * 15.75, 5.2, z), cq.Vector(0, -1, 0))))
            else:
                body = body.cut(cq.Workplane("XZ").polygon(6, hex_af).extrude(2.6)
                                .translate((sx * 15.75, 5.2, z)))
    # the split: keep y >= 0
    # the split box has to start BELOW z 0: with its bottom face exactly on the
    # flange's bottom face it left sliver edges there (2 non-manifold edges)
    body = body.cut(cq.Workplane("XY").box(160, 60, 62).translate((0, -30, 29)))
    return body


def make_rotor_clamp():
    """ONE HALF of the rotor's shaft clamp. Print twice, mate 180 deg apart.

    Same scheme as the stop collars, scaled up for the torque: two M3 x 12 across
    the split squeeze a Ø20 x 15 sleeve onto the Ø5 shaft, so the force comes from
    a bolt preload and never from a grub tip biting plastic. The sleeve carries a
    Ø44 flange with two counterbored M3 x 12 that go straight into the rotor's
    flat aft face - four screws for the pair, at r 18.5.

    Grip: 15 mm of Ø5.05 bore at 1800 N of clamp force gives ~0.9 N*m of friction
    against the 0.164 N*m the rotor actually sees, and the two split bolts sit at
    z 37, i.e. 9 mm clear of the rotor's face instead of 3 mm.
    """
    z_bot, z_top = HUB_LEN - 3.0, HUB_LEN + 19.0      # 25..47, right up to the bushing
    R_F = 24.0
    solid = cq.Workplane("XY").circle(R_F).extrude(7).translate((0, 0, HUB_LEN))   # flange 7 mm
    solid = solid.union(cq.Workplane("XY").circle(11).extrude(12).translate((0, 0, HUB_LEN + 7)))
    solid = solid.union(cq.Workplane("XY").circle(14.9).extrude(3).translate((0, 0, HUB_LEN - 3)))
    # Ø4.90, NOT Ø5.05. A split clamp with a clearance bore does nothing: once the
    # halves touch at the split, the bolt's tension goes into the mating faces and
    # never into the shaft. Undersize it and the shaft props the halves apart, so
    # the preload becomes radial squeeze - a collet, not a spacer.
    #
    # 0.10 and no more. These halves are rigid bodies, so closing the split is a
    # rigid-body motion: the only thing that deforms is the bore where it meets the
    # shaft. 0.10 mm makes the plastic yield into a full wrap and grips. 0.20 would
    # just print a polygon into the shaft and put the split line under a load it
    # does not need.
    solid = solid.cut(cq.Workplane("XY").circle(2.45).extrude(40).translate((0, 0, z_bot - 5)))
    # four M3 x 12 into the rotor, two of them land in this half
    for ang in (45.0, 135.0):
        a = math.radians(ang)
        x, y = 18.5 * math.cos(a), 18.5 * math.sin(a)
        solid = solid.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
            1.7, 12.0, cq.Vector(x, y, HUB_LEN - 2), cq.Vector(0, 0, 1))))
        solid = solid.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
            3.1, 2.0, cq.Vector(x, y, HUB_LEN + 5.2), cq.Vector(0, 0, -1))))
    # four M2 x 8 across the split: two pairs, 5 mm apart, in the sleeve's 10 mm
    # 21..40: between the rotor's hub face and the carrier boss. Identical to the cup's.
    # ONE bolt per side. Two rows in the 14 mm of ear above the flange leave 0.40 mm of
    # material over a Ø6.4 head pocket - one extrusion, it tears the moment the screw is
    # tightened. One bolt per side gives 3.80 (head half) and 4.49 (nut half).
    solid = _clamp_body(19.0, 24.0, 1, "M3", "head").translate((0, 0, 21.0))
    # the split: keep y >= 0
    solid = solid.cut(cq.Workplane("XY").box(120, 60, 60).translate((0, -30, 30)))
    return solid


def make_cup_clamp():
    """ONE HALF of a cup's shaft clamp - the rotor clamp's geometry, nut pockets.

    This used to be a hand-written leftover (Ø50 flange, M2 bolts, 12.35 mm) that was
    never replaced when the shared _clamp_body() was introduced, so the cup clamps were
    not the same part at all. Now they are: 19 mm, flange Ø48 x 7, sleeve Ø22, bore
    Ø4.90, two M3 x 8 per side. The only difference from the rotor clamp is that the
    pockets are hexagons (nut side) instead of round counterbores (head side).

    The 7 mm flange replaces the deleted 2 mm magnet cover: without that 2 mm the clamp
    would stop 2 mm short of the cup, and M3 x 12 would not reach.
    """
    return _clamp_body(19.0, 24.0, 1, "M3", "nut")   # one per side, see make_rotor_clamp


def make_shaft_collar(thickness, z0=0.0):
    """ONE HALF of a two-piece bolted stop collar. Print it twice, mate the pair
    180 deg apart, and two M3 x 12 with nuts clamp the Ø5 shaft hard.

    This is Filip's design and it is the right one for a shaft clamp: the force
    comes from a bolt preload across the split, not from a grub-screw tip biting
    plastic. It grips evenly, it does not mark the rod, and it comes off again.

    Each half carries BOTH features, one at x +4.5 and one at x -4.5: a Ø6.2 x
    3.2 counterbore for the screw head and a hex pocket 5.7 across flats x 3.2
    for an M3 nut. Rotate the second half 180 deg about Z and the head of one
    lands over the nut pocket of the other, so a two-part set needs no mirrored
    model - one STL printed twice.
    """
    half = (cq.Workplane("XY").circle(7.5).circle(2.55).extrude(thickness)
            .cut(cq.Workplane("XY").box(20, 20, thickness + 2)
                 .translate((0, -10, thickness / 2))))
    # pocket depth follows the part: at 3 mm a 3.2 mm pocket breaks through to
    # the split plane and the half falls into pieces (it did).
    pocket = min(3.4, thickness - 0.6)
    for x, kind in ((4.5, "head"), (-4.5, "nut")):
        # bolt runs along Y, from the split plane out to the OD
        half = half.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
            1.7, 10, cq.Vector(x, 0, thickness / 2), cq.Vector(0, 1, 0))))
        if kind == "head":
            half = half.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
                3.1, pocket, cq.Vector(x, 7.6, thickness / 2), cq.Vector(0, -1, 0))))
        else:
            # hex on the XZ plane so it extrudes along -Y, i.e. INTO the half from
            # the OD. Built on XY it extruded along Z and cut a vertical hex right
            # through the part instead of a nut pocket.
            half = half.cut(cq.Workplane("XZ").polygon(6, 6.6).extrude(pocket)
                            .translate((x, 7.6, thickness / 2)))
    return half


def make_dry_shaft():
    """Ø5 x 42, from inside the dry cup (85) out to the Oldham hub A (127).
    Grip points: the cup's 3 M3 at 95..101, a stop collar at 106, hub A at 113."""
    # 37 mm, 85..122: the end sits exactly at the Oldham hub A's slot floor, so the
    # disc's tongue can cross that face without running into the shaft
    return cq.Workplane("XY").circle(2.5).extrude(37).translate((0, 0, 85))


def make_dry_bearing():
    """Placeholder for the 695ZZ (13 x 5 x 4, 2Z) in the barrel's internal spider.
    It is what takes the 56 N of magnet pull off the motor: the dry collar at 106
    pushes the inner ring, the boss holds the outer ring."""
    return (cq.Workplane("XY").circle(6.5).circle(2.5).extrude(4)
            .translate((0, 0, 105)))


def make_motor_plate():
    """Ø44 x 5.5 plate carrying the motor, bolted to the frame's cradle by four
    M3 x 12 on r 17 - a SEPARATE part on purpose: if the pattern is wrong he
    reprints 7 cm3 in half an hour, not the 12 hour frame.

    Eight holes is correct, not a mistake: four at r 17 go into the frame's cradle,
    four at r 12.9 go into the motor, and the Ø12.4 centre clears the motor's Ø11.6
    rotating boss. They cannot be the same four - the motor's screws have to end
    inside the motor.

    Pattern is straight off the GB2208 datasheet: 4-M3 on 16 x 19 mm centre to
    centre, so (±8.0, ±9.5). Filip's caliper read 13.60 and 16.60 inner wall to inner
    wall, which is 16.1 and 19.1 once the Ø2.5 tapping size is added - a tenth off.
    The plate's holes are Ø3.4 clearance so the screw slides through and threads into
    the motor.

    Thickness: the motor's threads are 2.5 deep and the shortest M3 he has is x8, so
    5.5 mm - and NO counterbore, which would only push the tip further in.
    """
    plate = cq.Workplane("XY").circle(22).extrude(5.5)
    plate = plate.cut(cq.Workplane("XY").circle(6.4).extrude(16).translate((0, 0, -5)))
    for sx in (-1, 1):
        for sy in (-1, 1):
            plate = plate.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
                1.7, 12, cq.Vector(sx * 8.0, sy * 9.5, -4), cq.Vector(0, 0, 1))))
    for ang in (0.0, 90.0, 180.0, 270.0):
        a = math.radians(ang)
        plate = plate.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
            1.7, 12, cq.Vector(17 * math.cos(a), 17 * math.sin(a), -4),
            cq.Vector(0, 0, 1))))
    # cable relief: the motor's lead leaves radially at its rim (r 13.75) and would
    # be crushed between this plate and the motor's face. A radial slot 4 wide x 1.5
    # deep on the motor side lets it out at any angle.
    plate = plate.cut(cq.Workplane("XY").box(4.0, 40, 1.5).translate((0, 15, 3.25)))
    return plate


def make_oldham_hub_a():
    """115.5..123.5, C-ring gripping the dry shaft's end with one M2 x 12 across a
    single saw cut. The cut runs from the OD to the bore on the +X side only, so the
    ring stays one piece; the bolt sits at x 10.5, through material on both sides of
    the cut, and its slot on the downstream face takes the disc's upstream tongue.
    The shaft stops at 122, exactly at the slot floor."""
    h = cq.Workplane("XY").circle(14).circle(2.475).extrude(8).translate((0, 0, 115.5))
    # saw cut: 1.4 mm wide, from just past the bore (x 1.5) out past the OD (x 15)
    h = h.cut(cq.Workplane("XY").box(13.5, 1.4, 20).translate((8.25, 0, 119.5)))
    # M2 x 12 across the cut
    h = h.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
        0.85, 40, cq.Vector(10.5, 0, 119.5), cq.Vector(0, 1, 0))))
    h = h.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
        1.9, 1.8, cq.Vector(10.5, 14.2, 119.5), cq.Vector(0, -1, 0))))
    h = h.cut(cq.Workplane("XZ").polygon(6, 5.0).extrude(1.8)
              .translate((10.5, 14.2, 119.5)))
    # slot for the disc's tongue
    h = h.cut(cq.Workplane("XY").box(10.4, 3.4, 1.5).translate((0, 0, 122.75)))
    return h


def make_oldham_disc():
    """123.5..127.5, Ø26, a 10 x 3 x 1.5 tongue on each face at 90 deg."""
    d = cq.Workplane("XY").circle(13).circle(3.5).extrude(4).translate((0, 0, 123.5))
    d = d.union(cq.Workplane("XY").box(10, 3, 1.5).translate((0, 0, 122.75)))
    d = d.union(cq.Workplane("XY").box(3, 10, 1.5).translate((0, 0, 128.25)))
    return d


def make_oldham_hub_b():
    """127.5..133, bolted to the motor's rotating bell: 4-M2 at 4.5 mm from the axis
    on both axes, i.e. a 9 mm square on a Ø12.7 bolt circle - datasheet, and it agrees
    with Filip's 7.25 inner-to-inner + 1.6 tapping size = 8.85. 5.5 mm thick because
    the bell's M2 threads are 2.5 mm deep and the shortest M2 he has is x8."""
    h = cq.Workplane("XY").circle(13).circle(4).extrude(5.5).translate((0, 0, 127.5))
    h = h.cut(cq.Workplane("XY").box(3.4, 10.4, 1.5).translate((0, 0, 128.25)))
    for sx in (-1, 1):
        for sy in (-1, 1):
            h = h.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
                1.2, 12, cq.Vector(sx * 4.5, sy * 4.5, 126), cq.Vector(0, 0, 1))))
    return h


def make_oldham():
    """Assembly view: the three parts in place. It transmits 0.164 N*m and ZERO
    axial force, which is the whole reason the motor's bearings never see the
    56 N of magnet pull."""
    return (make_oldham_hub_a().union(make_oldham_disc()).union(make_oldham_hub_b()))


def make_engine_block():
    """The whole dry train on ONE removable part: bearing boss, motor mount, closing
    plate and cable glands. It slides in from behind, bolts to the barrel's flange,
    and the sensor cage then bolts to its outer face.

    NOTHING but the motor lives inside. Filip's call: the electronics go out on the
    pole, which the prototype does not have, so the pod carries the motor and the
    sensors - which is why there is no PCB shelf in here.

      105..115     Ø20 bearing boss, Ø13 pocket from behind; the shoulder at 105 stops
                   the 695ZZ and the dry cup's clamp butts its inner ring
      106..114     four spokes out to r 30
      110..205     four arms at r 25..45, clear of hub B and the Ø44 motor plate
      161.5..166.5 Ø52 motor ring, four tapped M3 at r 17, Ø12.8 centre
      193..205     Ø96 spigot, a RING (r 42..50) not a disc: 26 cm3 instead of 87
      205..211     Ø136 plate ring, 6x M4 at r 61.5, two Ø8 cable glands at r 30
    """
    plate = cq.Workplane("XY").circle(68).circle(47).extrude(6).translate((0, 0, 205))
    plate = plate.union(cq.Workplane("XY").circle(48).circle(42).extrude(12).translate((0, 0, 193)))
    for i in range(6):
        a = math.radians(60 * i)
        x, y = 61.5 * math.cos(a), 61.5 * math.sin(a)
        plate = plate.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
            2.25, 24, cq.Vector(x, y, 200), cq.Vector(0, 0, 1))))
        plate = plate.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
            3.75, 3.4, cq.Vector(x, y, 211.5), cq.Vector(0, 0, -1))))
    for ang in (30.0, 210.0):
        a = math.radians(ang)
        x, y = 30 * math.cos(a), 30 * math.sin(a)
        plate = plate.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
            4.0, 24, cq.Vector(x, y, 190), cq.Vector(0, 0, 1))))
        plate = plate.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
            5.5, 3.0, cq.Vector(x, y, 205), cq.Vector(0, 0, 1))))
    ring = cq.Workplane("XY").circle(26).circle(6.4).extrude(5).translate((0, 0, 161.5))
    for ang in (0.0, 90.0, 180.0, 270.0):
        a = math.radians(ang)
        ring = ring.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
            1.3, 6.0, cq.Vector(17 * math.cos(a), 17 * math.sin(a), 161.5),
            cq.Vector(0, 0, 1))))
    arms = None
    for i in range(4):
        leg = (cq.Workplane("XY").box(20, 8, 95).translate((35, 0, 157.5))
               .rotate((0, 0, 0), (0, 0, 1), 45 + 90 * i))
        arms = leg if arms is None else arms.union(leg)
    # shoulder at 105.3, not 105.0: the dry cup's face is located by this shoulder
    # through the clamp, so the shoulder has to hold it 0.3 mm CLEAR of the bulkhead.
    # Otherwise print tolerance alone can press the spinning cup into the wall.
    boss = (cq.Workplane("XY").circle(10).extrude(10.3).translate((0, 0, 105.3))
            .cut(cq.Workplane("XY").circle(2.7).extrude(30).translate((0, 0, 95)))
            .cut(cq.Workplane("XY").circle(6.5).extrude(10.3).translate((0, 0, 105.3))))
    sp = None
    for i in range(4):
        # pulled in to 18: at 20 the spoke only TOUCHED the Ø20 boss at r 10, a
        # coincident face OCC leaves as a separate body. 2 mm of real overlap now.
        spoke = (cq.Workplane("XY").box(20, 10, 8).translate((18, 0, 110))
                 .rotate((0, 0, 0), (0, 0, 1), 45 + 90 * i))
        sp = spoke if sp is None else sp.union(spoke)
    # ---- electronics box, open toward the closing plate so you can reach into it
    # through the Ø94 opening once the frame is seated. 64 x 40 x 24 outside, 1.8 mm
    # walls: an ESP32-S3 board and a supercap sit side by side, and the four arms run
    # on the diagonals so the box's corners clear them.
    bw, bl, bz0, bz1, th = 64.0, 40.0, 165.5, 189.5, 1.8
    shell = (cq.Workplane("XY").box(bw, bl, bz1 - bz0).translate((0, 0, (bz0 + bz1) / 2))
             .cut(cq.Workplane("XY").box(bw - 2 * th, bl - 2 * th, bz1 - bz0 + 2)
                  .translate((0, 0, (bz0 + bz1) / 2 + th))))
    # No PCB standoffs: four posts sunk into the floor kept coming out as separate
    # bodies (coincident faces again) and they are not worth the risk - the box is a
    # pocket to stuff, and a board can be hot-glued or screwed later.
    for sx in (-1, 1):
        shell = shell.cut(cq.Workplane("XY").box(6, 10, 4)
                          .translate((sx * (bw / 2), 0, bz1 - 1.5)))
    return plate.union(ring).union(arms).union(boss).union(sp).union(shell)



def make_shaft():
    # 78 mm, from the hub's front face (0) to the cup's clamp boss (78). The old
    # 115 mm version reached 37 mm into what is now the nose cone and shared
    # 275 mm3 with it.
    #
    # Plain round bar, Ø5 x 78, no flat and no cross hole. Everything grips it
    # from the side with M3 screws instead: 3 at the hub, 3 at the cup.
    sh = cq.Workplane("XY").circle(2.5).extrude(78)
    return sh

def make_cup(flavour="wet"):
    """Ø70 x 10 magnet cup, FLAT back face, no clamp boss.

    Same move as the rotor: the shaft clamp is a separate two-piece part bolted to
    this face, so the cup is a plain disc with eight blind magnet pockets. What the
    old Ø14 boss did - grip the shaft with three M3 tips biting into plastic - is
    now a 12 mm sleeve squeezed by two M3 x 12 across a split, with a Ø4.90 bore
    that is 0.1 mm under the shaft.

    Back face carries: Ø6 clearance bore, Ø30 x 2 centring recess (71..73 on the wet
    side), and four Ø2.6 x 6 holes on r 18.5 for M3 x 12. r 18.5 sits between the
    recess (r 15) and the magnet pockets (22.9..33.1), so nothing is weakened.
    """
    cup = cq.Workplane("XY").circle(MAGCUP_D / 2).extrude(CUP_BODY)
    cup = cup.cut(cq.Workplane("XY").circle(3.0).extrude(CUP_BODY + 20).translate((0, 0, -10)))
    cup = cup.cut(cq.Workplane("XY").circle(15.0).extrude(1.0))   # Ø30 spigot recess
    for ang in (45.0, 135.0, 225.0, 315.0):
        a = math.radians(ang)
        cup = cup.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
            1.3, 5.0, cq.Vector(18.5 * math.cos(a), 18.5 * math.sin(a), 0.0),
            cq.Vector(0, 0, 1))))
    for i in range(MAG_N):
        th = 2 * math.pi * i / MAG_N
        r = MAGCUP_D / 2 - MAG_D / 2 - 2
        # cut from the BACK face (z 0) up to 5.2, leaving MEMBRANE at the magnet face.
        # The cup prints magnet-face DOWN, so that membrane is the first three layers
        # on the bed - solid and flat, no bridging, no sag.
        cup = cup.cut(cq.Workplane("XY").circle(MAG_D / 2 + 0.1).extrude(MAG_H + 0.2)
                      .translate((r * math.cos(th), r * math.sin(th), 0.0)))
    return cup


def make_cup_cover():
    """Ø70 x 2 lid that closes all twelve pockets from behind, so the magnets cannot
    leave backwards and no glue is trusted for retention. A Ø29.8 x 1 spigot centres
    it in the cup's recess, Ø12 clears the shaft, and the cup clamp's four M3 x 12 go
    straight through it - the cover has no screws of its own."""
    cov = cq.Workplane("XY").circle(MAGCUP_D / 2).extrude(2.0)
    cov = cov.union(cq.Workplane("XY").circle(14.9).extrude(1.0).translate((0, 0, 2.0)))
    cov = cov.cut(cq.Workplane("XY").circle(6.0).extrude(10).translate((0, 0, -2)))
    for ang in (45.0, 135.0, 225.0, 315.0):
        a = math.radians(ang)
        cov = cov.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
            1.7, 10, cq.Vector(18.5 * math.cos(a), 18.5 * math.sin(a), -2),
            cq.Vector(0, 0, 1))))
    return cov


def make_magnets(dry=False):
    """12 discrete N52 discs, each dropped in from the BACK and sitting 0.2 mm off the
    cup's back face, magnet face 0.45 mm behind the printed membrane."""
    out = None
    for i in range(MAG_N):
        th = 2 * math.pi * i / MAG_N
        r = MAGCUP_D / 2 - MAG_D / 2 - 2
        m = (cq.Workplane("XY").circle(MAG_D / 2).extrude(MAG_H)
             .translate((r * math.cos(th), r * math.sin(th), 0.2)))
        out = m if out is None else out.union(m)
    return out

def make_generator():
    """T-Motor GB2208: Ø27.5 x 23, Ø6 through bore, bell at the upstream end."""
    body = cq.Workplane("XY").circle(27.5 / 2).extrude(23)
    return body.cut(cq.Workplane("XY").circle(3).extrude(30).translate((0, 0, -3)))

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
    # every union here overlaps its neighbour by 1 mm. Faces that land exactly on
    # each other (wall face at z 0, boss base at z 0) are the class of bug that
    # made the 695ZZ seat come out as a separate -0.8 cm3 inverted body.
    # The wall MUST stay exactly -4..0: its wet face seats the cup's thrust washer
    # at 81 and its dry face is the magnet-gap datum at 85. So the union overlap
    # goes on the OUTSIDE of the tube instead - a 1 mm collar at r 48..55 that
    # fuses the wall to the barrel without touching the dry cup (r <= 35).
    wall = (cq.Workplane("XY").circle(POD_OD / 2).extrude(WALL_T).translate((0, 0, -WALL_T))
            .union(cq.Workplane("XY").circle(POD_OD / 2).circle(POD_ID / 2).extrude(1)))
    rib = cq.Workplane("XY").circle(POD_ID / 2).circle(40).extrude(11).translate((0, 0, -1))
    pod = tube.union(wall).union(rib)
    # NO bearing boss on the dry face. A Ø20 boss there reaches into the dry
    # cup's body (85..95) and, worse, any boss long enough to seat a 695ZZ
    # (13x5x4) pushes the cup back and the magnet gap goes from 4.4 to 9.4 mm,
    # where the coupling slips. The dry shaft is carried by a bearing in a
    # SPIDER downstream instead - three legs off the barrel wall into a central
    # boss, which is the arrangement Filip described.
    # 1 mm recess in the WET face for the cup's PTFE thrust washer. The magnets
    # pull the wet cup downstream with ~56 N; without a washer that is ABS
    # sliding on ABS at 0.73 m/s, which grooves in hours and the groove changes
    # the magnet gap. The washer takes 1 mm out of the wall and puts 1 mm of
    # PTFE in the same 4.4 mm window, so the magnetic gap does not move.
    pod = pod.cut(cq.Workplane("XY").circle(35).circle(3).extrude(1.5)
                  .translate((0, 0, -WALL_T - 0.5)))
    # Four spider bosses on the wet face, with BLIND M4 insert seats. The seat is
    # Ø6.3 x 7 from the boss's wet end, so it bottoms 7 mm short of the dry face
    # and the 4 mm wall behind it is untouched: a section through the wall is a
    # continuous disc at every depth (checked). This is the difference between a
    # blind boss and a hole through the barrier - and it also fixes the screw:
    # M4x20 through a 6 mm ear would travel 14 mm and land exactly ON the dry
    # face. M4x12 is the length that fits.
    for i in range(4):
        a = math.radians(45 + 90 * i)
        x, y = 45 * math.cos(a), 45 * math.sin(a)
        pod = pod.union(cq.Workplane("XY").circle(5.5).extrude(11)
                        .translate((x, y, -14)))
        pod = pod.cut(cq.Workplane("XY").circle(3.15).extrude(7)
                      .translate((x, y, -14)))
    # O-ring groove on the downstream face
    # Groove for an NBR70 Ø100 x 2.5 ring: 3.0 wide x 1.8 deep. It was 2.2 wide,
    # which gives 2.2*1.8 = 4.0 mm2 of groove for 4.9 mm2 of cord rubber - the
    # ring would have had to extrude out of the joint. 3.0 x 1.8 = 5.4 mm2 holds
    # the displaced volume, mean Ø102.8 against a 102.5 cord mean is ~0 stretch,
    # squeeze (2.5-1.8)/2.5 = 28%, and both lands stay over 1.8 mm.
    pod = pod.cut(cq.Workplane("XY").circle(52.9).circle(49.9).extrude(2.8)
                  .translate((0, 0, POD_LEN - 1.8)))
    # Flange, not six lugs. The lugs were at r 46..58 with their Ø4.5 holes at
    # r 52.5 - straight through the O-ring band (49.9..52.9), so the seal ran
    # round the lugs instead of a flat face, and there was nowhere for a nut.
    # A continuous flange r 55..68 keeps the whole sealing face flat and puts the
    # joint outboard of the groove: 1.9 mm of land inside, 2.1 mm outside.
    flange = (cq.Workplane("XY").circle(68).circle(55).extrude(6)
              .translate((0, 0, POD_LEN - 6)))
    pod = pod.union(flange)
    # ---- mount pad on the OUTER wall, +Y side. A boss, not a collar: four blind M5
    # holes (Ø4.2 tap drill) go 12 mm in from the flat outer face and stop short of
    # the Ø96 bore, so the wall is never pierced and the dry side stays dry. The Ø10
    # duct runs axially THROUGH the pad's own body at r 64 - also clear of the wall -
    # and is where the cables come out. Rotate the pod about its axis to put the pad
    # wherever the structure needs it; the flange has 60 deg symmetry, so it is free.
    pad = cq.Workplane("XY").box(52, 20, 60).translate((0, 62, 70))
    pod = pod.union(pad)
    for sx in (-1, 1):
        for z in (48.0, 92.0):
            pod = pod.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
                2.1, 12, cq.Vector(sx * 16, 72.5, z), cq.Vector(0, -1, 0))))
    pod = pod.cut(cq.Workplane(obj=cq.Solid.makeCylinder(
        5.0, 80, cq.Vector(0, 64, 30), cq.Vector(0, 0, 1))))
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
    # boss 47..61, Ø18, TWO iglidur bushings 14 mm apart - Filip is right that the
    # pair has to spread the propeller's bending moment, and he cuts the shaft to
    # whatever length the stack needs.
    # boss 40..54: two bushings, 14 mm of span end to end (40..47 and 47..54), so the
    # pair still spreads the propeller's bending moment. Moving the boss 7 mm upstream
    # is what buys the cup's clamp the same 19 mm the rotor's has - the shaft simply
    # gets 7 mm longer at the propeller end, and Filip cuts it himself.
    boss = (cq.Workplane("XY").circle(9).extrude(16.35).translate((0, 0, 40))
            .cut(cq.Workplane("XY").circle(2.5).extrude(30).translate((0, 0, 34))))
    b1 = cq.Workplane("XY").circle(3.5).circle(2.5).extrude(7).translate((0, 0, 40.2))
    b2 = cq.Workplane("XY").circle(3.5).circle(2.5).extrude(7).translate((0, 0, 47.6))
    boss = boss.cut(b1).cut(b2)
    # Three spokes 59..67. They must overlap the boss axially: the boss is Ø18
    # (r 9) and the spokes need a Ø15 hole for the cup's Ø14 clamp boss, so their
    # inner edge can never reach the boss radially - at 61..69 the two only met
    # on a 1.5 mm wide coplanar ring at z 61, which reads as a floating boss with
    # a notch in it. At 59..67 there are 2 mm of real 3D overlap.
    arms = None
    for i in range(3):
        a = (cq.Workplane("XY").box(48, 9, 6)
             .translate((24, 0, 49))
             .rotate((0, 0, 0), (0, 0, 1), i * 120))
        arms = a if arms is None else arms.union(a)
    arms = arms.cut(cq.Workplane("XY").circle(7.5).extrude(40).translate((0, 0, 40)))
    # ring 65..71 at r 42..48 sits on the four bulkhead bosses (71..81)
    # ring 50..71, not 57..71: the spokes moved upstream with the boss (46..52), and
    # at 57..71 they did not reach it at all - the carrier came out as two bodies
    ring = cq.Workplane("XY").circle(47).circle(42).extrude(21).translate((0, 0, 50))
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
# the whole rotor moves 7 mm upstream so its hub face meets the clamp at 21 instead of
# 28: that is the 7 mm which lets both clamps be the same 19 mm part
parts["rotor"] = parts["rotor"].translate((0, 0, -7.0))
# ---- explicit axial layout (local Z, before the pod is laid horizontal) ----
# upstream -> downstream: weed guard | rotor | carrier | wet cup | WALL | pod | adapter | cage
Z_SHAFT   = 0     # shaft spans -37..78 (115 mm), hub grips at -31, cup at 67
Z_CARRIER = 15    # wet bearing carrier 47..71
Z_WETCUP  = 81 - CUP_BODY   # 75.35: magnet face stays on the bulkhead at 81
Z_POD     = 85    # pod: wall 80..85, barrel 85..205
Z_DRYCUP  = 85.3  # dry cup face 0.3 mm clear of the wall: its position is set by
                  # the clamp butting the frame's shoulder, not by the wall
Z_ADAPTER = 205   # transition cone 205..225
Z_CAGE    = 225   # cage 225..425
Z_GUARD   = -50   # weed guard ring, upstream of the blade plane

parts["shaft"]       = make_shaft().translate((0,0,Z_SHAFT))
parts["wet_carrier"] = make_wet_carrier()
# the two Ø14 collars are gone: the shaft is trapped by the hub's aft face on
# one side of the spider boss and by the cup's clamp boss on the other, with a
# 1 mm PTFE thrust washer at -46..-47. Nothing rides on a grub screw in shear.
# No washer in the hub's clearance any more: the cup pressed on the bulkhead
# sets the axial position, so a second thrust surface at 46..47 would fight it.
# PRINTED, not bought: ABS ring Ø24/Ø8 x 1 (r 4..12). It is a consumable - 4
# minutes on the printer. Putting the contact ring small matters: at r 4..12 the
# mean sliding speed is 0.36 m/s and the pressure 0.14 MPa, i.e. PV 0.05
# MPa*m/s, which ABS in water handles. The same ring at r 12..34 would run at
# 0.73 m/s and 0.09 MPa on a much bigger area, and it was the version that
# grooved.
parts["cup_washer"] = (cq.Workplane("XY").circle(12).circle(4).extrude(1)
                       .translate((0, 0, Z_POD - WALL_T)))
parts["rotor_clamp"] = make_rotor_clamp()
parts["magcup_wet"]  = make_cup().translate((0,0,Z_WETCUP))
parts["cup_clamp_wet"] = make_cup_clamp().mirror("XY").translate((0, 0, 75.35))

parts["pod"]         = make_pod().translate((0,0,Z_POD))
# mirror("XY") flips Z, which is what a part BUILT along Z needs; mirror("XZ")
# flips Y and is a no-op on a body of revolution - it silently leaves the cup
# facing the wrong way, with its magnet pockets pointing into the cage.
parts["magcup_dry"]  = make_cup("dry").mirror("XY").translate((0,0,Z_DRYCUP + CUP_BODY))
parts["cup_clamp_dry"] = make_cup_clamp().mirror("XY").translate((0, 0, Z_DRYCUP + CUP_BODY))

parts["joints"] = make_joints()
# same frame as the cup: built along Z, mirrored like cup A, no extra rotation
parts["magnets_wet"] = make_magnets().translate((0,0,Z_WETCUP))
parts["magnets_dry"] = make_magnets(dry=True).mirror("XY").translate((0,0,Z_DRYCUP + CUP_BODY))
parts["dry_shaft"]   = make_dry_shaft()
parts["dry_bearing"] = make_dry_bearing()

parts["oldham_hub_a"] = make_oldham_hub_a()
parts["oldham_disc"]  = make_oldham_disc()
parts["oldham_hub_b"] = make_oldham_hub_b()
parts["generator"]   = make_generator().translate((0,0,133))
parts["motor_plate"] = make_motor_plate().translate((0, 0, 156))
parts["engine_block"]= make_engine_block()
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
             "wet_carrier","cup_washer","dry_shaft","dry_bearing","oldham_hub_a","oldham_disc","oldham_hub_b","cup_clamp_wet","cup_clamp_dry","motor_plate","engine_block","rotor_clamp","sensors","cage_adapter","generator","joints","magnets_wet","magnets_dry"]
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
    "wet_carrier": (0.45, 0.50, 0.58), "cup_washer": (0.90, 0.90, 0.60), "dry_shaft": (0.55,0.55,0.58),
    "dry_bearing": (0.75,0.75,0.78), "cup_clamp_wet": (0.62,0.45,0.30), "cup_clamp_dry": (0.62,0.45,0.30), "rotor_clamp": (0.95,0.62,0.20), "motor_plate": (0.40,0.62,0.45),
    "oldham_hub_a": (0.80,0.45,0.80), "oldham_disc": (0.70,0.35,0.75), "oldham_hub_b": (0.80,0.45,0.80), "engine_block": (0.35,0.55,0.75),
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
