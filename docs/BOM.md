# sub-mission probe — complete BOM v1 (Slovakia-sourced, 90-day target)

> **Single source of truth: `PARTS_LIST.csv` / `PARTS_LIST.md`** (80 lines, 62 verified
> live listings, 7 pending quotes, 10 printed in-house). The sections below are the
> original narrative version; where they disagree with PARTS_LIST, PARTS_LIST wins.
>
> **Real totals after the full list was priced (correcting an earlier optimistic claim):**
> - first probe, everything bought new: **~920 EUR**
> - marginal probe (tooling + filament spools excluded): **~720 EUR**
> - site hardware per deployment: **~105 EUR**
> - gateway: **~300 EUR**
> - 20 probes + 2 gateways: **~17 100 EUR** one-off, ~0 recurring

Honesty gate: every item is either in a Slovak/CZ shop's catalogue TODAY
(link + price) or has a printed/machined substitute named. Prices are
list + VAT where shown; check stock before ordering. This is v1 design,
nothing is bought yet.

Critical caveat on accuracy — stated, not hidden:
- Temperature, depth, turbidity, conductivity and flow: 90-day service
  interval is realistic with this BOM. Details per-channel below.
- pH on a hobby glass electrode is NOT honest at 90 days unattended
  (drift +-0.3 pH per 30 days unserviced is what v0 proved). pH is
  therefore specced as a SERVICEABLE MODULE (14-30 day swap) and the
  core probe does not depend on it. If you want 90-day pH, the answer is
  a commercial multi-parameter sonde (~EUR 3-8k), not TechFun parts.

---

## 1. WET SIDE (submerged module)

### 1.1 Hydrodynamic rotor + drive (printed + machined)
| # | item | spec | source | EUR |
|---|------|------|--------|-----|
| 1 | Rotor 3-blade NACA4412, D220, twist 28deg->2deg | Printed ASA, 6 wall, 50% gyroid, post-coated West 105/206 epoxy | print own | (filament below) |
| 2 | Wet shaft | 316L ground h6, Ø5 x 115mm, 2 flats ground each end | tme.eu 1263K12-equiv / metal shop | 6 |
| 3 | Wet bushings x2 | PEEK machined Ø8 OD x Ø5.05 ID x 12L, flanged Ø12 x 2 | local machinist or prusa printed CF-PETG with wear caveat | 12 |
| 4 | Bearing carrier tube | 316SS seamless Ø12 x Ø8 x 55 | metal shop cut | 4 |
| 5 | Hub | Printed ASA Ø64 x 46, brass M4 heat-set inserts x2 | print own + inserts | 2 |
| 6 | Retention | M4 x 8 316SS cup-point set screw x2 | tme.eu ISO 4029 | 1 |

### 1.2 Magnetic coupling (no shaft seal — key reliability call)
| # | item | spec | source | EUR |
|---|------|------|--------|-----|
| 7 | Magnets x16 | N52 Ø8 x 5, hermetically canned 316L (not bare!) | magnet-shop or kjmagn.com canning service; bare N52 in river corrodes in weeks | 18 |
| 8 | Cup x2 | Printed ASA Ø48 rim, potted magnets | print + epoxy | 1 |
| 9 | Separation wall | Printed PC-blend or machined POM-C Ø106 x 5mm, integral with pod nose | print + post-cure | 2 |
| 10 | Potting (magnets) | 3M Scotch-Weld DP270 black, 5x 25ml | techfun.sk | 14 |
| 11 | Slip-torque jig consumables | spring balance 0-5 N, Ø15mm drum | home | 5 |

### 1.3 Sealed generator pod
| # | item | spec | source | EUR |
|---|------|------|--------|-----|
| 12 | Pod barrel | Printed ASA Ø110 x 120, wall 2.4mm 6-perimeter + epoxy coat | print own | (filament) |
| 13 | Tail cone | Printed, integrated | print own | - |
| 14 | Generator | gimbal BLDC 300 rpm/V class (e.g. iFlight GM3506 / T-Motor GB2208, rewound if needed) | unmannedtech / tme | 28 |
| 15 | Pod O-ring | NBR 70, Ø100 x 2.5, greased Molykote 111 | laskakit/tme | 3 |
| 16 | Pod clamp screws | M4 x 30 A4 x6 + washers | tme | 3 |
| 17 | Desiccant | 5g silica + indicator, replaceable | anywhere | 2 |
| 18 | Cable gland (wet side) | Lapp Skintop MS-M 12x1.5 + 3M Scotchcast 2131 potted | tme | 12 |

### 1.4 Flow-through sensor cage + sensors
| # | item | spec | source | EUR |
|---|------|------|--------|-----|
| 19 | Cage | Printed ASA Ø130 x 150, 12 slots | print own | (filament) |
| 20 | Weed guard ring + struts | Printed ASA Ø250 ring, 3 struts | print own | (filament) |
| 21 | Water temperature | DS18B20 waterproof probe 1m cable | techfun.sk sku LA112050 | 6 |
| 22 | Depth (absolute) | MS5837-30BA on Blue Robotics-type carrier; TE part MS583730BA01-50 | components-store.cz 5941 pcs stock | 9 |
| 23 | Electrical conductivity (EC) | DFRobot Gravity SEN0244 TDS module + probe | tme.eu / components-store | 14 |
| 24 | Turbidity | DFRobot SEN0169 (proper analog turbidity, not the cheap LA131102) | techfun.sk 6 in stock 12.45 | 13 |
| 25 | pH kit — SERVICEABLE, optional | DFRobot Gravity pH v2 SEN0161-V2 + electrode | techfun.sk | 39 |
| 26 | pH electrode spare x2 | E201-C BNC | techfun.sk | 18 |
| 27 | pH buffer pH7+pH10 | 2x250 ml | techfun.sk | 12 |
| 28 | Sensor cable | 4x 2x0.5mm² shielded PUR, 4m runs | laskakit / tme | 20 |
| 29 | Cage fasteners M3 A4 x12 + nylock | tme | 6 |

## 2. WET-DRY INTERFACE (the one cable)

| # | item | spec | source | EUR |
|---|------|------|--------|-----|
| 30 | Submersible multi cable | 8x 0.5mm² PUR jacket, 6 m | tme | 35 |
| 31 | Dry-side bulkhead | SubConn MCBH8F or potted Lapp equivalent | tme / quote  | 40 |
| 32 | Wet-mate inline | SubConn MCIL8M (service disconnect) | tme / quote | 45 |

## 3. STRUCTURE (bank + arm)

| # | item | spec | source | EUR |
|---|------|------|--------|-----|
| 33 | Pole | galvanised scaffold tube Ø48.3 x 3.2 x 3 m + drive spike | stavebniny/Mobiak | 18 |
| 34 | Arm tube | alu Ø28 x 1.5 x 1.3 m | hornbach/metal shop | 9 |
| 35 | Drop tube | alu Ø22 x 1.5 x 0.8 m | hornbach | 6 |
| 36 | Hinge collar + pin | printed ASA + M8 A4 bolt | print + tme | 3 |
| 37 | Yaw strut | alu Ø22 x 0.6 m + 2 clamps (flutter mitigation) | hornbach | 5 |
| 38 | Guy wires x2 | 3mm Dyneema + M5 turnbuckles | tme | 9 |
| 39 | Earth anchor for pole | ground screw 600mm | hornbach | 10 |
| 40 | Anti-vandal cap | printed ASA + locknut | print | 1 |

## 4. DRY BOX (electronics)

| # | item | spec | source | EUR |
|---|------|------|--------|-----|
| 41 | Enclosure | IP68 ready-made 190x130x80mm, NOT printed | tme.eu Fibox PC 100/75 HG or equiv | 22 |
| 42 | MCU | ESP32-S3-WROOM-1-N8 dev | laskakit | 12 |
| 43 | Radio | Wio-E5 (SX1262) mini board, 868 | techfun / seeed distributor | 15 |
| 44 | Antenna | 868 MHz 2dBi whip + SMA pigtail + IPEX u.FL | laskakit | 9 |
| 45 | PSU supervisor | TLV840 nanopower supervisor | tme | 1.5 |
| 46 | Buck | TPS62A02DRC step-down | tme | 2.5 |
| 47 | Boost harvester | LTC3105EFE MPPT boost (for low-EMF start) | tme | 5 |
| 48 | Rectifier | 3ph bridge, 6x PMEG2010AEB schottky | tme | 2 |
| 49 | Clamp | TL431LIAQ + MJD127 + PWR263S-20-3R30 dump | tme | 4 |
| 50 | Supercap | Eaton XLR-4R0507 500F 4.0V LIC (not 5.5V EDLC - ESR) | tme | 11 |
| 51 | Dry-box barometer | BME280 PCB (OUTSIDE potted zone, in vented sub-box) | laskakit LA131113 | 6 |
| 52 | Load switches | 2x TPS22860 pH/EC sequencing | tme | 2 |
| 53 | pH front-end | MCP6L02 precision op-amp + 1G bias resistor + ADC ref | tme | 6 |
| 54 | Cable glands dry box | 3x M12 IP68 potted | tme | 9 |
| 55 | PCB | custom 2-layer, JLC order | jlcpcb | 15 |
| 56 | Connectors + crimps | JST-PH, XH assortment | laskakit | 10 |
| 57 | Fuse + TVS + ESD | standard kit | tme | 6 |

## 5. CONSUMABLES / PRINT

| # | item | spec | source | EUR |
|---|------|------|--------|-----|
| 58 | Filament ASA | Prusament ASA 850g, Jet Black | prusa3d.com (SK delivery) | 32 |
| 59 | Filament PC-blend (wall) | Prusament PC Blend 970g | prusa3d.com | 40 |
| 60 | Epoxy barrier coat | West System 105 resin + 206 hardener | techfun | 18 |
| 61 | Conformal coat | Electrolube acrylic 200ml | tme | 14 |
| 62 | Silicone grease | Molykote 111 100g | tme | 9 |
| 63 | Threadlocker | Loctite 243 + 406 CA | tme | 11 |
| 64 | Heat-set inserts | M3/M4 brass assortment | tme | 6 |
| 65 | O-ring assortment | NBR metric kit | tme | 12 |

## 6. SITE / FIELD

| # | item | spec | source | EUR |
|---|------|------|--------|-----|
| 66 | Reference thermometer (calibration) | DS18B20 in sealed vial (cross-check) | techfun | 5 |
| 67 | Calibration cups + scales | kitchen scale 0.01g + DI water | home | 0 |
| 68 | Deployment tools | mallet, level, spanner set, waders | home | 0 |
| 69 | Vacuum test chamber | Bel-Art F42025 + gauge | tme | 85 |
| 70 | Bench drill/driver + torque driver Wiha 28506 | workshop | ~40 |

---

## Totals (v1, one probe, mid prices, EUR)

- wet mechanical + coupling:   ~91
- generator pod:               ~64
- sensor cage + sensors:       ~137  (pH kit included; subtract 69 without)
- wet-dry cable + connectors:  ~120
- structure:                   ~61
- dry electronics:             ~121
- consumables / print:         ~158
- site / field (incl. vac rig) ~130
- shipping budget              ~30

TOTAL (with pH):        ~812 EUR
TOTAL (without pH):     ~743 EUR
Recurring per 90d:      ~0 (own LoRa gateway), or ~6 NB-IoT SIM
Per-visit consumables:  pH buffers 2 EUR, electrode 9 EUR if replaced
                        (only on the pH interval, 14-30 days)

---

## Accuracy per channel — the honest numbers

| channel | part | accuracy claimable | drift / 30d | 90-day safe |
|---|---|---|---|---|
| temp | DS18B20 | +-0.5 C direct, +-0.1 after 0-pt cal | negligible | YES |
| depth | MS5837-30BA | +-2 cm with dry-box BME280 baro ref | negligible | YES |
| EC | DFRobot TDS | +-5% FS after 2-pt cal | small, mostly temp | YES |
| turbidity | SEN0169 | relative NTU only, needs site cal | fouling-limited | YES with wiper |
| flow (RPM) | rotor+hall | +-5% after volume cal | small | YES |
| pH | SEN0161-V2 hobby | +-0.1 pH fresh after 2-pt | **+-0.3 unserviced** | **NO - 14-30d interval** |

Why pH is honest at 30 days, not 90: glass electrode junction fouls;
slope decays; reference KCl diffuses. Nobody sells a 90-day pH electrode
at hobby prices. If the jury asks, the correct answer is "pH is our
premium short-interval channel; the long-duration autonomous record is
temp/EC/turbidity/depth/flow."

## Maintenance plan (the 90-day service)

- Day 0: fresh deploy, vacuum-tested pod, cal'd sensors, logged baseline
- Day 14-30 (pH only if fitted): swim-out, electrode swap, 5-min field
  cal, redeploy. Core probe untouched.
- Day 90: pod swap at the arm (single wet-mate connector). On bench:
  rotor/bearing check, magnet cup inspection, O-ring re-grease,
  desiccant swap, EC+turbidity cal, sensor wipe, full dry-box seal check.

## Low-water deployment (your recent observation)

Pod nominal 420mm. At low stage the drop tube is re-hung one notch
shallower (3 preset clips: 250 / 420 / 600mm). Below 250mm and the
blade tip breaks surface -> vortex ingestion -> unreliable RPM and
air lock on pH. The weed-guard then protects nothing. If the site
regularly drops below ~300mm, move to the deeper preset AND reduce
cadence; if it drops below ~250mm the pod is out of the water and the
design goal becomes "survive dry spell and restart", not "keep measuring".
That behaviour must be detectable in telemetry (RPM=0 + depth<0.25m).

## What still needs a measurement before ordering

1. **Cogging torque of the donor motor** (weight-on-arm jig) — gates everything
2. Flow-speed survey at the chosen site (3 visits, min/median/max)
3. MS5837 pressure drift after 24h submerged on the bench
4. Mag coupling slip torque on a printed jig (~0.35 Nm target)
5. Printed pod passes the vacuum-submerge acceptance test

---

# Sourcing update 2026-10-19 (verified live listings)

## Radio / LoRa
- Probe antenna: 868 MHz 5 dBi omni, SMA-M, 195 mm, ~6 EUR — neven.cz
  (SMA-M and RPSMA-M both in stock). Probe end does not need high gain; pole
  height does the work. Gateway end is where gain matters.
- Gateway antenna: MikroTik 868_Omni_Antenna, 862-876 MHz, 6.5 dBi, IP66,
  mast-mount kit (25-50 mm pole) + 1 m SMA cable — i4wifi.cz. THIS is the
  ridgeline/mast antenna for the 10 km+ links.
- Gateway: RAK2287 (SX1302 concentrator, mini-PCIe) + Pi HAT + Raspberry Pi 4
  + above antenna. Budget 180-220 EUR per gateway, covers every probe within
  ~10 km radio horizon. Two gateways cover the whole middle Hron.

## Generator candidates (gimbal BLDCs used as 3-phase alternators)
- X-TEAM XTG3506 — sk.x-teamrc.com (Slovak!). 24N22P, 6 ohm, 42 g,
  0.08 N·m @ 11.1 V, inbuilt AS5048A encoder (free RPM telemetry = free flow
  measurement, no extra sensor). Measure cogging first — gating #1.
- T-Motor GB2208 KV128 — 39.5 g, 14.4 ohm, advertised low-cogging, ~26 USD.
- iFlight GM3506 — 5.6 ohm, hollow shaft 12 mm (routing option for shaft).
NOTE: all three are ~130-300 rpm/V class, LOWER than my sim's assumed 300 -
good: higher EMF per spin. Sim v3 bus check stays the gating formula.

## Power
- Supercap decision: Eaton XLR-4R0507 LIC 500 F 4.0 V stands (field-failure
  review reason: 5.5 V EDLC coin cells like Eaton KR-5R5H474 have ~50 ohm ESR,
  which browns out a 40 mA LoRa burst - do NOT cheapen to the coin class).
- Rectifier diode: Nexperia PMEG2010AEB,115 in stock at TME (SOD-523, 20 V,
  1 A, Vf 270 mV @ 100 mA). 6x per probe.
- MCU: LaskaKit ESP32-S3-DEVKit — measured ~12 uA deep sleep board-level,
  Li-ion charger onboard; beats generic S3 boards for sleep budget.

## Sensors (verified before)
- Turbidity DFRobot SEN0189: techfun.sk, 12.45 EUR, 6 in stock.
- TDS DFRobot SEN0244: TME. pH: DFRobot SEN0161-V2.
- Temp: DS18B20 waterproof 1 m: techfun.sk (multiple listings ~3-6 EUR).
- Depth: MS5837-30BA01: components-store.cz (5941 pcs) or Blue Robotics
  Bar30 carrier if potted-ready preferred.
- Baro ref: BME280 module: laskakit.cz (in dry box, NOT potted).

## Revised totals (with pH deferred to per-site option)
- Probe, no pH: ~430-470 EUR (was 743; SubConn wet-mate swapped to potted
  gland + on-bank disconnect, pH kit out, connector savings verified).
- Attribution network, middle Hron (20 probes + 2 gateways):
  20 x ~450 + 2 x ~200 = ~9400 EUR one-off, ~0 recurring.
- pH module add-on per selected intake site: ~70 EUR.

---

# Machined / non-printable materials (verified 2026-10-19)

## Magnets (the coupling hearts)
- magsy.sk (SK) — cylinder N52 Ø8x5 exists in their cylinder catalogue
  (axial magnetization). Bare N52 still needs canning: potted in DP270 +
  316L foil wrap; canned Ø8 with resin/Inox cup exists at
  supermagneticshop.com ("SM05"/"SM08 INOX", epoxy/Inox coated, from
  ~0.30 EUR at 51+ pcs) — cheaper than machining our own cans.
- 16 per probe; cost < 6 EUR either path.

## Bearings (wet shaft)
- igus iglidur J plain bearings at tme.eu — JSM-0507-05 (5x7x5 mm, 83 pcs
  in stock, 1.18 USD) or flanged JFM-0507-05 (170 pcs). These are the
  official water/dirt-proof plain bearings the adversarial review named
  (RR-01). No PEEK machining needed for v1 — iglidur J is the better
  wet bearing anyway. 2x per probe.
- MR105ZZ steel ball bearings exist (NSK/EZO) but only for the DRY
  generator-side reference jig, not submerged.

## Steel / rod stock
- nerezmaterial.cz (Brno, delivers SK): nerezová tyč kruhová Ø5 h9,
  Wst.Nr. 1.4301 (AISI 304) 3 m bar = 63.1 Kč (~2.6 EUR).
  For the wet shaft use their 316L (1.4404) on request — same shop,
  on-quote for small sections. One 3 m bar = ~26 shafts.
- Pole: scaffold tube Ø48.3 zinc — stavebniny local (listed already).
- Bearing carrier tube: 316SS Ø12xØ8 — nerezmaterial "trubka" section
  or cut from Ø12 bar stock; fallback: brass tube from modelař shop.

## O-rings / chemicals
- NBR O-rings metric kit + Ø100x2.5 singles: tme.eu/gme.sk (listed).
- Molykote 111 100 g: tme.eu. Loctite 243: tme.eu / local auto shop
  (MotoPlex etc). DP270: techfun.sk. West 105/206: techfun.sk.

## Verdict on "stuff we can't print"
Nothing on this probe is unreachable from SK/CZ shops. The only true
machine-shop touch is IF we wanted machined PEEK bushings — avoided by
using igus iglidur J stock parts, which are also the correct wet-bearing
engineering answer.

