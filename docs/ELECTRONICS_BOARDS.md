# Electronics chain - board split and part review

Status: draft 2026-11-11, Haven. Board split + numbers for the 4 protoboards
(18 x 24 holes, 2.54 mm pitch = 45.7 x 61.0 mm usable). Nothing built yet.

Supersedes the converter choices in DESIGN.md section 2 for this build:
BQ25570 (not LTC3105), 2 x 40 F / 2.7 V supercap (not the 500 F LIC).

## 1. The motor has THREE phases, not plus/minus/middle

T-Motor GB2208 KV128, 14 pole (7 pole pairs). A gimbal BLDC is 3-phase and
the three pins are phase A, B, C. The connector is a servo-style 3-pin header,
which is why it looks like signal/+/-, but on this motor all three wires go to
the same symmetric winding.

- There is no neutral and no star point brought out. The "middle pin" is the
  third phase and it carries current in normal operation.
- Measured AC between any two pins = line-to-line EMF. All three pairs read
  the same magnitude, just phase-shifted 120 deg.
- Resistance between any two pins = 2 x R_phase (two phases in series).
  Measure it: GB2208 class is ~14 ohm per phase / ~29 ohm line-to-line.
- Rectify with a 3-phase bridge (6 diodes), not 2 phases. Using only two
  leaves one third of the copper disconnected, raises the effective
  resistance and roughly halves the harvest.

## 2. Numbers at the rotor the pod actually drives

KV = 128 rpm/V. Rotor 434 rpm at 1.0 m/s (D220, TSR 5).
**R_ll measured on the real motor: 14 ohm** (all three pairs), so R_phase = 7 ohm.
Numbers below are ngspice transient results (see docs/board_A.pdf page 3), not
hand arithmetic.

| v (m/s) | rpm | P at MPP | bus at MPP | I at MPP |
|---|---|---|---|---|
| 0.30 | 130 | 2.9 mW | 0.24 V | 12 mA |
| 0.50 | 217 | 18.4 mW | 0.51 V | 36 mA |
| 0.75 | 326 | 58.7 mW | 0.91 V | 65 mA |
| 1.00 | 434 | 122.6 mW | 1.31 V | 94 mA |
| 1.50 | 651 | 323.1 mW | 2.13 V | 152 mA |

The earlier table in this document (49.6 mW at 1 m/s) came from an assumed
29 ohm line-to-line and hand arithmetic; the measured 14 ohm doubles it.
sim/simulate.py still carries R_PHASE_2W = 0.5 ohm and is wrong by ~28x.

The chain still closes: the node needs ~28 J/day = 0.32 mW average, and
0.3 m/s already gives 4.5 mW (14x).

Overvoltage: open-circuit bus crosses 4.3 V at v = 1.33 m/s and 5.1 V (VIN_DC
max) at 1.58 m/s. Free-spinning at TSR 7 in 1.5 m/s gives E_ll = 7.1 V. The
clamp is a required part, not an option.

## 3. BQ25570 hard limits (datasheet SLUSBH2G, Rev G)

| parameter | value | consequence here |
|---|---|---|
| VIN_DC range | 100 mV - 5.1 V (abs 5.5) | clamp the rectified bus at <= 4.5 V |
| cold start | VIN >= 600 mV | first-ever charge needs ~0.3 m/s, later 100 mV is enough |
| VSTOR(CHGEN) | 1.73 V | main boost takes over above that |
| input power | 5 uW - 510 mW | fine, we make <= 112 mW |
| IOUT (buck) | 110 mA at VOUT = 1.8 V (~200 mW) | **at VOUT 3.3 V that is only ~60 mA** |
| VOUT | divider, Rsum <= 13 M | 3.3 V rail |
| VBAT_OV | must be > VIN_DC | VBAT_OV 5.0 V, clamp 4.3-4.5 V |
| MPPT | VOC_SAMP to VSTOR = 80 %, to GND = 50 % | **use 50 % (GND)** - max power transfer, not solar's 80 % |

Consequence for loads: do not feed the ESP32S3 + SX1262 from VOUT. 110 mA is
spec'd at 1.8 V; at 3.3 V the buck is good for ~60 mA and a LoRa TX burst plus
MCU is ~120 mA. Feed the MCU from VSTOR through the MCP1700 and use VOUT only
for the always-on housekeeping rail (DS18B20, ADC dividers, VBAT sense).

Required externals that are NOT in the parts list:
- L1 = 22 uH, ISAT >= 300 mA, low DCR (LPS4018-223)
- L2 = 10 uH, ISAT >= 200 mA (LPS4018-103)
- CIN 4.7 uF + CBYP 0.01 uF, CREF 10 nF low leakage, CSTOR 4.7 uF, COUT 22 uF
- VBAT_OV / VBAT_OK / OK_HYST / VOUT_SET dividers at 1 % (the 100k/1M/10k/4.7k
  set cannot hit all four thresholds - buy the values from a divider calc,
  total 11-15 M per divider)

Package: BQ25570RGR = VQFN-20, 3.5 x 3.5 mm, 0.5 mm pitch. Not hand-solderable
with an iron. Either hot air + paste + stencil, or a breakout module, or a
5 EUR JLCPCB 2-layer board for this block alone.

## 4. Storage

2 x 40 F / 2.7 V in series = 20 F / 5.4 V max, one 1 M across each cell for
balancing (5 uA, ~0.12 mAh/day, affordable).

Usable window with VBAT_OV 5.0 V and VBAT_OK 3.5 V: 0.5*20*(5.0^2 - 3.5^2)
= 128 J = 4.5 days at 28 J/day. Charge from empty: 7.9 h at 0.3 m/s,
2.9 h at 0.5 m/s, 0.7 h at 1.0 m/s.

Physical: 40 F / 2.7 V cells are can types, roughly 16-18 mm dia x 25-40 mm.
They do not fit on a 45.7 x 61 mm board next to anything else - mount them
mechanically and wire them, with the balancing resistors on the board.

## 5. Clamp (TL431 + TIP125 + 10 ohm)

Linear shunt = the TIP125 sits mid-range and burns the difference. At 4.3 V
across a 10 ohm dump that is 0.43 A: 1.85 W in the resistor (10 W part,
derate to 5 W in free air) and up to 0.43 W in the transistor if it is held in
saturation, but 1-2 W if it is used as a linear pass element - SOT-93/TO-220
without a heatsink is ~62 C/W, so 2 W is +124 C. Build it as a hysteretic
switch, not a linear regulator: TL431 with positive feedback (or a small
comparator) drives the PNP hard on or fully off. Set point 4.3-4.5 V.

The dump resistor is ~40 mm long wirewound - off-board.

## 6. Board split (4 x 18 x 24)

| board | function | contents | why separate |
|---|---|---|---|
| A | GEN IN | 3-phase bridge 6x 1N5819, CIN, 0.5 A fuse, TVS, TL431+TIP125 clamp | sees the highest dv/dt and the dump-resistor heat; sacrificial |
| B | HARVEST | BQ25570 + L1/L2 + dividers + CSTOR, supercap terminals, 1 M balancing | 488 nA quiescent and nA-level dividers: any leakage next to switching noise ruins the thresholds |
| C | MCU + RADIO | XIAO ESP32S3 + Wio-SX1262, MCP1700, VBAT_OK load switch, USB-C | antenna needs a quiet ground; keep away from switching nodes |
| D | SENSOR FRONT END | DS18B20 (4k7 pullup), turbidity (5 V + divider), TDS, MT3608 5 V, load switches | analog; the 5 V boost and the two water electrodes must be switchable |

Rules for the split:
- 4 is the maximum. Every board-to-board wire is a failure point in a box that
  gets potted; do not split the MCU and its radio, or the bridge and its fuse.
- A and D are perfboard-friendly. B is not: QFN-20 plus two switching loops on
  2.54 mm pitch perfboard is where efficiency and stability go. Make B a real
  PCB (or buy the module) and use the 4 protoboards for A, C, D + spare.
- If the boards are stripboard, cut the strips under the bridge and under the
  clamp; do not rely on the copper pattern.

## 7. Sensor board detail

- Turbidity SEN0189/SEN0169 needs 5 V and outputs 0-4.5 V: run it from the
  MT3608 (3.5-5.0 V in, 5 V out, min input 2 V, so fine from VSTOR) and divide
  the output by 2 into the ADC.
- TDS SEN0244 is 3.3-5.5 V in, 0-2.3 V out: direct to ADC at 3.3 V. Its +-10 %
  FS is a trend, not a measurement.
- Both are invasive electrodes in the same water. Power them sequentially
  through load switches so two cells never drive the same volume at once.
- ESP32-S3 ADC is nonlinear; calibrate the two points you care about.

## 8. Missing from the parts list

- 2N7002 / AO3401 class small FETs for load switching (BQ25570 VBAT_OK cannot
  drive a load directly, and MCP1700 has no EN pin)
- 22 uH and 10 uH inductors, 4.7/22 uF ceramics, 10 nF CREF
- 1 % divider resistors in the actual values (not the E12 assortment)
- TVS or zener on the rectified bus (belt to the TL431 braces)
- Ferrite bead + 100 nF at the XIAO 3V3 pin

## 9. Measure before the boards are etched

1. R_ll between any two motor pins (expect ~29 ohm for a 2208 class).
2. E_ll at a known rpm (drill, or count revolutions): E_ll = rpm/128.
3. Cogging torque, weight on arm (gates cut-in).
4. Clamp behaviour: spin the motor with no load and watch the bus - it must
   never exceed 5.0 V.
