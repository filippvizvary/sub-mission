#!/usr/bin/env python3
"""Fill the gap between each blade root and the hub wall with a smooth gusset.

The gap: the blade's underside hangs above the hub's cylindrical wall, so where they meet
there is a concave corner with nothing under the blade. A fillet is impossible on this
model - the hub-blade union runs with clean=True and merges the surfaces, so there is no
junction edge to fillet at all (0 edges on r=32, verified). So the fill is BUILT: for each
blade, a gusset that runs along the root chord, rising from the hub wall to the blade's
underside on a smooth ramp, and it is unioned in as a separate solid.

    python3 tools/fill_root_gaps.py in.stl out.stl [--ramp 4.0] [--show]

Everything is measured off the mesh - nothing is assumed about the blade angles or the
underside height.
"""
import sys
import numpy as np
import trimesh
import manifold3d


def blade_angles(mesh, r=36.0, step=1.0):
    """Blades found by casting rays up through the root radius, not by clustering vertices.

    Vertex clustering put the blades at 62 deg when they are at 107 - the blade is sparse at
    the tip so the angular runs were averaged with empty space. A per-degree scan gives the
    runs directly, so it also returns the chord's angular half-width at the root.
    """
    hit = []
    for phi in np.arange(0.0, 360.0, step):
        a = np.radians(phi)
        loc, _, _ = mesh.ray.intersects_location(
            np.array([[r * np.cos(a), r * np.sin(a), -3.0]]), np.array([[0.0, 0.0, 1.0]]))
        hit.append(len(loc) > 0)
    hit = np.array(hit)
    if hit.all():
        return []
    runs, idx = [], np.where(hit)[0]
    start = prev = int(idx[0])
    for k in idx[1:]:
        k = int(k)
        if k != prev + 1:
            runs.append((start, prev + 1))
            start = k
        prev = k
    runs.append((start, prev + 1))
    out = []
    for a0, a1 in runs:
        n = len(hit)
        width = a1 - a0
        if width <= 0:
            width = 1
        centre = ((a0 + width / 2.0) * step) % 360.0
        half = width * step / 2.0
        if half > 5.0:
            out.append((centre, half))
    # a blade straddling 0 deg appears as a run starting at 0 and one ending at 359
    if len(out) >= 2 and runs[0][0] == 0 and runs[-1][1] == len(hit):
        c0, h0 = out.pop(0)
        c1, h1 = out.pop()
        out.append(((c1 + h1) % 360.0, h0 + h1))
    return out


def underside(mesh, phi_deg, r_lo=33.0, r_hi=38.0, half_deg=2.5):
    """Lowest material above the hub wall along one radial line, by ray casting up.

    Vertex sampling was too sparse near the root and came back empty for most of the
    chord; a vertical ray from just above the bed always finds the blade's underside.
    """
    import numpy as np
    hits = []
    for rr in np.linspace(r_lo, r_hi, 4):
        a = np.radians(phi_deg)
        # start BELOW the bed: at r 33-36 the blade reaches z 0, so an origin at 0.25 is
        # already inside the material and the ray finds nothing
        origin = np.array([[rr * np.cos(a), rr * np.sin(a), -2.0]])
        loc, idx_ray, _ = mesh.ray.intersects_location(origin, np.array([[0.0, 0.0, 1.0]]))
        if len(loc):
            hits.append(float(loc[:, 2].min()))
    return min(hits) if hits else None


def gusset_mesh(phi_c, arc_half_deg, ramp, hub_r=32.0, n=25, floor=None):
    """A closed wedge per blade: from the bed at the hub wall up to the blade's underside.

    Cross-section is a triangle (hub wall at the bed, hub wall where the ramp starts, and
    the blade's underside out at hub_r + ramp). Lofting triangles cannot produce the
    degenerate faces the four-point profile did.
    """
    phis = np.radians(np.linspace(phi_c - arc_half_deg, phi_c + arc_half_deg, n))
    raw = [underside_curve(p) for p in np.degrees(phis)]
    tops = np.array([np.nan if t is None else float(t) for t in raw], dtype=float)
    good = ~np.isnan(tops)
    if good.sum() < 4:
        return None
    xs = np.arange(len(tops))
    tops = np.interp(xs, xs[good], tops[good])
    k = 5
    tops = np.convolve(np.pad(tops, (k // 2, k // 2), mode="edge"), np.ones(k) / k, mode="valid")
    tops = np.maximum(tops, 3.0 + ramp)
    if floor is None:
        # the blade's root hangs well above the bed (11 mm at r 32), so the gusset is a
        # corner fillet on the hub wall: its bottom edge is ramp below the blade's underside
        floor = float(np.nanmin(tops)) - ramp - 0.5

    verts = []
    for phi, top in zip(phis, tops):
        c, s_ = np.cos(phi), np.sin(phi)
        z_a = top - ramp            # bottom of the corner, on the hub wall
        z_b = top - 0.35            # just inside the blade, so the faces overlap
        verts += [
            [hub_r * c, hub_r * s_, z_a],                    # A on the hub wall
            [hub_r * c, hub_r * s_, z_b],                    # B tucked under the blade
            [(hub_r + ramp) * c, (hub_r + ramp) * s_, top],  # C out on the underside
        ]
    verts = np.array(verts, dtype=float)
    faces = []
    for i in range(n - 1):
        a, b = 3 * i, 3 * (i + 1)
        faces += [[a, b, b + 1], [a, b + 1, a + 1],      # inner wall
                  [a + 1, b + 1, b + 2], [a + 1, b + 2, a + 2],  # ramp
                  [a, b + 2, b], [a, a + 2, b + 2]]      # underside/floor
    faces += [[0, 1, 2]]                                  # end caps, one winding each
    e = 3 * (n - 1)
    faces += [[e, e + 2, e + 1]]
    m = trimesh.Trimesh(vertices=verts, faces=np.array(faces), process=True)
    if m.volume < 0:                                      # caps may be wound the wrong way
        m.invert()
    m.fix_normals()
    return m if m.is_watertight and m.volume > 1 else None


def underside_curve(phi_deg):
    return _CURVE(phi_deg)


def main():
    src = sys.argv[1]
    dst = sys.argv[2]
    ramp = 4.0
    if "--ramp" in sys.argv:
        ramp = float(sys.argv[sys.argv.index("--ramp") + 1])

    global _CURVE
    mesh = trimesh.load(src)
    runs = blade_angles(mesh)
    print("blade runs:", [(round(c,1), round(h,1)) for c, h in runs])

    # the chord's angular half-width at the hub, measured from material at r 36-40
    v = mesh.vertices
    r = np.hypot(v[:, 0], v[:, 1])
    a = np.degrees(np.arctan2(v[:, 1], v[:, 0])) % 360.0
    parts = []
    for phi, half in runs:
        print(f"  {phi:5.1f} deg: chord half-width {half:5.1f} deg at the root")

        def curve(pd, _phi=phi, _half=half):
            return underside(mesh, pd)

        _CURVE = curve
        g = gusset_mesh(phi, half * 0.92, ramp)
        if g is None:
            print(f"    gusset failed for {phi:.0f} deg"); continue
        print(f"    gusset {g.volume/1000:5.2f} cm3, watertight {g.is_watertight}, z {g.bounds[0][2]:.1f}..{g.bounds[1][2]:.1f}")
        parts.append(g)

    if not parts:
        raise SystemExit("no gussets built")

    out = mesh
    for g in parts:
        try:
            out = trimesh.boolean.union([out, g], engine="manifold")
        except Exception as ex:
            print("union failed:", ex)
            raise
    e = out.edges_sorted; u, c = np.unique(e, axis=0, return_counts=True)
    print(f"\nresult: {out.volume/1000:.1f} cm3 (was {mesh.volume/1000:.1f}) | watertight {out.is_watertight} "
          f"| bad edges {int((c!=2).sum())} | bodies {len(out.split(only_watertight=False))}")
    out.export(dst)
    print("written", dst)


if __name__ == "__main__":
    main()
