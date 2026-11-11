# Build checklist - physical inventory (RESULT 2026-11-11)

Status after walking the bench with Filip. HAVE = in hand and identified,
MISSING = not there, CHECK = present but must be confirmed by a test.

| # | part | value | ks | status | note |
|---|---|---|---|---|---|
| 1 | Schottky 1N5819 | DO-41 | 6 | HAVE (15 pcs) | |
| 2 | Fuse 0.5 A glass | TR 250 V | 1 | HAVE (7 pcs) | |
| 3 | Ceramic cap | **1 uF**, KDPU RM 5.08, Z5U 50 V | 5 | HAVE (11-12 pcs) | marking "105"; the bag's "1F" is shop shorthand for 1 uF, not farads |
| 4 | TIP125 PNP Darlington | TO-220 | 1 | HAVE (3 pcs) | first line confirmed "TIP125"; the rest is a lot code |
| 5 | TL431A | TO-92 | 1 | HAVE (5 pcs) | TechFun part; pinout 1 REF / 2 ANODE / 3 CATHODE per the Fairchild datasheet the shop links |
| 6 | Power resistor | 10 ohm / 10 W | 1 | HAVE | white cement block |
| 7 | Resistor 1 k | | 2 | HAVE (2) + stock | |
| 8 | Resistor 100 k | | 2 | HAVE (2) + stock | |
| 9 | Resistor 10 k | | 5 | HAVE (2) + stock | 3 for board A, 2 for board D |
| 10 | Resistor 1 M | | 3 | MISSING - dig in stock | 2 for balancing are REQUIRED, 1 hysteresis optional |
| 11 | JST-PH 3-pin | 20 cm | 4 | HAVE (6) | |
| 12 | BQ25570 module | | 1 | HAVE | |
| 13 | Supercapacitor | 40 F / 2.7 V | 2 | HAVE | |
| 14 | Resistor 1 M | | 2 | same as #10 | |
| 15 | Ceramic 1 uF | | 1 | HAVE | |
| 16 | Wire for caps | 24 AWG is enough at 40 mA | - | HAVE (40 m red, 0.205 mm2) | no ring terminals needed, solder to the tabs |
| 17 | XIAO ESP32S3 + Wio-SX1262 | | 2 | HAVE | |
| 18 | Schottky 1N5819 | | 1 | HAVE | from the 15 |
| 19 | Ceramic 1 uF | | 2 | HAVE | |
| 20 | Ceramic 100 nF | | 1 | MISSING - optional | use a 1 uF instead, no consequence on a 40 mA rail |
| 21 | Antenna 868 MHz | + pigtail | 2 | HAVE | inside the Seeed kits |
| 22 | USB-C cable | data | 1 | HAVE | |
| 23 | DS18B20 waterproof | 1 m | 1 | HAVE | |
| 24 | Resistor 4.7 k | | 1 | HAVE (2) | |
| 25 | TDS module | SEN0244 | 1 | HAVE | 3.3-5.5 V in, 0-2.3 V out |
| 26 | Turbidity module | **SEN0189** | 1 | HAVE | 5 V supply, 0-4.5 V analog output |
| 27 | Resistor 10 k | | 2 | HAVE + stock | output divider |
| 28 | N-MOSFET | logic-level | 1 | CHECK | somewhere in his own inventory, unused so far |
| 29 | JST-PH 3-pin | | 3 | HAVE | from the 6 |
| 30 | Boost module | MT3608 or unlabelled black DC-DC | 1 | CHECK / optional | VIN+/VIN-/OUT+/OUT- and a trimmer; type unknown. Not needed: turbidity runs from the XIAO 5V pin at 3.9 V |
| 31 | Protoboard 18 x 24 | | 4 | HAVE (more) | |
| 32 | Pin headers / sockets | 2.54 mm | 1 | HAVE | |
| 33 | Hook-up wire | solid 0.5 mm | 1 | HAVE | |
| 34 | Fuse holder 5 x 20 | | 1 | MISSING | workaround: solder the fuse inline between two wire ends, heat-shrink over it |
| 35 | MCP1700-3302E/TO | TO-92 | 1 | HAVE | spare, not used |

## Verdict

Two real gaps, both small:
1. **1 M resistors** - 2 required for the supercap bank. 1 M is
   brown-black-green. Substitutes down to 470 k are acceptable; anything
   under ~220 k leaks too much for a 5 mW harvest.
2. **Fuse holder** - not required for bench work. The generator delivers
   ~40 mA at most and cannot damage 0.2 mm2 wiring. Fit one before the
   probe sees a river.

Optional: 100 nF (use 1 uF), boost module (not needed).

## Three parts to confirm by test, not by label

1. TIP125 - read the first line of the marking. TIP125 = PNP, clamp as
   drawn. TIP122 = NPN, the clamp has to be flipped - do not wire blind.
2. TL431 pinout - 2.5 V test, see VERIFIED_PARTS.md.
3. Black DC-DC board - feed 3.7 V in, measure OUT while turning the
   trimmer. If OUT can exceed 3.7 V it is a boost, otherwise a buck.
   Either way it is not needed for this build.

## Still unknown regardless of inventory

- the module's own VBAT_OV value (measure at step 2 of WIRING.md)
- supercapacitor part number / ESR (read the can)
