# Verified parts sheet - what the datasheets actually say

Date 2026-11-11. Rule from here on: no part is called "OK" until its
datasheet has been read and the claim has a source in this table. Anything
not in here is MEASURE, not fact.

Source PDFs were downloaded and parsed, not quoted from memory:
- TI BQ25570, SLUSBH2G Rev G (2019)
- Microchip MCP1700, DS20001826F
- TI TL431/TL432, SLVS543S Rev (2024)
- onsemi 1N5817/18/19, AND onsemi TIP120/121/122/125/126/127
- Aerosemi MT3608
- DFRobot SEN0189 and SEN0244 product docs
- Seeed XIAO ESP32S3 wiki

## 1. VERIFIED

### 1N5819 (onsemi)
| claim | value | source |
|---|---|---|
| reverse voltage | 40 V (VRRM) | ratings table |
| forward current | 1.0 A average | ratings table |
| forward drop | 0.34 V max at 0.1 A | elec. characteristics |

Consequence: 6 in a 3-phase bridge, 2x 0.34 V = 0.68 V worst case out of the
bus. At 2.7 V bus that is 25 %, which is why the generator's own numbers
matter more than the diode choice.

### TIP125 (onsemi, TO-220AB CASE 221A STYLE 1)
| claim | value |
|---|---|
| pinout | **1 = Base, 2 = Collector, 3 = Emitter, tab = Collector** |
| VCEO | 60 V |
| IC continuous | 5.0 A |
| IB max | 120 mA |
| hFE | 1000 min at IC = 0.5 A, VCE = 3 V |
| VCE(sat) | 2.0 V max at IC = 3 A (lower at our 0.3 A) |
| power | 65 W (case-limited) |

Consequence for the clamp: at 0.34 A the base current needed is ~0.34 mA,
the TL431 sees ~4 mA through the 1k pull-up (above its 1 mA minimum), and
the transistor dissipates ~0.3-0.7 W. No heatsink.

### TL431 (the part actually supplied by TechFun)
TechFun links the Fairchild TL431/TL431A datasheet on the product page
(https://techfun.sk/produkt/tl431a-36v-programovatelna-napatova-referencia/
-> cdn.sparkfun.com/assets/learn_tutorials/4/2/3/TL431.pdf).

| claim | value | source |
|---|---|---|
| **TO-92 pinout** | **1 = REF, 2 = ANODE, 3 = CATHODE** (flat face to you, legs down, left to right) | Fairchild datasheet, page 1, package outline |
| reference voltage | 2.5 V nominal; TL431A = 1 % | same |
| sink current | 1.0 to 100 mA | features list |
| output range | up to 36 V | same |

TI's own datasheet (SLVS543S) gives its **LP** package as CATHODE 1,
ANODE 2, REF 3 - the outer two pins swapped. Same part name, opposite
order. The middle pin is the anode in both.

Consequence: wire the clamp with REF on pin 1 and CATHODE on pin 3, then
confirm in circuit. Do not "verify" it by swapping pins on a live bus with
the module attached.

### MCP1700-3302E/TO (Microchip)
| claim | value |
|---|---|
| TO-92 pinout | **1 = GND, 2 = VIN, 3 = VOUT** (Table 3-1) |
| output | 3.3 V, 250 mA |
| quiescent | 1.6 uA typ |
| output capacitor | **1 uF ceramic required for stability** |
| TO-92 thermal resistance | 92 C/W junction-to-air |

Note the pinout is NOT what a SOT-23 part would suggest (SOT-23 is
1 = GND, 2 = VOUT, 3 = VIN). Same chip, different order.

### XIAO ESP32S3 (Seeed)
| claim | value | source |
|---|---|---|
| 3V3 pin | **regulated OUTPUT** of the onboard regulator, up to 700 mA | wiki pin map |
| 5V pin | input or output of USB VBUS; may be fed externally **through a series Schottky, anode to source** | wiki power pins |

Consequence - this corrects the earlier wiring: **do not feed 3.3 V into the
3V3 pin.** Feed the 5V pin from the storage through a 1N5819 and let the
onboard regulator make 3.3 V. The MCP1700 is then not needed for the MCU.
Its 3V3 output can feed the sensors.

### MT3608 (Aerosemi)
| claim | value |
|---|---|
| input | 2.0 - 24 V |
| output | up to 28 V, set by the trimmer |
| EN pin | high = on, tie to VIN if unused |
| switch current limit | 4 A, 1.2 MHz |

Consequence: 4.2 V in -> 5 V out is inside spec. Its EN pin means it can be
turned off, which matters if it ever feeds a sensor.

### SEN0189 turbidity (DFRobot)
5 V DC supply, analog output 0-4.5 V, output falls as turbidity rises.

### SEN0244 TDS (DFRobot)
Input 3.3-5.5 V, output 0-2.3 V, range 0-1000 ppm, AC excitation.

## 2. MEASURE - not verified, must be checked on the bench

| item | unknown | how to check |
|---|---|---|
| BQ25570 module | its VBAT_OV setting (the module's own divider) | 3.3 V through 100 ohm into IN+, watch BAT stop. Write the number down. |
| BQ25570 module | whether EN is pulled up on the module | same test: if BAT does not climb, tie EN to GND |
| Supercapacitors | actual part, ESR, size, surge rating | read the marking on the can, report it |
| Turbidity sensor | which model (0189 or 0169) | read the label; both are 5 V, 0-4.5 V analog |
| GB2208 | R line-to-line, cogging torque | DMM between two pins, weight on arm |
| Generator | E_ll per rpm | drill at known rpm, DMM on AC |

## 3. Where the design changed because of this sheet

1. XIAO is fed on the **5V pin through a diode**, not on 3V3. The MCP1700
   moves off the MCU rail and becomes optional (sensors, or spare).
2. TIP125 pin order is fixed: base on pin 1, collector on 2 (and the tab),
   emitter on 3. The clamp diagram in WIRING.md follows that.
3. TL431 must be identified, not assumed.
4. MCP1700 pinout is GND-VIN-VOUT in TO-92, which is the reverse of what
   its SOT-23 sibling does.
