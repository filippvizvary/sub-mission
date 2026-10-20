# CAD tool decision — 2026-10-18

## Short answer

OpenSCAD is the right tool for this project. FreeCAD with headless Python
scripting works, but the parametric NACA loft for a twisted hydro blade hit
a known OCC kernel issue tonight (twisted+translated airfoil sections loft
to closed shells, not solids). Neither tool is "broken" — the
twisted-blade loft is a genuinely hard solid-modelling problem. Every other
component (pod, cups, cage, mast, site structure, the site itself) is
easier in OpenSCAD, already written, already rendered, and already correct.

## What the renders showed (and why they looked wrong)

The bad-looking PNGs were a mix of:
- tight camera crops
- pastel default OpenSCAD colours
- no ground plane / dimensions / labels
- the vision model reading low-poly facets as geometry defects

A mesh-topology check (connected-component analysis on the exported STL)
told the truth: the OpenSCAD model was fragmented into 669 disconnected
shells. That is a genuine defect of the hull-of-thin-airfoils approach, not
an OpenSCAD defect per se. The fix in OpenSCAD is a different module
strategy — thick 3D airfoil extrusions per station instead of 0.1mm
slices, plus explicit hull bridges — which is a 30-minute fix, not a
tool-switch.

## What was produced tonight

- `cad/probe_v1r1.scad`  — full parametric site + pod + sensors + box
- `cad/naca4412.scad`    — analytic NACA generator (works in both tools)
- `cad/rotor_freecad.py` — FreeCAD parametric rotor (WIP; loft outstanding)
- `cad/freecad/rotor.step` — partial STEP export for inspection only
- `sim/simulate_v3.py`   — physics-corrected energy sim
- `docs/BOM_V1.md`       — full Slovak-sourced bill of materials
- `docs/frontier/`       — fabrication spec, field-failure, rotor sweep, sim review

## Next step

Fix the blade loft in OpenSCAD (thick-section hull bridges; verified
against a printed blade profile). If a STEP export is ever needed for a
machinist, come back to FreeCAD with a dedicated session for the rotor
only — the OCC workaround for twisted NACA lofts is known (periodic
spline + guide rails) but not something to bolt on at 11:50pm.
