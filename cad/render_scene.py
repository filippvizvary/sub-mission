#!/usr/bin/env python3
"""Final scene render: the probe in a river, bank + water + sky included."""
import trimesh, os, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D, art3d
from matplotlib.patches import Polygon as P2

CQ="/home/filip/sub-mission/cad/cq"
OUT="/home/filip/.hermes/profiles/haven/cache/scratch/renders"
os.makedirs(OUT, exist_ok=True)

# ---- parts with colors + labels ----
PARTS = {
  "site_pole":      ("dimgray", 1.0),
  "site_collar":    ("black", 1.0),
  "site_arm":       ("slategray",1.0),
  "site_drop":      ("slategray",1.0),
  "site_strut":     ("slategray",1.0),
  "site_box":       ("khaki", 1.0),
  "site_lid":       ("darkkhaki",1.0),
  "site_antenna":   ("black",1.0),
  "site_antenna_tip":("crimson",1.0),
  "site_cable":     ("black",1.0),
  "anchor":         ("silver",1.0),
  "guys":           ("dimgray",1.0),
  "safety_cable":   ("silver",1.0),
  "rotor":          ("darkorange",1.0),
  "shaft":          ("darkgray",1.0),
  "magcup_wet":     ("gray",1.0),
  "magcup_dry":     ("gray",1.0),
  "pod":            ("seagreen",1.0),
  "pod_seal":       ("seagreen",1.0),
  "wet_carrier":    ("slategray",1.0),
  "weed_guard":     ("forestgreen",1.0),
  "cage":           ("royalblue",1.0),
  "sensors":        ("whitesmoke",1.0),
}

def load(name):
    p=os.path.join(CQ,f"{name}.stl")
    if not os.path.exists(p): return None
    return trimesh.load(p)

def add_part(ax, m, color, alpha):
    if m is None: return
    if len(m.faces)>20000:
        m = m.simplify_quadric_decimation(20000)
    coll = art3d.Poly3DCollection(
        m.vertices[m.faces],
        facecolor=color, alpha=alpha,
        edgecolor=(0,0,0,0.06), linewidths=0.05)
    ax.add_collection3d(coll)

def add_plane(ax, mn_x, mx_x, mn_y, mx_y, z, color, alpha):
    # simple quad as a big polygon at height z
    verts = np.array([[mn_x,mn_y,z],[mx_x,mn_y,z],[mx_x,mx_y,z],[mn_x,mx_y,z]])
    coll = art3d.Poly3DCollection([verts], facecolor=color, alpha=alpha, edgecolor="none")
    ax.add_collection3d(coll)

def render(name, view_elev, view_az, pod_zoom=False):
    fig = plt.figure(figsize=(16,10))
    ax = fig.add_subplot(111, projection="3d")
    # parts
    for part,(color,alpha) in PARTS.items():
        m=load(part)
        if m is None: continue
        if pod_zoom and part.startswith("site_") and part not in ("site_drop","site_elbow"):
            continue   # pod-only view
        add_part(ax, m, color, alpha)
    # river: water surface + riverbed + bank
    if not pod_zoom:
        add_plane(ax, 100, 2000, -700, 700, 0,     "deepskyblue", 0.32)      # water surface
        add_plane(ax, 100, 2000, -700, 700, -800,  "saddlebrown", 0.85)      # riverbed
        add_plane(ax, -1400, 80,  -700, 700, 0,    "darkgreen", 0.95)        # bank (tops at 0)
        # water column between surface and bed: side wall to fake depth
        side = np.array([[100,700,-800],[100,700,0],[2000,700,0],[2000,700,-800]])
        art3d.Poly3DCollection([side], facecolor="deepskyblue", alpha=0.25, edgecolor="none")
        c = art3d.Poly3DCollection([side], facecolor="deepskyblue", alpha=0.22, edgecolor="none")
        ax.add_collection3d(c)
        side2 = np.array([[100,-700,-800],[100,-700,0],[2000,-700,0],[2000,-700,-800]])
        c2 = art3d.Poly3DCollection([side2], facecolor="deepskyblue", alpha=0.22, edgecolor="none")
        ax.add_collection3d(c2)
    if pod_zoom:
        ax.set_xlim(950, 1500); ax.set_ylim(-180, 180); ax.set_zlim(-700, 100)
    else:
        ax.set_xlim(-300, 1800); ax.set_ylim(-700, 700); ax.set_zlim(-800, 2200)
    ax.set_box_aspect((ax.get_xlim()[1]-ax.get_xlim()[0],
                       ax.get_ylim()[1]-ax.get_ylim()[0],
                       ax.get_zlim()[1]-ax.get_zlim()[0]))
    ax.view_init(elev=view_elev, azim=view_az)
    ax.set_axis_off()
    ax.set_title(name, fontsize=13, pad=6, color="#222")
    fig.savefig(os.path.join(OUT, f"{name}.png"), dpi=150, bbox_inches="tight", facecolor="#f2ecd9")
    plt.close(fig)

render("01 — deployed on riverbank", view_elev=18, view_az=-58, pod_zoom=False)
render("02 — side elevation (upstream view)", view_elev=8, view_az=0, pod_zoom=False)
render("03 — wet pod detail (underwater)", view_elev=14, view_az=-70, pod_zoom=True)
render("04 — top-down over site", view_elev=68, view_az=-50, pod_zoom=False)
print("rendered ->", OUT)
