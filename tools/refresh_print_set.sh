#!/bin/sh
# Regenerate the print set AND re-apply the mesh post-processes.
#
# export_print_stls.py builds 01_rotor_vrtula.stl straight from probe_cq.py, which does NOT
# contain the blade-root corner fills - those were added as separate cylinders in a mesh
# boolean (tools/fill_corners.py). Running the exporter alone silently drops them and the
# print set no longer matches the approved gcode. Always run this script instead.
set -e
cd "$(dirname "$0")/.."
/usr/bin/python3 tools/export_print_stls.py
.cadvenv/bin/python tools/fill_corners.py print/01_rotor_vrtula.stl print/_rotor_filled.stl --radius 6
mv print/_rotor_filled.stl print/01_rotor_vrtula.stl
.cadvenv/bin/python - <<'PY'
import trimesh, numpy as np
m = trimesh.load("print/01_rotor_vrtula.stl"); m.merge_vertices()
_, c = np.unique(m.edges_sorted, axis=0, return_counts=True)
print(f"rotor: {m.volume/1000:.2f} cm3, watertight {m.is_watertight}, "
      f"bad edges {int((c != 2).sum())}, bodies {len(m.split(only_watertight=False))}")
PY
