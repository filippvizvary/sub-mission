MAGNET RETENTION - v2 IDEA (Filip, 2026-11-10)

Insert the magnets from the BACK of the cup, with a 3-5 layer printed membrane at
the magnet face, so nothing can leave through the face and the pull presses the
magnet INTO the membrane instead of pulling it out of an epoxy plug. Close the back
with a screwed cover. Epoxy optional, no dependency on it curing.

WHY IT IS RIGHT
  Serviceable magnets, no cure waiting, and the retention no longer relies on a
  0.2 mm glue film.

WHAT IT COSTS IN THE CURRENT STACK (measured, not guessed)
  1. The membrane puts the magnet 0.6 mm behind the face. Two cups = the air gap
     goes 4.4 -> 5.2 mm, and coupling torque falls with roughly the 2.5th power of
     the gap: 1.4 -> ~1.0 N*m at 12 magnets. Still 6x the 0.164 N*m load.
  2. A 5 mm magnet under a 0.6 membrane in a 10 mm cup leaves 4.4 mm of empty pocket
     behind it, so the cover needs 12 bosses (one per pocket) or the magnets rattle
     axially when the coupling is apart.
  3. That cover wants 2 mm of axial room, and there is none: 61..71 is exactly the
     wet cup clamp's budget (sleeve end must butt the bushing at 61, flange must sit
     on the cup face at 71). Adding a cover means the clamp shrinks 12 -> 8 mm,
     which halves its friction reserve, or the cup body has to be re-cut.

WHAT THE EPOXY ACTUALLY TAKES TODAY
  Each magnet is pulled toward the gap with ~7 N (56 N over 8 magnets, ~84 N over
  12). That sits on a 0.2 mm plug of 78 mm2 = 0.09 MPa, against a typical epoxy/ABS
  bond of 3-5 MPa. Reserve is 40-55x, and the load is pure tension with the magnet
  fully supported by the pocket walls - the glue only stops it sliding out.

VERDICT
  For the prototype before the Saturday deadline: keep the epoxy. Nothing in the
  numbers says it will fail, and the rework costs 3 parts and a third of the torque
  margin.
  For v2, with a free weekend: do it Filip's way. It is the better design. It needs
  a cup re-cut (8 mm body), both clamps re-cut (8 mm), and a new cover - 4 STLs.
