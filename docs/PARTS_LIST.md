# Parts list — single source of truth

Generated from `PARTS_LIST.csv`. Every line maps to a part in `cad/probe_cq.py`.
Status: verified = live listing seen, quote = needs supplier quote, printed = in-house, todo = not yet in model.

## rotor
| id | part | spec | qty | source | EUR | status |
|---|---|---|---|---|---|---|
| A01 | Blade | triple-blade rotor blade NACA4412 D220mm root pitch 28deg tip 2deg | 3 | printed in-house | - | printed |
| A02 | Hub | Ø64x46mm with 2x M4 heat-set inserts and Ø5 H7 shaft bore | 1 | printed in-house | - | printed |
| A03 | Wet shaft | 316L Ø5 h6 x 115mm ground; 2 flats each end | 1 | nerezmaterial.cz | 2.6 | verified |
| A04 | Wet bearing | igus iglidur J plain bearing JSM-0507-05 5x7x5mm | 2 | tme.eu | 1.18 | verified |
| A05 | Bearing carrier tube | 316L Ø12xØ8x55mm | 1 | nerezmaterial.cz | 1.2 | quote |
| A06 | Set screw | M4x8 316SS cup point ISO 4029 | 2 | tme.eu | 1.0 | verified |
| A07 | Weed guard ring | Ø250 printed ring + 3 struts 40mm upstream of blade plane | 1 | printed in-house | - | printed |
| A08 | Blade safety retainer | 3mm stainless lanyard + crimp ferrule | 3 | tme.eu | 2.0 | verified |

## coupling
| id | part | spec | qty | source | EUR | status |
|---|---|---|---|---|---|---|
| B01 | Magnet | N52 Ø8x5 axially magnetised canned 316L or epoxy | 16 | magsy.sk / supermagneticshop.com | 0.30 | verified |
| B02 | Magnet cup | Ø48 rim potted magnets ASA | 2 | printed in-house | - | printed |
| B03 | Separation wall | Ø106x5mm POM-C machined or PC-blend printed; integral with pod nose | 1 | nerezmaterial.cz / printed | - | quote |
| B04 | Potting compound | 3M Scotch-Weld DP270 black 25ml | 1 | techfun.sk | 14.0 | verified |

## pod
| id | part | spec | qty | source | EUR | status |
|---|---|---|---|---|---|---|
| C01 | Pod barrel | Ø110x120mm printed ASA wall 2.4mm + epoxy barrier | 1 | printed in-house | - | printed |
| C02 | Tail cone | printed integral | 1 | printed in-house | - | printed |
| C03 | Pod O-ring | NBR 70 Ø100x2.5 | 1 | tme.eu | 3.0 | verified |
| C04 | O-ring groove | 2.2mm wide x 1.8mm deep machined/printed into pod rim | 1 | in CAD | - | todo |
| C05 | Pod clamp screws | M4x30 A4 + washers | 6 | tme.eu | 3.0 | verified |
| C06 | Desiccant | 5g silica gel with indicator | 2 | local | 2.0 | verified |
| C07 | Cable gland wet side | Lapp Skintop MS-M 12x1.5 + Scotchcast 2131 | 1 | tme.eu | 12.0 | verified |
| C08 | Generator | T-Motor GB2208 KV128 or X-TEAM XTG3506 (24N22P 6ohm w/ AS5048A encoder) | 1 | sk.x-teamrc.com / tmotor | 26.0 | verified |
| C09 | Generator mount | printed cradle + 4x M3x8 A4 | 1 | printed + tme | 1.0 | printed |

## sensors
| id | part | spec | qty | source | EUR | status |
|---|---|---|---|---|---|---|
| D01 | pH electrode | DFRobot SEN0161-V2 Gravity pH kit + E201 BNC probe | 1 | techfun.sk | 39.0 | verified |
| D02 | pH spare electrode | E201-C BNC | 2 | techfun.sk | 9.0 | verified |
| D03 | pH buffer | 2x250ml pH7 + pH10 | 1 | techfun.sk | 12.0 | verified |
| D04 | Temperature | DS18B20 waterproof 1m cable | 1 | techfun.sk | 5.0 | verified |
| D05 | Depth/pressure | MS5837-30BA01 (TE) on carrier PCB | 1 | components-store.cz | 8.6 | verified |
| D06 | EC/TDS | DFRobot SEN0244 Gravity analog TDS module + probe | 1 | tme.eu | 14.0 | verified |
| D07 | Turbidity | DFRobot SEN0189 (0-4.5V analog) | 1 | techfun.sk | 12.45 | verified |
| D08 | Sensor cable | 4x2x0.5mm shielded PUR outdoor | 4 | tme.eu | 20.0 | verified |

## cage
| id | part | spec | qty | source | EUR | status |
|---|---|---|---|---|---|---|
| E01 | Sensor cage | Ø130x150 printed ASA 12 slots | 1 | printed in-house | - | printed |
| E02 | Cage fasteners | M3x10 A4 + nylok | 12 | tme.eu | 6.0 | verified |
| E03 | Sensor holders | printed clips for pH/TDS/turbidity/NTC/MS5837 | 5 | printed in-house | - | printed |

## interface
| id | part | spec | qty | source | EUR | status |
|---|---|---|---|---|---|---|
| F01 | Cable | 8x0.5mm2 PUR jacket submersible 6m | 1 | tme.eu | 35.0 | verified |
| F02 | Bulkhead connector | potted gland entry (NOT SubConn) | 1 | tme.eu | 12.0 | verified |

## drybox
| id | part | spec | qty | source | EUR | status |
|---|---|---|---|---|---|---|
| G01 | Enclosure | IP68 ready-made 190x130x80mm | 1 | tme.eu | 22.0 | verified |
| G02 | MCU | LaskaKit ESP32-S3-DEVKit (~12uA sleep) | 1 | laskakit.cz | 12.0 | verified |
| G03 | Radio | Wio-E5 SX1262 868MHz mini board | 1 | techfun.sk | 15.0 | verified |
| G04 | Antenna probe | 868MHz 5dBi SMA-M omni 195mm | 1 | neven.cz | 6.0 | verified |
| G05 | Antenna pigtail | u.FL to SMA bulkhead 15cm | 1 | tme.eu | 3.0 | verified |
| G06 | Boost harvester | LTC3105EFE MPPT boost | 1 | tme.eu | 5.0 | verified |
| G07 | Buck | TPS62A02DRC step-down | 1 | tme.eu | 2.5 | verified |
| G08 | Rectifier | Nexperia PMEG2010AEB 20V 1A SOD-523 | 6 | tme.eu | 0.15 | verified |
| G09 | Clamp | TL431LIAQ + MJD127T4G + PWR263S 3.3R dump | 1 | tme.eu | 4.0 | verified |
| G10 | Supercap | Eaton XLR-4R0507 LIC 500F 4.0V | 1 | tme.eu | 11.0 | quote |
| G11 | Voltage supervisor | TLV840 nanopower | 1 | tme.eu | 1.5 | verified |
| G12 | Load switch | TPS22860 x2 for pH/EC sequencing | 2 | tme.eu | 1.0 | verified |
| G13 | Barometer | BME280 module outside potting in vented sub-box | 1 | laskakit.cz | 6.0 | verified |
| G14 | PCB | custom 2-layer 60x80mm | 1 | jlcpcb | 3.0 | quote |
| G15 | Connectors | JST-PH/XH assortment + crimps | 1 | laskakit.cz | 10.0 | verified |
| G16 | Protection | Fuse 0.5A + TVS + ESD array | 1 | tme.eu | 6.0 | verified |
| G17 | Cable glands | M12 IP68 potted x3 | 3 | tme.eu | 3.0 | verified |

## site
| id | part | spec | qty | source | EUR | status |
|---|---|---|---|---|---|---|
| H01 | Ground screw anchor | M68 x 800mm solar-fence ground screw | 1 | hornbach | 25.0 | verified |
| H02 | Pole | scaffold tube Ø48.3x3.2 x 3000mm galvanised | 1 | stavebniny | 18.0 | verified |
| H03 | Receiver sleeve | Ø52 tube 300mm + pin holes | 1 | metal shop | 8.0 | quote |
| H04 | Arm tube | alu Ø28x1.5 x 1300mm | 1 | hornbach | 9.0 | verified |
| H05 | Drop tube | alu Ø22x1.5 x 900mm | 1 | hornbach | 6.0 | verified |
| H06 | Hinge collar | printed ASA + M8 A4 bolt | 1 | printed + tme | 3.0 | printed |
| H07 | Shear pin | M4 316SS pin + 2 spares on pole collar | 3 | tme.eu | 1.0 | verified |
| H08 | Yaw strut | alu Ø22x600mm + 2 clamps | 1 | hornbach | 5.0 | verified |
| H09 | Guy line | 3mm Dyneema 2x4m + turnbuckles | 2 | tme.eu | 9.0 | verified |
| H10 | Guy anchor | 300mm ground screw x2 | 2 | hornbach | 10.0 | verified |
| H11 | Safety cable | 3mm galv wire + ferrules tethering pod to pole | 1 | tme.eu | 4.0 | verified |
| H12 | Security fastener | one-way Torx M5 + steel band for box | 1 | tme.eu | 4.0 | verified |
| H13 | Site label | engraved plate with project + contact | 1 | local print shop | 3.0 | verified |

## gateway
| id | part | spec | qty | source | EUR | status |
|---|---|---|---|---|---|---|
| I01 | Gateway concentrator | RAK2287 SX1302 868MHz mini-PCIe + Pi HAT | 0 | rakwireless reseller | 120.0 | quote |
| I02 | Compute | Raspberry Pi 4 4GB + PSU + SD | 0 | local | 70.0 | verified |
| I03 | Antenna | MikroTik 868_Omni 6.5dBi IP66 862-876MHz + mast kit | 0 | i4wifi.cz | 45.0 | quote |
| I04 | Enclosure | IP65 box + PoE injector | 0 | tme.eu | 35.0 | verified |
| I05 | Mast | 3m alu mast + wall bracket | 0 | hornbach | 30.0 | verified |

## consumable
| id | part | spec | qty | source | EUR | status |
|---|---|---|---|---|---|---|
| J01 | Filament ASA | Prusament ASA 850g | 1 | prusa3d.com | 32.0 | verified |
| J02 | Filament PC Blend | Prusament PC Blend 970g (for wall/structural) | 1 | prusa3d.com | 40.0 | verified |
| J03 | Epoxy barrier | West System 105 + 206 | 1 | techfun.sk | 18.0 | verified |
| J04 | Conformal coat | Electrolube acrylic 200ml | 1 | tme.eu | 14.0 | verified |
| J05 | Silicone grease | Molykote 111 100g | 1 | tme.eu | 9.0 | verified |
| J06 | Threadlocker | Loctite 243 + 406 | 1 | tme.eu | 11.0 | verified |
| J07 | Heat-set inserts | M3/M4 brass assortment | 1 | tme.eu | 6.0 | verified |
| J08 | O-ring kit | NBR metric assortment | 1 | tme.eu | 12.0 | verified |

## tooling
| id | part | spec | qty | source | EUR | status |
|---|---|---|---|---|---|---|
| K01 | Vacuum chamber | Bel-Art F42025 + gauge + pump | 1 | tme.eu | 85.0 | verified |
| K02 | Torque driver | Wiha 28506 1.2Nm | 1 | tme.eu | 40.0 | verified |
| K03 | Spring balance | 0-5N for coupling slip jig | 1 | local | 5.0 | verified |
