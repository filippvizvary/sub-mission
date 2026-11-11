# Wiring - Sunday build, everything from the parts on the table

Status 2026-11-11, Haven. Perfboard only, no JLCPCB, no new orders.
Replaces the "missing parts" list: the BQ25570 is a MODULE, its inductors,
caps and dividers are on the module board. Nothing to add.

## 0. What the module pins are

| silkscreen | is | connect to |
|---|---|---|
| IN+ / IN- | charger input (VIN_DC) | board A bus+ / bus- |
| BAT+ / BAT- | storage node (VSTOR) | supercap bank |
| OUT+ / OUT- | regulated buck output | not used in v1 |
| GND | common | star ground |
| EN | charger enable (active LOW on the chip) | GND to enable |
| V_EN | buck enable | leave open in v1 |
| V_OK | VBAT_OK, digital high when storage is good | optional, see C |

Module limits that still apply (they are the chip's):
- IN+ must never exceed 5.1 V. Clamp at 4.4 V on board A.
- Storage must never exceed the supercap rating: 2 x 2.7 V = 5.4 V.
- OUT is a 110 mA-at-1.8 V buck, i.e. ~60 mA at 3.3 V. Do not run the
  ESP32 from OUT. Run it from BAT through the MCP1700.

## 1. Board A - generator in, rectifier, clamp

### 1.1 Three-phase bridge, 6 x 1N5819
Motor pins A, B, C (all three are phases; the "middle" one is phase B).

| diode | anode | cathode |
|---|---|---|
| D1 | A | BUS+ |
| D2 | B | BUS+ |
| D3 | C | BUS+ |
| D4 | BUS- | A |
| D5 | BUS- | B |
| D6 | BUS- | C |

The band on the diode body is the cathode. D4-D6 are turned "backwards"
on purpose - that is what makes it a bridge.

### 1.2 Bus
- 0.5 A fuse in series with BUS+ going to board B.
- CIN: five 1 uF ceramics in parallel between BUS+ and BUS- (place them
  at the exit of the board, next to the cable to B). 5 uF total is fine.
- Two test points: BUS+ and BUS-.

### 1.3 Clamp (dump / brake)
Parts: 1x TIP125 (PNP Darlington, TO-220), 1x TL431, 1x 10 ohm / 10 W,
resistors 1k, 100k, 130k, 1M.

**Pin facts, from the datasheets, not from memory:**
- TIP125, TO-220AB case 221A style 1: **pin 1 = Base, pin 2 = Collector,
  pin 3 = Emitter, tab = Collector.** VCEO 60 V, IC 5 A, hFE >= 1000 at
  0.5 A, VCE(sat) 2.0 V max at 3 A.
- TL431 in TO-92 **as supplied by TechFun** (Fairchild datasheet that the
  shop links, TL431/TL431A, page 1):
  **1 = REF, 2 = ANODE, 3 = CATHODE** - flat face toward you, legs down,
  reading left to right.
  Note this is the OPPOSITE of TI's own LP package (CATHODE 1, ANODE 2,
  REF 3). The middle pin is the anode in both; the two outer pins swap.
  Vref 2.495 V, cathode needs **1 mA minimum** to regulate.
  Wire it as below, then confirm in circuit (section 1.4): correct shows a
  bus clamped at 4.4 V, a bus that will not pass 0.7 V means the outer two
  pins are swapped, a bus that runs past 5 V means REF and cathode are
  swapped. Never do that test with the module or the supercaps connected.

```
BUS+ ---+--- E  TIP125 (pin 3)      +--- 10 ohm/10W --- BUS-
        |       C (pin 2) ----------+
        |       |
        |     1k
        |       |
        |     B (pin 1) --- TL431 CATHODE (pin 3)
        |
BUS+ ---+--- 100k ---+--- TL431 REF (pin 1)
                     |
                    130k
                     |
BUS- --------------- +--- TL431 ANODE (pin 2) --- BUS-
                          (and 1M from REF to cathode, optional hysteresis)
```

- Set point: TL431 conducts when REF reaches 2.5 V, i.e. at
  BUS = 2.5 * (100k + 130k) / 130k = 4.42 V.
- Behaviour: bus rises to 4.42 V, TL431 pulls the base down, PNP opens,
  the 10 ohm resistor dumps. At 3.4 V across it that is 0.34 A, 1.16 W in
  the resistor (10 W part, fine) and ~0.35 W in the transistor. No heatsink
  needed because the PNP is fully on, not used as a linear pass element.
- The 1M from REF to cathode is optional; without it the clamp chatters
  around the threshold, which is harmless but noisy.

### 1.4 Board A test
Motor by hand or a drill: AC on all three pairs (equal magnitude), then DC
on BUS. Then spin hard with **nothing downstream connected** and read BUS:

| BUS reads | meaning | action |
|---|---|---|
| stops at ~4.4 V | clamp correct | proceed |
| never passes ~0.7 V | TL431 outer pins swapped | swap pins 1 and 3 |
| climbs past 5 V | TL431 REF and cathode swapped, it is not conducting | swap pins 1 and 3 |

Never run this test with the module or the supercaps attached.

## 2. Board B - storage (module + supercaps)

- Module IN+ <- BUS+ from A (after the fuse), IN- <- BUS-.
- Module EN -> module GND (if the module already pulls EN up, leave it;
  test at 5.1, whichever makes BAT rise).
- Supercaps in series, watch polarity:
  BAT+ -> C1 (+), C1 (-) -> C2 (+), C2 (-) -> BAT- (GND).
- 1 M across C1, 1 M across C2 (balancing).
- One 1 uF across the whole bank (HF only, optional).
- OUT+/OUT-, V_EN: leave open.

The module needs no board. Mount it on standoffs next to the caps, or on
the spare protoboard if that is easier mechanically. The supercaps are
16-18 mm cans - cable them, do not try to seat them on the perfboard.

### 2.1 Measure the module before trusting it
Feed IN+ from a 3.3 V source through 100 ohm (the XIAO's 3V3 pin is fine,
that is ~30 mW and stays far under the 510 mW input limit). Watch BAT.
- BAT must climb.
- Note the voltage where it stops: that is the module's VBAT_OV.
  5.0 V or lower: good. 4.2 V: works, 54 J usable instead of 128 J,
  reserve drops from 4.5 days to 2 days. Above 5.4 V: do not connect
  the supercaps, the module's divider has to be changed.

This test proves the module works before the generator ever spins.

## 3. Board C - MCU power

Power path (corrected after checking the Seeed pin map):
`BAT+` -> 1N5819 (anode to BAT) -> XIAO pin "5V". The onboard regulator
makes 3.3 V. Do NOT feed 3.3 V into the "3V3" pin - on this board that pin
is a regulated OUTPUT, not an input.

- 1N5819 drops 0.3-0.34 V, so the XIAO sees 3.9 V from a 4.2 V store.
- 1 uF + 100 nF on the XIAO 5V pin.
- Sensors take 3.3 V from the XIAO "3V3" pin (good for 700 mA per Seeed).
- The MT3608's 5 V rail, if used for the turbidity sensor, comes off the
  XIAO 5V pin too (3.9 V) - the sensor is specced at 5 V, see section 4.
- Do not have USB plugged in while the probe powers itself; the diode
  protects the source, not the other way round.
- Antenna to the SX1262 module, keep it away from the module and the caps.

MCP1700 (TO-92, verified: **1 = GND, 2 = VIN, 3 = VOUT**): no longer needed
in the MCU rail. Keep it as a spare or use it to give the analog sensors a
clean 3.3 V of their own if the ESP32 ADC turns out noisy on the XIAO rail.
It needs 1 uF ceramic on the output to be stable.

V_OK (module) -> optional: a 4.7k + LED to 3V3, or a XIAO GPIO as a
"storage good" flag. Not needed for the first run.

## 4. Board D - sensors

All three share 3V3 from board C and the same ground. No isolation needed:
the whole probe is one floating system, nothing is earth-referenced.

| sensor | VCC | signal |
|---|---|---|
| DS18B20 (waterproof) | 3V3 | DQ -> GPIO, 4.7k pull-up to 3V3 |
| TDS SEN0244 | 3V3 | AOUT -> GPIO direct (0-2.3 V) |
| Turbidity SEN0189/0169 | BAT (4.2 V) | AOUT -> 10k/10k divider -> GPIO |

- Turbidity at 4.2 V instead of 5 V: the LED is dimmer, the curve shifts.
  Calibrate on site against clear water and a muddy sample; do not trust
  the datasheet curve at 5 V. If the response is too weak, put the MT3608
  in front of it (3.5-5 V in, 5 V out) - that is the only job it has.
- The 10k/10k divider halves the output so it cannot exceed the ADC range.
  Use 10k and not 100k: the ESP32 ADC wants a source under ~10k.
- Turbidity draws 20-30 mA while lit. Switch it: N-MOSFET on its GND, gate
  from a GPIO, high = measuring. Otherwise it eats the harvest 24/7.
- ESP32-S3 ADC is nonlinear. Two-point calibration per channel, store the
  coefficients in firmware.

## 5. Inter-board wiring

Four wires: BUS+ , BUS- , BAT+ (to the LDO), GND. Plus the sensor cables.
Use the JST-PH connectors or solder directly; a 500 mA circuit does not
care. Keep the BUS pair twisted.

## 6. Build and test order (do not skip a step)

1. MCP1700 alone: feed 4 V, measure 3.3 V on the output. 1 minute.
2. Module alone: 3.3 V through 100 ohm into IN+, watch BAT climb and stop.
   Write the stop voltage down.
3. Board A alone: motor, AC on three pairs, DC on BUS, clamp at 4.4 V.
4. A + B: spin the motor, watch BAT climb. This is the whole project in
   one measurement.
5. C: connect 3V3, does the XIAO boot and join the LoRa link.
6. D: sensors one at a time, calibrate.

If step 4 does not climb, the fault is almost always one of: a diode
reversed in the bridge, IN+ and BAT+ swapped, or the fuse not fitted.
Check those three before suspecting the module.
