#!/usr/bin/env python3
"""
FreeCAD parametric build of the sub-mission rotor.
Run: freecad -c path/to/rotor_freecad.py
Outputs: rotor.step + rotor.fcstd + a render PNG via a headless screenshot if the GUI is up.
"""
import FreeCAD as App
import Part, math, os
from FreeCAD import Vector

# ------------- NACA 4412 analytic (same as OpenSCAD version) -------------
def naca_pts(n=32, m=0.04, p=0.4, t=0.12):
    # finite trailing edge: 0.1016 instead of 0.1036 keeps TE open ~0.0008 chord,
    # then we close the face explicitly. Fixes FreeCAD makeLoft producing shells.
    def yt(x): return 5*t*(0.2969*math.sqrt(x)-0.1260*x-0.3516*x*x+0.2843*x**3-0.1016*x**4)
    def yc(x):
        return m/(p*p)*(2*p*x-x*x) if x<p else m/((1-p)**2)*((1-2*p)+2*p*x-x*x)
    def dyc(x):
        return 2*m/(p*p)*(p-x) if x<p else 2*m/((1-p)**2)*(p-x)
    up=[]; lo=[]
    for i in range(n+1):
        x=0.5*(1-math.cos(math.pi*i/n))
        th=math.atan(dyc(x))
        up.append(Vector(x - yt(x)*math.sin(th), yc(x)+yt(x)*math.cos(th), 0))
        lo.append(Vector(x + yt(x)*math.sin(th), yc(x)-yt(x)*math.cos(th), 0))
    # keep both TE points distinct (they differ by ~0.0008 chord), plus close at LE
    pts = up + lo[-1::-1]
    return pts

def naca_wire(n=32):
    # closed wire as a periodic BSpline through NACA points
    pts = naca_pts(n)
    pts.append(pts[0])  # explicit closure for interpolation
    bs = Part.BSplineCurve()
    bs.interpolate(pts)
    return bs.toShape()

# ------------- build one twisted blade via real loft -------------
def blade_solid(rotor_r=110, root_cut=0.2, stations=None):
    if stations is None:
        stations=[(0.20,42,28),(0.40,38,20),(0.55,34,12),(0.70,30,6),(0.85,24,3),(1.00,17,2)]
    faces=[]
    for rf, chord, twist_deg in stations:
        r = rotor_r*rf
        pts = naca_pts(40)
        wire = Part.makePolygon(pts + [pts[0]])
        # translate so quarter-chord sits at origin (pitch axis)
        wire.translate(Vector(-0.25, 0, 0))
        m = App.Matrix(); m.scale(chord,chord,1)
        wire = wire.transformGeometry(m)
        # twist about quarter-chord (now at local origin)
        wire.rotate(Vector(0,0,0), Vector(0,0,1), -twist_deg)
        wire.translate(Vector(r,0,0))
        faces.append(Part.Face(wire))
    loft = Part.makeLoft(faces, True)
    return loft

def hub_solid(d=64, h=46):
    return Part.makeCylinder(d/2, h, Vector(0,0,-h/2), Vector(0,0,1))

def rotor(blades=3):
    hub = hub_solid()
    blade = blade_solid()
    parts=[hub]
    for i in range(blades):
        b = blade.copy()
        b.rotate(Vector(0,0,0), Vector(0,0,1), i*360/blades)
        parts.append(b)
    comp = Part.makeCompound(parts)
    return comp

out = rotor()
doc = App.newDocument("rotor")
Part.show(out, "rotor")
App.ActiveDocument.recompute()

d="/home/filip/sub-mission/cad/freecad"
os.makedirs(d, exist_ok=True)
doc.saveAs(f"{d}/rotor.fcstd")
out.exportStep(f"{d}/rotor.step")
print("saved", f"{d}/rotor.fcstd", f"{d}/rotor.step")
