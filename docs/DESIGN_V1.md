# sub-mission probe — v1 design (bank-deployed)

Status: design draft 2026-10-18, Haven. Everything here is computed or
assumed; nothing below has been built or measured unless tagged [v0].

## 0. Why — the Budča 2021 case

26 July 2021: ~500 m3 of biogas-plant digestate leaked from a Bag Tank at
Bioplyn Budca after a storm-downed branch punctured the liner, flowed down
Biensky potok into the Hron, contaminated >30 km of river, killed an
estimated 40 t of fish across 26 species (including the entire Hron
population of hlavatka podunajska). SIzP assessed environmental damage at
~400 MEUR; criminal charges followed. Detection happened the next morning
when passing fishermen reported turbid, smelly water — no monitoring
system gave any warning during the hours the plume was still moving.

Reference: SIzP / TASR case record (2021-07-26), police charge 2025-07-16,
SOP SR event log. The probe exists so the next Budca is detected at
minute 3, not hour 10.

## 1. Architecture

Bank-mounted pole, hinged swing arm, submerged pod. One-person,
10-minute deployment, any open bank.

```
 z
 |  [antenna 868 MHz]
 |  [dry box: S3+SX1262+supercap]  ~1.9 m
 |   |
 |==POLE== (driven, OD60), on bank edge
 |   \____ arm (OD28) 1.2 m, +5 deg
 |          \== drop tube
 ~~~~~~~~~~~|~~~~~~~~~~~~~~~ z=0 ~~~~~~~ flow +X ->
 |        [POD]  rotor -> cups -> [wall] -> gen -> sensor cage
 |        420 mm below surface
 +---------------------------- x
```

Rejected: buoy (antenna at waterline, sail in current, ice/debris loss),
bridge rail (needs bridge), riverbed anchor (service requires retrieval
gear).

## 2. Wet pod

| part | spec |
|---|---|
| rotor | 3 blades, D=220 mm, NACA 4412, pitch 28 deg @ 0.7R, root 22 mm |
| hub | 64 mm OD, 46 mm long |
| coupling | magnetic, 2x8 N52 Ø8x5 discs, slip limit ~0.35 N m (ORDER, measure) |
| wall | 5 mm solid pod end (sealed, no shaft penetration) |
| generator | low-cogging outrunner BLDC ~28 mm, coreless-slot preferred |
| rectifier | 3-phase, 6x 1N5819 |
| storage | 0.47 F supercap 5.5 V -> 3.76 J usable [computed] |
| buck | TPS62A02 / BQ25570 option |
| cage | flow-through, 12 slots, +MS5837 (level/temp), pH, EC/TDS, turbidity, NTC |

No dynamic shaft seal anywhere. Pods swapped whole at the bank.

## 3. Measured quantities

pH (two-point, temp-comp via DS18B20; drift +-0.3/30d unserviced), EC,
turbidity (flow-through w/ manual wiper), water temp, depth (MS5837-30BA),
flow from rotor RPM (free, generator IS the tachometer).

## 4. Radio

v1: 868 MHz LoRa g1, 14 dBm, SF12, 1 % duty guaranteed in firmware.
Link budget 152 dB; radio horizon 2.5 m box / 10 m gateway = 19.5 km;
effective ~11-13 km with vegetation margin. Own gateway on ridge/roof.
NB-IoT B20 as fallback variant; decision deferred until site chosen.

## 5. Energy (computed; cogging torque is the open unknown)

| v (m/s) | P elec | daily net |
|---|---|---|
| 0.2 | 17.9 mW | +1.5 kJ |
| 0.5 | 422 mW | +36 kJ |
| 1.0 | 3.5 W | +305 kJ |

Cut-in at 0.123 m/s IF cogging torque = 2 mN m [ASSUMED].
Load applied in bursts after cap crosses threshold. Full detail in
`sim/simulate.py`.

## 6. Waterproofing

Electronics box: ready-made IP68, glands potted in epoxy, BME280 inside
as humidity leak-sensor (permanent). Pod: printed PETG/ASA, walls >= 3 mm,
but treat print as splash-only; sealing relies on the solid 5 mm coupling
wall + potting. Acceptance: 0.5 bar vacuum, 24 h submerged, internal
humidity flat.

## 7. Build-before-order list (the honesty ledger)

1. Measure cogging torque of candidate generator (weight on arm / back-EMF) [gating #1]
2. Measure magnetic coupling slip torque (spring balance jig)
3. XFOIL polar NACA 4412 at Re 6e4 -> confirm Cp~0.35 at TSR 5.5
4. Flow-speed survey at candidate sites
5. 24 h vacuum-submerge test of printed pod
6. Field range test of radio at actual site

## 8. AMAVET honesty

Generator has never powered the board [v0]. No river test ever [v0].
This document describes v1 design; only the sim numbers exist, and every
one is labelled [computed]/[assumed].
