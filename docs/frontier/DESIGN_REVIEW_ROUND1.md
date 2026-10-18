

## anthropic/claude-opus-5.5

[NULL]

## google/gemini-4-argon

1. [CRITICAL] At $K_v = 300\text{ rpm/V}$ and $v = 0.5\text{ m/s}$ ($\text{TSR } 5.5$), rotor speed is $239\text{ rpm}$, yielding only $\sim 0.8\text{ V}$ open-circuit EMF—after two $1\text{N}5819$ Schottky drops ($2 \times 0.35\text{ V}$), net output cannot charge a $3.0\text{–}5.0\text{ V}$ supercap without a step-up converter or a geared/much-lower-$K_v$ generator.
2. [CRITICAL] `cutin_speed()` computes breakaway using dynamic running torque at $\text{TSR} = 5.5$, which is physically invalid because at $\omega = 0$ ($\text{TSR} = 0$) the blades are stalled at high angle of attack and produce a small fraction of peak running torque.
3. [CRITICAL] The wet rotor assembly (`rotorside_z` + `rotor_axis_z`) has no shaft, radial bearing, or thrust bearing defined anywhere in the CAD or spec; magnetic attraction across the $5\text{ mm}$ wall will pull the wet cup directly against the dry pod wall, locking the rotor by friction.
4. [CRITICAL] The `river()` CAD model sets water depth to $260\text{ mm}$ (`z` from $-260$ to $0$), which places the $420\text{ mm}$ deep pod and its $220\text{ mm}$ rotor ($z = -310$ to $-530\text{ mm}$) completely buried inside the riverbed (`z = -260` to $-300\text{ mm}$) and sub-bed.
5. [HIGH] In `probe.scad`, `wetpod_z()` places the `rotor_axis_z()` center at $z=0$ and `genpod_z()` front wall at $z = 24\text{ mm}$ (`hub_len/2 + 6 - magcup_gap`), causing the `rotorside_z()` wet magnet cup ($z = -13$ to $+1\text{ mm}$) to intersect the rotor hub ($z = -23$ to $+23\text{ mm}$) and sit $23\text{ mm}$ away from the barrier wall instead of flush against it.
6. [HIGH] The open $220\text{ mm}$ 3-blade rotor lacks an upstream debris guard or weed deflector, guaranteeing rapid fouling and stall from riverine leaves, filamentous algae, and plastic in any natural flow.
7. [HIGH] The MS5837-30BA is an absolute pressure sensor ($0\text{–}30\text{ bar}$ full-scale, $\sim 2\text{ mbar}$ resolution $\approx 2\text{ cm}$ water), so using it for river stage without an atmospheric barometer reference in the dry box (the internal BME280 is sealed inside an IP68 potted enclosure) will alias synoptic weather pressure swings ($\pm 30\text{ mbar} \approx \pm 30\text{ cm}$ water) directly into depth readings.
8. [HIGH] There is no overvoltage clamp or dump load on the supercap bus; at $v = 1.0\text{ m/s}$ ($3.5\text{ W}$) or higher flows, the $5.5\text{ V}$ supercap will overcharge and vent within seconds once full.
9. [HIGH] Measuring pH and EC simultaneously in the same unisolated water volume creates ground-loop errors unless the EC excitation is bipolar AC and one or both analog front-ends are galvanically isolated (noted in `sim.py` output string, but absent from the hardware architecture and power budget).
10. [HIGH] Uncoated N52 NdFeB magnets in the wet cup will rapidly corrode and spall in river water; they require complete hermetic encapsulation (e.g., epoxy potting or marine-grade stainless cans).
11. [MEDIUM] The build-before-order list places the site flow-speed survey at step 4, whereas river velocity at the bank edge dictates whether a $220\text{ mm}$ rotor can ever start and must be gated at step 1 before sizing the generator or blades.
12. [MEDIUM] The $1.2\text{ m}$ (`1500 mm` in SCAD) cantilevered OD28 swing arm and drop tube lack a yaw constraint or stays; hydrodynamic drag and vortex-induced vibration on the pod and drop tube will cause the hinged arm to swing downstream to the bank and twist.
13. [MEDIUM] `P_SLEEP` in `sim.py` is commented as `A * 3.3V` (`45e-6`), which is $45\ \mu\text{W}$ ($\sim 13.6\ \mu\text{A}$ at $3.3\text{ V}$), underestimating the quiescent current of an ESP32-S3 + buck regulator + supercap leakage + pH/EC analog front-end standby.
14. [MEDIUM] A $0.5\text{ bar}$ *vacuum* test inside a 3D-printed pod does not properly validate external hydrostatic sealing and risks imploding or delaminating thin layer lines inward; positive external water-pressure testing or internal air pressurization with bubble-check is required.
15. [LOW] In `blade()`, `linear_extrude(0.1)` precedes `rotate([0,-t0,0])` and `scale([c0,c0,1])`, which extrudes the airfoil along global Z (streamwise) rather than spanwise X before hulling, distorting the leading/trailing edge geometry at high twist angles.