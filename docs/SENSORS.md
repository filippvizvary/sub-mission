# Sensor selection — decision record (2026-10-19)

## What we measure, and why

Tied to the Budca 2021 failure mode: digestate entered the river as an
organic load, consumed oxygen, and the fish suffocated. So the instrument
must measure, in order of diagnostic value:

| # | channel | why it matters | detects plume in |
|---|---|---|---|
| 1 | dissolved oxygen (DO) | the actual harm mechanism; fish die of hypoxia | seconds-minutes |
| 2 | turbidity | optical signature of digestate; cheapest early alarm | minutes |
| 3 | electrical conductivity (EC) | digestate is highly ionic; large step change | minutes |
| 4 | water temperature | context + mandatory compensation for EC and DO | continuous |
| 5 | water level / stage | hydrology, flood warning, dilution context | continuous |
| 6 | flow velocity | from rotor RPM — free, no sensor | — |

pH stays as an OPTIONAL per-site module: it is the fragile, drifting
channel (14-30 day service) and adds nothing to spill detection.

## Chosen sensors (prices checked 2026-10-19)

| channel | part | source | price | accuracy | service interval |
|---|---|---|---|---|---|
| DO | DFRobot SEN0237-A Gravity analog DO kit | global-ic.sk 666 pcs / botland.cz | 80 USD / 4381 Kc (~175 EUR) | 0-20 mg/L, 98% in 90 s | **membrane cap 1-2 months in muddy water**, filling solution monthly, electrode life 1 yr |
| Turbidity | DFRobot SEN0189 | techfun.sk, 6 in stock | 12.45 EUR | relative NTU, site-calibrated | wipe at service |
| EC / TDS | DFRobot SEN0244 Gravity | TME / botland.cz | ~14 EUR / 328 Kc | **+-10% FS** (0-1000 ppm) | none, AC excitation resists polarisation |
| Temp | DS18B20 waterproof 1 m | techfun.sk | ~5 EUR | +-0.5 C (+-0.1 after cal) | none |
| Level | submersible level probe, 0-1 mH2O, IP68, 316L, 0.5-4.5 V out | TME / sensorsone quote | 60-440 EUR depending on brand | 0.5% FS = 5 mm on 1 m range | permanent immersion rated |
| Flow | rotor RPM (AS5048A on XTG3506, or hall on dry side) | — | 0 | +-5% after volume cal | none |
| pH (optional) | PH-4502C + E201 | laskakit.cz 338 + 298 Kc | ~26 EUR | +-0.5 pH module spec, +-0.1 after 2-pt | 14-30 days |

## Three decisions that changed today

**1. DO is added. It is the highest-value channel.**
The 2021 event killed fish by oxygen depletion. Turbidity and EC tell you
something entered; DO tells you it is killing. A network that alarms on
DO drop is the one that would have mattered.
Cost is the problem: ~175 EUR, and it is the most maintenance-hungry
channel — membrane in muddy water lasts 1-2 months, filling solution
monthly. It fits a 30-day service cycle, NOT the 90-day core.
Procurement trap: the 0.5 mol/L NaOH filling solution cannot be shipped
by air and is NOT in the kit. Buy it locally (chemical shop) or mix it.

**2. MS5837-30BA is DISQUALIFIED as our depth sensor.**
Datasheet and Blue Robotics both state the gel-covered element must be
dried typically once a day; max continuous submersion 24 h, and prolonged
submersion causes drift and permanent damage. We planned 90 days
submerged. That is a spec violation, not a risk — it would have failed in
the field and looked like "sensor drift".
Replacement: an industrial submersible level probe (IP68, 316L,
permanent-immersion rated, 0-1 mH2O range, voltage output so it runs from
our 5 V rail, not 12-30 V). Blue Robotics BarXT is the right class but
$380 — too expensive. Generic 316L probes are 60-120 EUR and need one
quality check on arrival.
Note the physics is unchanged: pod sits at fixed z, so pressure in the pod
reads stage relative to the surface. We just need a sensor that tolerates
being wet for three months.

**3. TDS +-10% FS is honest but weak.**
Fine for detecting a step change (which is all spill detection needs),
not fine for reporting an absolute value. State it as a trend indicator.
If absolute EC matters later, the upgrade is a proper 4-electrode
conductivity cell, not a different hobby module.

## Consequence for the service model

| tier | channels | interval |
|---|---|---|
| T1 (core, 90 days) | temp, level, flow | 90 d |
| T2 (90 days, needs wiper) | turbidity, EC | 90 d |
| T3 (30 days) | DO | 30 d |
| T4 (14-30 days, optional) | pH | 14-30 d |

So the "90-day probe" is real only for T1+T2. With DO fitted the honest
service interval for that unit is 30 days. This must be on the poster —
claiming 90 days for a probe carrying a DO membrane would be false.

## Still to verify before ordering

1. Pick and quote the specific submersible level probe (SK/CZ supplier,
   0-1 mH2O, 316L, voltage output, 5 m cable).
2. Confirm SEN0237-A stock and that the filling solution can be sourced
   locally in SK.
3. Bench-test SEN0244 linearity in river-range water (0-500 ppm) since
   +-10% FS is the weakest number in the set.
4. Confirm DS18B20 cable jacket survives 90 days submerged (it is rated
   for short immersion only — swap to a potted probe if not).
