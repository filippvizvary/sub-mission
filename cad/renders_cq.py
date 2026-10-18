#!/usr/bin/env python3
"""Render labelled views of the CadQuery assembly with matplotlib + trimesh."""
import trimesh, os, numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D, art3d

CQ="/home/filip/sub-mission/cad/cq"
OUT="/home/filip/.hermes/profiles/haven/cache/scratch/renders"
os.makedirs(OUT, exist_ok=True)

FILES = [
    ("rotor","darkorange",1.0,"rotor (3 blades + hub)"),
    ("shaft","slategray",1.0,"shaft (316L)"),
    ("magcup_wet","dimgray",1.0,"wet magnet cup"),
    ("magcup_dry","dimgray",1.0,"dry magnet cup"),
    ("pod","seagreen",1.0,"generator pod (sealed)"),
    ("cage","royalblue",1.0,"sensor cage"),
    ("site_pole","dimgray",1.0,"pole"),
    ("site_arm","darkgray",1.0,"swing arm"),
    ("site_drop","darkgray",1.0,"drop tube"),
    ("site_box","khaki",1.0,"dry box"),
    ("site_antenna","black",1.0,"antenna"),
]

# load and place pod-side parts together (they're already assembled in Z space),
# site parts sit at world origin; we just render all of them
meshes={}
for name,color,alpha,label in FILES:
    p=os.path.join(CQ,f"{name}.stl")
    if os.path.exists(p):
        meshes[name]=(trimesh.load(p), color, alpha, label)

def render(view_elev=20, view_az=-60, fname="probe_iso", title="sub-mission probe"):
    fig = plt.figure(figsize=(14,10))
    ax = fig.add_subplot(111, projection="3d")
    for name,(m,color,alpha,label) in meshes.items():
        # render only a decimated surface
        if len(m.faces)>20000: m = m.simplify_quadric_decimation(20000)
        verts = np.array(m.vertices); tris = np.array(m.faces)
        coll = art3d.Poly3DCollection(verts[tris], alpha=alpha, facecolor=color, edgecolor=(0,0,0,0.12), linewidths=0.15)
        ax.add_collection3d(coll)
    # bounds
    allv = np.vstack([m.vertices for m,_,_,_ in meshes.values()])
    mn, mx = allv.min(0), allv.max(0)
    span = (mx-mn).max()/2
    ctr = (mx+mn)/2
    ax.set_xlim(ctr[0]-span, ctr[0]+span)
    ax.set_ylim(ctr[1]-span/1.6, ctr[1]+span/1.6)
    ax.set_zlim(mn[2]-20, mx[2]+20)
    ax.view_init(elev=view_elev, azim=view_az)
    ax.set_axis_off()
    ax.set_title(title, fontsize=14, pad=8, color="#222")
    fig.savefig(os.path.join(OUT,f"{fname}.png"), dpi=150, bbox_inches="tight", facecolor="#f5f2ea")
    plt.close(fig)
    print("rendered", fname)

# full scene from 4 views
render(22,-55, "probe_iso",  "sub-mission probe — isometric")
render(15, 30, "probe_alt",  "sub-mission probe — opposite side")
render(5, -90, "probe_side", "sub-mission probe — side elevation")
render(75, -30, "probe_top", "sub-mission probe — top view")

# pod detail (crop site by loading only pod group)
pod_keys = [k for k in meshes if k in ("blade","hub","shaft","magcup_wet","magcup_dry","pod","cage")]
site_save = {k:meshes[k] for k in meshes if k not in pod_keys}
for k in list(site_save): del meshes[k]
render(15,-60,"pod_iso", "wet pod — rotor / cups / generator pod / sensor cage")
render(5,-90,"pod_side","wet pod — side view")
print("done ->", OUT)
