# Build procedure — from boxes to a probe in the water

Nine phases. Each has a **gate**: do not start the next phase until the gate
passes. This is the order that avoids discovering a problem after potting.

## Phase 0 — bench setup (half a day)
- tools out: multimeter, soldering iron, calipers, torque driver if present
- **gate:** you can flash the Wio-E5 mini (blink sketch over USB-C) and read
  its serial output. If this fails, nothing else matters yet.

## Phase 1 — measure the generator (1 h) ← GATING MEASUREMENT
- hang a known weight on a 100 mm arm attached to the motor shaft, find the
  mass where it just starts to turn → cogging torque = m·g·0.1 N·m
- spin it by hand on a drill, measure open-circuit AC voltage vs rpm
- **gate:** cogging ≤ 4 mN·m and you know its real KV. If cogging is higher,
  the 220 mm rotor will not start at low flow — change motor before building.

## Phase 2 — electronics on the bench (1–2 days)
- solder the harvest chain: rectifier → clamp → supercap → buck
- confirm 3.3 V out from a bench supply standing in for the generator
- read every sensor over I2C/analog and print them on serial
- **gate:** all channels print plausible values in a cup of tap water.

## Phase 3 — calibrate sensors (half a day)
- pH: 2-point with 7.00 and 10.00 buffer (skip if no pH module)
- turbidity: clear water vs stirred dirt, record both voltages
- EC/TDS: tap water vs a pinch of salt
- DS18B20: compare to a known thermometer in ice water and warm water
- **gate:** each channel has written calibration constants and a recorded
  uncertainty. No calibration file = do not pot anything.

## Phase 4 — print and post-process (2–3 days)
- print: rotor (3 blades + hub), pod barrel, magnet cups, cage, adapter,
  collar, weed guard, sensor holders
- post: sand blade roots, brush epoxy barrier coat on wet parts, cure
- **gate:** every printed part is dimensionally checked (calipers) against
  the model, and no part is warped.

## Phase 5 — dry assembly, no glue (half a day)
- dry-fit the whole pod chain on the bench: rotor → carrier → wet cup →
  wall → dry cup → pod → adapter → cage
- check the coupling: with the wet cup on the bench side of the wall, turn
  the rotor by hand — the dry cup must follow with no slip at low torque
- measure coupling slip with a spring balance
- **gate:** drivetrain turns freely, no rubbing, slip torque recorded.

## Phase 6 — pressure test (1 day + 24 h waiting)
- assemble the pod with a desiccant pack and a humidity sensor inside
- 0.5 bar vacuum, submerge, hold 24 h — internal humidity must not move
- **gate:** humidity flat and desiccant still blue. A leak here is found on
  the bench, not in the river.

## Phase 7 — potting and final assembly (1 day)
- pot the cable gland, pot the magnet pockets, grease the O-ring
- close the pod, fit the collar clamp, fit the cage
- **gate:** pod is sealed; the cable runs freely through the drop tube.

## Phase 8 — gateway (half a day)
- Wio-E5 mini into the Raspberry Pi over USB, antenna on the mast
- run the packet listener, confirm it prints packets from a second board
  on the bench
- **gate:** the Pi logs a packet from the probe across the room.

## Phase 9 — field (1 day)
- range test BEFORE choosing the site: gateway at the high point, walk the
  bank with the spare board, log RSSI at 500 m intervals
- deploy: pole, guys, anchor, arm, drop tube, pod clip at 250/420/600 mm
- record baseline: depth, turbidity, EC, temperature, rotor RPM
- **gate:** 24 h of continuous packets and a rising-stage test by lifting
  the pod 20 cm.

## Spares that prevent a second order
| part | why |
|---|---|
| 3× Wio-E5 mini | one probe, one gateway, one spare/range-test board |
| 2× rotor blade set | blades are the mechanical fuse |
| 2× pH electrode | only on the pH channel |
| spare O-rings + desiccant | service consumables |
| one extra spool ASA | failed prints consume more than expected |
| 4 extra magnets | potted ones cannot be recovered |
