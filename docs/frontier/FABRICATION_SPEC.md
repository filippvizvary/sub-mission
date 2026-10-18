

# mech

# FABRICATION SPECIFICATION: RIVER PROBE POD (REV 1.0)

## 1. GENERAL PRINT & MACHINING PARAMETERS
*   **FDM Material (Wet/Structural):** ASA (UV/impact resistant) for external cowlings, PETG for internal brackets.
*   **Print Settings:** 0.4 mm nozzle, 0.2 mm layer height, 6 perimeters (2.4 mm wall thickness), 50% gyroid infill, 6 top/bottom solid layers (1.2 mm).
*   **Machined Polymer:** Virgin PEEK (unfilled), POM-C (Acetal) for static plugs.
*   **Metals:** 316L Stainless Steel (all wetted fasteners, shafts, and structural tubes).
*   **Potting/Sealing Compound:** 3M Scotch-Weld DP270 Black (rigid potting) or Loctite Stycast 2850FT with Catalyst 9.
*   **Adhesive/Threadlocker:** Loctite 406 (cyanoacrylate for O-ring splicing if needed), Loctite 243 (medium strength threadlocker for 316SS).
*   **Lubricant:** Dow Corning Molykote 111 (O-ring silicone grease).

---

## 2. HYDRODYNAMIC ROTOR & HUB ASSEMBLY
*   **Geometry:** 3-blade, Ø220.0 mm swept diameter, NACA 4412 airfoil profile, constant 28° root-to-tip pitch (optimized for 0.8–1.5 m/s flow).
*   **Hub Dimensions:** Ø64.0 mm OD × 46.0 mm L, conical nose fairing (R15 mm tip radius).
*   **Shaft Bore:** Ø5.0 mm H7 (+0.012/0 mm) central axial bore, 40.0 mm deep from aft face.
*   **Retention Feature:** Dual M4 radial bores at 90° offset, 15.0 mm from aft face, fitted with M4 × 0.7 heat-set brass inserts (McMaster 94180A351, press-fit to 6.0 mm depth).
*   **Fasteners:** 2× M4 × 8 mm 316SS cup-point set screws (ISO 4029).
*   **Post-Processing:** Wet-sand blades to 600 grit, vapor-smooth (acetone for ASA) or brush-coat with West System 105/206 epoxy (thin coat, 0.15 mm max) to seal layer lines against water ingress. Balance statically on a razor-edge jig by drilling Ø3.0 mm blind holes inside the aft hub face.

---

## 3. WET DRIVE TRAIN & MAGNETIC COUPLING

### 3.1 Wet Shaft
*   **Part:** Ø5.0 mm h6 (+0/-0.008 mm) × 115.0 mm L precision ground 316SS linear shaft (McMaster 1263K12).
*   **Machining:** Grind two 3.5 mm wide × 0.5 mm deep flats at the forward end (for hub set screws) and two matching flats at the aft end (for wet mag cup retention). Chamfer ends 0.5 mm × 45°.

### 3.2 Bearing Carrier & PEEK Bushings
*   **Carrier Tube:** 316SS seamless tubing, Ø12.0 mm OD × Ø8.0 mm ID × 55.0 mm L, welded or press-fit + epoxied into the forward wet stator nosecone.
*   **Bushings (×2):** Machined Virgin PEEK.
    *   **OD:** Ø8.0 mm r6 (+0.019/+0.010 mm) for press-fit into carrier.
    *   **ID (Installed):** Ream after press-fitting to Ø5.05 mm (+0.03/+0.00 mm) to allow for 0.2% water absorption swell and silt clearance.
    *   **Length:** 12.0 mm each, spaced 31.0 mm apart.
    *   **Flange:** Ø12.0 mm OD × 2.0 mm thick on both bushings to take axial thrust loads.
    *   **Debris Grooves:** Broach 3× axial grooves (1.0 mm wide × 0.5 mm deep) along the ID to flush fine silt.

### 3.3 Magnetic Coupling (Axial-Flux Face Type)
*   **Wet Mag Cup (Driver):** PETG, Ø42.0 mm OD × 18.0 mm L.
    *   **Shaft Interface:** Ø5.0 mm H7 bore with dual M3 × 5 mm 316SS set screws into M3 heat-set inserts.
    *   **Magnet Array:** 8× Ø8.0 mm × 5.0 mm N52 NdFeB disc magnets (Ni-Cu-Ni plated), arranged on a Ø30.0 mm Bolt Circle Diameter (BCD), alternating N-S polarity.
    *   **Pockets:** Ø8.2 mm × 5.5 mm deep, leaving a 0.5 mm recessed lip.
    *   **Capping/Canning:** Pot magnets into pockets with DP270 epoxy. Bond a 0.5 mm thick PETG or 316SS shim disc over the face using DP270 to completely encapsulate magnets from river water.
*   **Dry Mag Cup (Driven):** Identical magnet array and Ø30.0 mm BCD, machined/printed from PETG, bored to match BLDC rotor shaft **[FLAG: Re-derive bore diameter and mounting bolt pattern from actual selected BLDC motor datasheet]**.
*   **Air/Wall Gap:**
    *   Wet Cup to Barrier Wall: 1.5 mm.
    *   Barrier Wall Thickness: 5.0 mm (flat face of Main Pod Bulkhead).
    *   Barrier Wall to Dry Cup: 1.5 mm.
    *   **Total Magnet-to-Magnet Gap:** 8.0 mm.

---

## 4. SEALED GENERATOR & ELECTRONICS POD

### 4.1 Main Housing Cylinder
*   **Dimensions:** Ø110.0 mm OD × Ø98.0 mm ID (6.0 mm solid wall) × 120.0 mm L.
*   **Material:** CNC-turned PVC Schedule 80 pipe (bored true) or lathe-turned solid POM-C (Acetal) billet. *(Note: If 3D printed in PETG, print with 100% concentric infill, 0.15 mm layers, and coat internal bore with 0.5 mm DP270 epoxy, then lathe-turn O-ring sealing counterbores to Ra 0.8 μm).*
*   **Sealing Counterbores:** Both ends bored to Ø100.00 mm H8 (+0.054/-0.000 mm) × 18.0 mm deep, with a 15°×2.0 mm lead-in chamfer to prevent O-ring shearing.

### 4.2 Forward Bulkhead (Magnetic Barrier & Stator Mount)
*   **Material:** CNC-machined POM-C or PETG (solid 100% infill, CNC finished).
*   **Flange:** Ø110.0 mm OD × 10.0 mm thick.
*   **Spigot (Piston Seal):** Ø99.90 mm f7 (-0.036/-0.071 mm) × 16.0 mm L.
*   **O-Ring Grooves (Dual Radial):** 2× grooves cut into spigot, 4.0 mm wide × 2.75 mm deep (Groove Ø94.40 mm), spaced 4.0 mm apart.
*   **O-Rings:** 2× AS568-239 (3.53 mm CS × 91.67 mm ID) Buna-N 70A.
*   **Magnetic Barrier Face:** Central Ø46.0 mm pocket milled from the inside to leave a precise **5.00 mm ±0.10 mm** flat wall thickness.
*   **BLDC Mount:** 4× M3 tapped holes (or heat-set inserts) on the dry side, concentric with the outer diameter within 0.05 mm TIR **[FLAG: Re-derive bolt circle and axial standoff height from actual BLDC motor stack length so dry mag cup sits 1.5 mm from inner wall]**.
*   **Retention:** 6× M4 × 20 mm 316SS Socket Head Cap Screws (SHCS) on a Ø104.0 mm BCD, threading into axial M4 inserts/tapped holes in the Main Housing wall, OR 3× external Ø4.0 mm 316SS tie-rods spanning forward-to-aft bulkheads.

### 4.3 Aft Bulkhead (Cable Pass-Through)
*   **Spigot & Seals:** Identical to Forward Bulkhead (Ø99.90 mm spigot, dual AS568-239 O-rings).
*   **Wall Thickness:** 12.0 mm solid.
*   **Center Port:** Tapped M16 × 1.5 through-hole at center (or offset 20.0 mm radially) for a Blue Robotics WetLink Penetrator (WLP-M10 or M16 depending on cable OD) **[FLAG: Re-derive thread spec based on final umbilical cable outer diameter]**.
*   **Purge Port:** Tapped M6 × 1.0 through-hole, counterbored for an AS568-010 O-ring under an M6 × 10 mm 316SS sealing screw (for vacuum leak testing).

---

## 5. FLOW-THROUGH SENSOR CAGE (AFT SECTION)
*   **Dimensions:** Ø130.0 mm OD × Ø120.0 mm ID (5.0 mm wall) × 150.0 mm L.
*   **Material:** 3D printed ASA.
*   **Flow Slots:** 12× radial slots, 12.0 mm wide × 100.0 mm long, equally spaced (30° intervals), starting 25.0 mm from the forward edge. Slot ends full-radiused (R6.0 mm) to reduce stress risers.
*   **Forward Transition Collar:** Steps down from Ø130.0 mm OD to slip-fit over the Ø110.0 mm Main Pod OD (overlap 25.0 mm). Clamped via 4× M5 × 16 mm 316SS SHCS radial pinch bolts into captive M5 hex nuts (DIN 934).
*   **Internal Sensor Mount:** Removable internal spider bracket (PETG), Ø119.5 mm OD × 20.0 mm thick, retained by 3× M4 × 12 mm button-head screws through the cage wall. Central bore with twin EPDM-lined P-clamps or a printed split-clamp with 2× M4×25 mm bolts **[FLAG: Re-derive internal clamp diameter from physical water quality probe/sonde body OD]**.

---

## 6. UPSTREAM WEED GUARD
*   **Ring Dimensions:** Ø240.0 mm OD (oversized 20 mm beyond rotor diameter to deflect debris outward), 8.0 mm cross-section diameter (torus).
*   **Position:** 40.0 mm upstream of the rotor blade leading edges.
*   **Material:** 316SS Ø8.0 mm solid rod rolled and TIG-welded into a ring, with 4× Ø6.0 mm 316SS struts swept back at a 35° angle to shed weeds.
*   **Attachment:** Struts terminate in flattened tabs (2.5 mm thick × 14.0 mm wide) with Ø5.5 mm through-holes, bolting directly to the exterior of the Ø110.0 mm Forward Bulkhead flange via 4× M5 × 16 mm 316SS SHCS.

---

## 7. DEPLOYMENT RIG: DROP TUBE, ARM, & POLE

### 7.1 Vertical Drop Tube (Pod-to-Arm Strut)
*   **Tube:** 316SS seamless round tube, Ø25.4 mm (1.00") OD × 2.0 mm wall × 400.0 mm L.
*   **Pod Saddle Clamp:** 2-piece CNC-machined POM-C or 3D-printed ASA block (100% infill, 40.0 mm wide).
    *   Lower half bolts to the top of the Ø110.0 mm Main Pod using 4× M6 × 30 mm 316SS U-bolts or bands.
    *   Upper socket accepts the Ø25.4 mm drop tube vertically, pinned with 2× M6 × 40 mm 316SS hex bolts (ISO 4017) and Nyloc nuts (ISO 7040) spaced 25.0 mm apart.
*   **Cable Routing:** Drill a Ø14.0 mm ovalized slot (14 mm × 25 mm, deburred and fitted with a 2.0 mm wall rubber grommet) 50.0 mm above the bottom of the drop tube to route the umbilical cable internally up the tube.

### 7.2 Cantilever Arm (1.2 m)
*   **Beam:** 40.0 mm × 40.0 mm × 3.0 mm wall 316SS square hollow section (SHS), 1200.0 mm L.
*   **Outboard End (Drop Tube Mount):** Weld a 100.0 mm long vertical sleeve of Ø32.0 mm OD × 3.0 mm wall 316SS tube (Ø26.0 mm ID) to the side face of the square arm. Drill 2× Ø6.5 mm cross-holes to match the Ø25.4 mm drop tube for height adjustment pinning via M6 clevis pins.
*   **Guy Wire / Yaw Restraint Lug:** Weld a 5.0 mm thick 316SS eye-tab at the outboard tip for an upstream stabilization tether (prevents arm torsion in >2.0 m/s currents).

### 7.3 Main Bank/Riverbed Pole & Pivot Clamp
*   **Pole:** Ø48.3 mm OD × 3.68 mm wall (1-1/2" Schedule 40) 316SS or galvanized steel pipe, length site-dependent (standard 3000.0 mm with 45° Machined Drive Point at base).
*   **Inboard Arm-to-Pole Clamp:**
    *   Weld a 6.0 mm thick × 120.0 mm × 120.0 mm 316SS backing plate to the inboard end of the 1.2 m square arm, gusseted with 2× 50 mm × 50 mm × 5 mm triangular webs.
    *   Clamp to the Ø48.3 mm pole using 2× heavy-duty M8 × 50 mm ID 316SS U-bolts (with saddle plates and Nyloc nuts), spaced 90.0 mm vertically.

---

## 8. STEP-BY-STEP ASSEMBLY & TEST PROCEDURE

1.  **Rotor & Wet Cup Prep:**
    *   Install M4 and M3 heat-set inserts into the Rotor Hub and Wet Mag Cup using a temperature-controlled soldering iron at 240°C (for PETG/ASA).
    *   Pot the 8× N52 magnets into both Wet and Dry Mag Cups using 3M DP270. Verify alternating polarity with a Gauss meter or pole identifier before epoxy cures. Cure 24 hrs at 22°C.
2.  **Wet Drive Assembly:**
    *   Press the two PEEK bushings into the forward stator carrier tube using an arbor press. Ream ID to Ø5.05 mm.
    *   Slide the Ø5.0 mm 316SS shaft through the bushings. Install a 0.5 mm thick PEEK thrust washer on both ends.
    *   Mount the Wet Mag Cup on the aft shaft end; apply Loctite 243 to the two M3 set screws and torque to 0.8 Nm.
    *   Mount the Rotor Hub on the forward shaft end; verify a 0.5 mm axial end-play so the bushings are not pre-loaded. Torque M4 set screws to 1.5 Nm.
3.  **Dry Pod Internal Assembly:**
    *   Mount the Dry Mag Cup to the BLDC motor shaft.
    *   Bolt the BLDC motor to the interior of the Forward Bulkhead using M3 screws + Loctite 243 (Torque: 1.2 Nm). Verify the Dry Mag Cup rotates freely with 1.5 mm clearance from the inner bulkhead face.
    *   Pot the umbilical cable into the Aft Bulkhead WetLink penetrator per manufacturer spec (or install compression gland). Solder/crimp motor phase wires and sensor power/comms lines inside the pod.
4.  **Sealing & Vacuum Test:**
    *   Inspect all 4× AS568-239 O-rings for nicks. Apply a thin film of Molykote 111 grease to O-rings and housing counterbores.
    *   Press Forward and Aft Bulkheads into the Ø110.0 mm Main Housing. Secure with the 6× M4 SHCS (Torque: 2.5 Nm).
    *   Connect a hand vacuum pump to the M6 purge port on the Aft Bulkhead. Pull a vacuum of -0.5 bar (-15 inHg). Hold for 30 minutes. Zero pressure loss is required before deployment. Install M6 sealing plug with O-ring.
5.  **External Integration:**
    *   Bolt the forward wet stator carrier to the exterior of the Forward Bulkhead. Verify the Wet Mag Cup locks magnetically to the Dry Mag Cup and turns smoothly with low cogging torque.
    *   Bolt the Ø240.0 mm Weed Guard struts to the Forward Bulkhead flange (4× M5 SHCS, Torque: 4.0 Nm). Confirm 40.0 mm clearance to blades.
    *   Slide the Ø130.0 mm Sensor Cage over the aft end of the Main Pod. Secure the pinch collar (4× M5 SHCS, Torque: 3.5 Nm). Insert the water quality probe into the internal spider bracket and tighten clamp bolts.
    *   Route the umbilical cable up through the Ø25.4 mm Drop Tube grommet, bolt the Drop Tube saddle to the Main Pod, and pin the Drop Tube into the 1.2 m Cantilever Arm.

---

## 9. FLAGGED DIMENSIONS (RE-DERIVE BEFORE CUTTING METAL/PLASTIC)
*   **[FLAG 1 - Sec 3.3]:** Dry Mag Cup central bore diameter and shaft retention method (must match selected BLDC rotor shaft/bell).
*   **[FLAG 2 - Sec 4.2]:** Forward Bulkhead internal BLDC mounting bolt circle and standoff height (must position the dry magnet face exactly 1.5 mm from the 5.0 mm barrier wall).
*   **[FLAG 3 - Sec 4.3]:** Aft Bulkhead penetrator thread size (must be sized to the exact OD of the selected polyurethane-jacketed river umbilical cable).
*   **[FLAG 4 - Sec 5.0]:** Sensor Cage internal spider clamp ID (must be sized to the exact outer diameter of the deployed water quality sonde/sensor body).

# elec

### 1. SYSTEM ARCHITECTURE & CRITICAL DESIGN OVERRIDES

**CRITICAL OVERRIDE 1 (Energy Budget):** A 0.47F supercapacitor charged from 5.2V down to 3.4V yields **3.64 Joules** of usable energy ($E = 0.5 \cdot C \cdot (V_{max}^2 - V_{min}^2) \cdot \eta_{buck}$). A standard isolated DC-DC converter (e.g., TI DCP010505) draws 20mA quiescent current and will drain this capacitor in 45 seconds before a measurement occurs. 
*   **Solution:** The pH front-end and EC excitation will **not** use galvanic power isolation. Because the probe is floating (battery/supercap powered with no earth-ground reference), pseudo-isolation is achieved by powering the EC and pH rails sequentially via low-$R_{DS(on)}$ load switches. They are never powered simultaneously, eliminating cross-talk ground loops through the water.

**CRITICAL OVERRIDE 2 (Boot Brownout):** Connecting the TPS62A02 directly to the supercap will cause the ESP32-S3 to attempt booting at $V_{cap} = 2.5V$, resulting in a permanent brownout loop that stalls the turbine.
*   **Solution:** Added a nanopower voltage supervisor (TLV840) driving a Schmitt-trigger load switch to hold the buck converter `EN` pin LOW until the supercap hits 4.8V, latching it ON until the cap drops to 3.4V.

---

### 2. BLOCK-BY-BLOCK HARDWARE SPECIFICATION

#### BLOCK 1: Harvester & Rectifier
*   **Generator:** 3-Phase Brushless Gimbal Motor (e.g., T-Motor GB2208, rewound or native $K_v = 300\text{ RPM/V}$, $R_{phase} = 12\Omega$).
*   **Input Wiring:** 3x 24 AWG stranded PTFE wire (Alpha Wire 5854), 150mm length.
*   **Input Connector (Wet-Mate Bulkhead):** SubConn Micro Circular 3-pin (MCBH3F bulkhead, MCIL3M inline) or Potted Cable Gland (Lapp Skintop MS-M 12x1.5) with 3M Scotchcast 2131 resin.
*   **Board Connector (Internal):** JST PH 3-pin (B3B-PH-SM4-TB(LF)(SN)).
*   **3-Phase Bridge Rectifier:** 3x Nexperia **PMEG2010AEB** (Dual common-cathode/anode pair configured as 6-diode full bridge, or 6x individual SOD-523 diodes). $V_R = 20\text{V}$, $I_F = 1\text{A}$, $V_F = 270\text{mV}$ @ 100mA.

#### BLOCK 2: Shunt Regulator (5.2V Clamp)
*   **Reference:** Texas Instruments **TL431LIQDBZR** (SOT-23-3, $I_{min} = 0.4\text{mA}$, $V_{ref} = 2.495\text{V}$).
*   **Divider Network:** $R_{top} = 108\text{k}\Omega$ (Yageo RC0603FR-07108KL, 0.1%), $R_{bot} = 100\text{k}\Omega$ (Yageo RC0603FR-07100KL, 0.1%). Sets clamp to $2.495 \times (1 + 108/100) = 5.189\text{V}$.
*   **Pass Element:** Darlington PNP, ON Semi **MJD127T4G** (DPAK, $h_{FE} = 1000$, $I_C = 8\text{A}$). TL431 cathode pulls MJD127 base low via $1\text{k}\Omega$ 0603 resistor.
*   **Dump Resistor:** Bourns **PWR263S-20-3R30F** ($3.3\Omega$, 20W, D2PAK). Must be soldered to a $400\text{mm}^2$ 2oz copper pour stitched to the bottom ground plane with 24x 0.3mm thermal vias. Max continuous dissipation at 5.2V is 8.19W ($I_{dump} = 1.57\text{A}$).

#### BLOCK 3: Energy Storage & Hysteretic Undervoltage Lockout (UVLO)
*   **Supercapacitor:** Eaton **HV1020-2R7474-R** (Two 0.94F 2.7V caps in series) OR single Kyocera AVX **SCCR20B474SRB** configured for 5.5V, or **Eaton PHB-5R5474-R** (5.5V, 0.47F, ESR $= 0.3\Omega$, Lead spacing 5.0mm, THT). *Spec uses Eaton PHB-5R5474-R.*
*   **Balancing:** Active balancing IC, Advanced Linear Devices **ALD810025SCL** (SOIC-16, near-zero quiescent current MOSFET array balanced at 2.50V threshold per cell).
*   **Hysteretic Turn-On Supervisor:** Texas Instruments **TLV840MAPL46DBVR** (SOT-23-5, $I_Q = 120\text{nA}$, threshold 4.6V) + positive feedback resistor network ($R_{hys} = 4.7\text{M}\Omega$) to create a Turn-ON at 4.80V and Turn-OFF at 3.40V. Output drives TPS62A02 `EN` pin directly.

#### BLOCK 4: Primary Buck Converter (3.3V System Rail)
*   **Buck IC:** Texas Instruments **TPS62A02DRLR** (SOT-563, 2.4MHz, $I_Q = 20\mu\text{A}$).
*   **Inductor:** Murata **LQH2MPN1R0MGRL** ($1.0\mu\text{H}$, 2016 metric, $I_{sat} = 2.2\text{A}$, DCR $= 60\text{m}\Omega$).
*   **Input Capacitor:** Murata **GRM188R61A106KE69D** ($10\mu\text{F}$, 10V, X5R, 0603).
*   **Output Capacitor:** 2x Murata **GRM188R61A226ME15D** ($22\mu\text{F}$, 10V, X5R, 0603).
*   **Feedback Network:** $R_1 = 453\text{k}\Omega$ (0402, 1%), $R_2 = 100\text{k}\Omega$ (0402, 1%) for $V_{out} = 3.31\text{V}$ ($V_{FB} = 0.6\text{V}$).

#### BLOCK 5: Compute, Telemetry & Power Gating
*   **MCU:** Espressif **ESP32-S3-WROOM-1-N8** (8MB Flash, PCB Antenna disabled, external U.FL unused).
*   **LoRa Transceiver:** Semtech **SX1262IMLTRT** (QFN-24) or pre-certified module **Lambda62-868** / **Ebyte E22-900MM22S** (SX1262 + TCXO). Connected via SPI2 (`SCK`: GPIO12, `MOSI`: GPIO11, `MISO`: GPIO13, `CS`: GPIO10, `BUSY`: GPIO9, `DIO1`: GPIO8, `RST`: GPIO7).
*   **RF Connector:** Molex **0734120110** (U.FL) to bulkhead SMA-Female IP68 (Amphenol **901-10511-2**) via 100mm RG-178 coax.
*   **Sensor Power Gating (3x Load Switches):** Texas Instruments **TPS22916CNLH** (4-DSBGA, $I_Q = 10\text{nA}$, $R_{on} = 60\text{m}\Omega$).
    *   `SW1` (GPIO4): Powers I2C Bus, MS5837, NTC divider, and Turbidity LED/Photodiode.
    *   `SW2` (GPIO5): Powers pH AFE and pH ADC.
    *   `SW3` (GPIO6): Powers EC Excitation and EC AFE.

#### BLOCK 6: Sensor Suite & Analog Front-Ends (AFEs)

| Sensor | Interface | Part Numbers & Circuit Spec | Board Connector | Wiring |
| :--- | :--- | :--- | :--- | :--- |
| **Pressure/Temp** | I2C (`0x76`) | TE Connectivity **MS5837-30BA**. Mounted in O-ring gland on bulkhead. $10\text{k}\Omega$ 0402 pullups to `SW1_3V3` (`SDA`: GPIO1, `SCL`: GPIO2). | JST GH 4-pin (`BM04B-GHS-TBT`) | 28 AWG Silicone, 80mm |
| **NTC** | Analog (`ADC1_CH3`) | Vishay **NTCLE305E4103SB** ($10\text{k}\Omega$ @ 25°C, Stainless Steel housing). High-side $10\text{k}\Omega$ 0.1% resistor (Susumu **RG1608P-103-B-T5**) to `SW1_3V3`. | JST PH 2-pin (`B2B-PH-SM4-TB`) | 26 AWG PVC, twisted pair |
| **Turbidity** | Analog (`ADC1_CH4`) + GPIO | **TX:** Vishay **VSLY5850** (850nm IR LED) driven by ON Semi **MMBT3904** + $100\Omega$ resistor ($I_F = 20\text{mA}$) pulsed via GPIO14. **RX:** Vishay **BPW34** photodiode at 90° nephelometric angle. Transimpedance Amp: TI **OPA391DBVR** ($R_f = 100\text{k}\Omega$, $C_f = 15\text{pF}$). | JST PH 4-pin (`B4B-PH-SM4-TB`) | 26 AWG Shielded (Alpha Wire 2404C) |
| **pH (Time-Isolated)** | I2C (`0x48`) | **Probe:** Double-junction Ag/AgCl. **Buffer:** TI **LMP7721MA/NOPB** (SOIC-8, $I_B = 3\text{fA}$) in unity gain, guarded PCB trace ring. **Ref Bias:** TI **REF3020AIDBZR** (2.048V) divided to 1.024V virtual ground on pH BNC shield. **ADC:** TI **ADS1115IDGSR** (16-bit, differential mode between probe and 1.024V ref). Powered exclusively by `SW2_3V3`. | Amphenol **031-2367** (True 50$\Omega$ PCB BNC) | RG-174 Coax (Integral to pH probe) |
| **EC (Time-Isolated)** | Analog (`ADC1_CH5`) | **Probe:** $K=1.0$ 2-pole platinum. **Excitation:** ESP32 LEDC PWM (GPIO15) generating 2kHz square wave, AC-coupled via $1\mu\text{F}$ film cap (WIMA **MKS2C041001F00KSSD**), attenuated to $\pm 200\text{mV}$ via op-amp divider. **Transimpedance + Precision Rectifier:** Dual Op-Amp TI **OPA2391DGKR** converting cell current to DC voltage. Powered exclusively by `SW3_3V3`. | JST PH 2-pin (`B2B-PH-SM4-TB`) | 24 AWG coax (RG-316), 100mm |

---

### 3. POWER STATES, TIMING & ENERGY BUDGET

**Boundary Conditions:**
*   $C = 0.47\text{F}$ (Derated 15% for temp/aging $\rightarrow C_{eff} = 0.40\text{F}$).
*   $V_{turn\_on} = 4.80\text{V}$, $V_{cutoff} = 3.40\text{V}$.
*   Available Capacitor Energy: $E_{avail} = 0.5 \times 0.40\text{F} \times (4.80^2 - 3.40^2) = \mathbf{2.296\text{ Joules}}$.
*   Buck Converter Average Efficiency ($\eta$): **88%**.
*   Max Usable Load Energy at 3.3V Rail: $2.296\text{J} \times 0.88 = \mathbf{2.020\text{ Joules}}$ (or **612 mA·s** at 3.3V).

| State | Sub-State Description | Active Rails / Components | Current @ 3.3V | Duration | Energy @ 3.3V ($V \cdot I \cdot t$) | Cap $\Delta V$ Drop (Cumulative) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **0. CHARGE** | Supercap $V < 4.80\text{V}$. Buck disabled. | TLV840 + ALD810025 + Cap Leakage | $0\text{ mA}$ ($5\mu\text{A}$ @ $V_{cap}$) | Variable (River flow dependent) | $0\text{ mJ}$ | Charging up to 4.80V |
| **1. BOOT** | $V_{cap}$ hits 4.80V. TLV840 enables TPS62A02. ESP32-S3 ROM boot (Wi-Fi/BT disabled in eFuse/bootloader, 80MHz clock). | ESP32-S3 | $32.0\text{ mA}$ | $120\text{ ms}$ | $12.67\text{ mJ}$ | $4.79\text{ V}$ |
| **2. RUN_A** | Enable `SW1`. Read MS5837 (OSR 4096), sample NTC, pulse Turbidity IR LED & read ADC. Disable `SW1`. | ESP32-S3 (Light Sleep/ADC) + MS5837 + NTC + Turbidity | $38.0\text{ mA}$ | $50\text{ ms}$ | $6.27\text{ mJ}$ | $4.78\text{ V}$ |
| **3. RUN_B** | Enable `SW2`. Wait 350ms for LMP7721 guard ring & ADS1115 settling. Read pH differential. Disable `SW2`. | ESP32-S3 (Light Sleep) + LMP7721 + REF3020 + ADS1115 | $14.0\text{ mA}$ | $400\text{ ms}$ | $18.48\text{ mJ}$ | $4.76\text{ V}$ |
| **4. RUN_C** | Enable `SW3`. Drive 2kHz AC excitation for 50ms, sample rectified EC envelope, disable `SW3`. | ESP32-S3 (Active PWM/ADC) + OPA2391 | $28.0\text{ mA}$ | $60\text{ ms}$ | $5.54\text{ mJ}$ | $4.75\text{ V}$ |
| **5. TX_PREP**| Bit-pack payload (12 bytes), initialize SX1262 via SPI, calibrate TCXO. | ESP32-S3 + SX1262 (STDBY_XOSC) | $30.0\text{ mA}$ | $15\text{ ms}$ | $1.49\text{ mJ}$ | $4.75\text{ V}$ |
| **6. TX_RF** | SX1262 transmits 12-byte payload @ 868MHz, **SF9, BW125kHz, CR 4/5**, +22dBm output. ESP32 enters Deep Sleep. | ESP32-S3 (Deep Sleep) + SX1262 (TX +22dBm) | $118.0\text{ mA}$ | $165\text{ ms}$ | $64.25\text{ mJ}$ | $4.68\text{ V}$ |
| **7. KILL** | SX1262 `DIO1` (TX_DONE) wakes ESP32-S3 ULP/RTC GPIO to pulse a reset latch on the TLV840, OR system stays in Deep Sleep ($15\mu\text{A}$) until next RTC wake. *See Note below.* | ESP32-S3 (Deep Sleep) + SX1262 (Sleep) | $0.02\text{ mA}$ | Until next wake | Negligible | Holds at $4.68\text{ V}$ |
| **TOTAL** | **Single Measurement & Telemetry Cycle** | | | **810 ms** | **108.70 mJ** | **$\Delta V = -0.12\text{ V}$** |

*Note on State 7 (Continuous vs. Burst Operation):* Because a single cycle only consumes **108.7mJ** (5.3% of the supercap's usable energy), the supercap only drops from 4.80V to 4.68V (assuming zero turbine input during the 810ms window). The ESP32-S3 will enter Deep Sleep ($15\mu\text{A}$) and wake via its internal RTC timer every $N$ minutes. If the river stalls completely, the 0.47F cap can support **18 full measurement/TX cycles** before hitting the 3.40V hardware cutoff.

---

### 4. UNVERIFIED ASSUMPTIONS & FLAGS

1.  **Turbine Hydrodynamic Threshold (FLAG - CRITICAL):** A $300\text{ RPM/V}$ BLDC requires $300 \times (4.8\text{V} + 0.54\text{V}_{diode}) = \mathbf{1602\text{ RPM}}$ just to overcome the supercap voltage at peak charge and start trickling current. In a typical river flow of $1.0\text{ m/s}$, achieving 1602 RPM directly requires a micro-propeller with a pitch diameter under 25mm, which has terrible starting torque and will foul instantly with algae/silt. **You almost certainly need a lower $K_v$ motor ($30\text{–}50\text{ RPM/V}$) or an active boost-MPPT rectifier (e.g., BQ25570) instead of a passive Schottky bridge.**
2.  **LoRa Spreading Factor (FLAG):** The energy budget assumes **SF9 / BW125** ($165\text{ms}$ Time-on-Air for 12 bytes). If the river probe is in a deep gorge requiring **SF12 / BW125**, Time-on-Air jumps to **$1.318\text{ seconds}$**, increasing State 6 energy from $64.25\text{mJ}$ to **$513.2\text{mJ}$**. The 0.47F supercap will still survive this (dropping from 4.80V to 4.21V in one shot), provided the supercap ESR is $<0.5\Omega$.
3.  **Supercapacitor ESR IR-Drop (FLAG):** During the 118mA @ 3.3V TX spike, the buck converter pulls $\sim 125\text{mA}$ from the supercap (at $V_{cap} = 3.5\text{V}$ worst-case). If using a cheap coin-cell style 0.47F supercap (ESR $\approx 30\Omega$), $V_{cap}$ will instantly sag by $3.75\text{V}$ and brown out the system. You **must** use a cylindrical wound power supercap (like the specified Eaton PHB series, ESR $= 0.3\Omega$).
4.  **pH Probe Wet-Storage & Stabilization Time (FLAG):** The $400\text{ms}$ duration in State 3 assumes the pH glass bulb is continuously submerged and hydrated, and only the electronics (LMP7721) are power-cycled. If the LMP7721 input bias current charges the pH probe capacitance during turn-on, $350\text{ms}$ may yield a $\pm 0.2\text{ pH}$ settling error. Bench verification with the exact probe impedance ($50\text{M}\Omega\text{–}500\text{M}\Omega$) is required; if settling takes $>2\text{ seconds}$, leave the LMP7721 permanently powered ($1.1\text{mA}$ continuous draw) and only gate the ADS1115.
5.  **RF Propagation Underwater (FLAG):** 868MHz will not penetrate more than a few centimeters of fresh water. This architecture assumes the LoRa antenna is housed in a surface buoy connected via umbilical, or the probe body breaches the water surface.

# cal

### 1. Mechanical & Enclosure Integrity: Vacuum-Submerge Test

**Equipment:**
*   Bel-Art F42025-0000 Polycarbonate Vacuum Desiccator (or equivalent 10 L chamber).
*   Single-stage rotary vane pump (e.g., Robinair 15115) with inline glycerin-filled Bourdon gauge (0 to -100 kPa).
*   Deionized (DI) water bath with 0.1% surfactant (Triton X-100) to break surface tension.
*   M12x1.5 threaded brass test plug with Viton O-ring (replacing the MS5837 port if testing shell only, otherwise test fully populated pod).

**Procedure:**
1.  Assemble the 3D-printed pod with all penetrators, O-rings (lubricated with Dow Corning Molykote 111), and desiccant packs (2x 5g silica gel with cobalt chloride indicator) inside. Torque axial compression screws to 1.2 Nm using a calibrated driver (Wiha 28506).
2.  Submerge the pod in the surfactant-treated water bath inside the vacuum chamber, weighting it down with a 1 kg stainless V-block so the highest point of the pod is $\ge 50\text{ mm}$ below the waterline.
3.  Pull vacuum to $-85\text{ kPa}$ gauge ($16.3\text{ kPa}$ absolute) at a rate not exceeding $10\text{ kPa/s}$.
4.  Hold vacuum for $30\text{ minutes}$. Observe continuously for the first $5\text{ minutes}$ to distinguish surface-trapped air from active internal leaks.
5.  Vent chamber back to atmospheric pressure over $60\text{ seconds}$ (this drives water *into* the pod if the internal pressure dropped via air evacuation).
6.  Leave pod submerged at $0\text{ kPa}$ gauge for an additional $30\text{ minutes}$.
7.  Remove, dry exterior with compressed air, open pod, and weigh internal components/desiccant on a $0.01\text{ g}$ precision balance (Ohaus Scout SPX222).

*   **Duration:** $75\text{ minutes}$.
*   **Acceptance Criteria:** Zero continuous bubble streams (defined as $>1\text{ bubble every } 10\text{ seconds}$ from the same nucleation site after $t = 5\text{ min}$). Desiccant indicator remains blue; mass gain of desiccant $< 0.05\text{ g}$.
*   **Failure Modes Caught:** Inter-layer delamination in FDM/SLA print walls, micro-porosity around brass heat-set inserts, rolled or pinched radial O-rings, weeping through sensor cable potting compounds (Loctite E-120HP / Marine Epoxy).

---

### 2. Flow Drive Train: Bench Back-EMF Cogging & Mag-Coupling Slip Jig

**Equipment:**
*   Tektronix TBS1052B-EDU Oscilloscope (or equivalent 2-ch DSO).
*   Maxon 110049 DC motor (or precision variable-speed drill press) coupled to a $10\text{ N}\cdot\text{cm}$ rotary torque sensor (FUTEK TRS605) or dead-weight string spool (radius $r = 15.0\text{ mm}$).
*   3D-printed alignment jig holding the external turbine rotor, the $2.5\text{ mm}$ dry-wall barrier (simulating the pod hull thickness), and the internal Hall/coil pickup assembly.

#### Part A: Back-EMF & Cogging Torque Measurement
**Procedure:**
1.  Mount the internal follower assembly and external driver rotor into the test jig with a nominal axial air gap of $3.00\text{ mm} \pm 0.10\text{ mm}$ across the polymer wall.
2.  Connect oscilloscope Ch1 directly across the internal pickup coil terminals (disconnect pull-ups if using a raw variable-reluctance coil; if using a latching Hall sensor like US1881, probe the raw collector before the Schmitt trigger, or swap in a linear Hall sensor SS49E at the exact stator pole position).
3.  Drive the external rotor at exactly $60.0\text{ RPM}$ ($1.00\text{ Hz}$ mechanical) using the external reference motor.
4.  Record peak-to-peak voltage ($V_{pp}$), frequency, and duty cycle jitter over 100 revolutions.
5.  Remove the external drive motor. Attach a $1.5\text{ g}$ mass to a monofilament line wound around the $r = 15.0\text{ mm}$ rotor hub (applying $2.21\times 10^{-4}\text{ N}\cdot\text{m}$ static torque). Release rotor from 12 distinct angular positions ($30^\circ$ increments).

*   **Duration:** $25\text{ minutes}$.
*   **Acceptance Criteria:** 
    *   Back-EMF / Linear Hall sinusoid $V_{pp}$ variation across pole pairs $< 8\%$ (indicates concentric magnet array).
    *   Pulse-to-pulse period jitter at $60\text{ RPM} < 3\%$.
    *   Rotor must break away and rotate continuously from all 12 angular positions under the $1.5\text{ g}$ dead-weight test (verifies minimum startup flow velocity $< 0.08\text{ m/s}$).
*   **Failure Modes Caught:** Eccentricity in rotor shaft printing, axially Cocked NdFeB magnets in the rotor carrier, excessive magnetic cogging against internal stator iron/shielding, ceramic bearing brinelling or contamination.

#### Part B: Mag-Coupling Breakaway (Slip) Jig
**Procedure:**
1.  Lock the internal follower shaft mechanically using a set-screw collar.
2.  Couple the external rotor to the FUTEK torque watch (or wrap monofilament line around the $r = 15.0\text{ mm}$ hub and pull vertically using a Shimpo FGE-2X digital force gauge).
3.  Slowly ramp rotational torque at $< 0.1\text{ N}\cdot\text{cm/s}$ until the magnetic coupling poles slip past the first detente. Record peak breakaway torque ($\tau_{\text{slip}}$).
4.  Unlock the internal shaft, submerge the wet-side rotor in a bucket of water seeded with $2\text{ g/L}$ bentonite clay and $5\text{ mm}$ pine needles, and spin external rotor at $1200\text{ RPM}$ (simulating $3.5\text{ m/s}$ flood surge) for $5\text{ minutes}$.

*   **Duration:** $15\text{ minutes}$.
*   **Acceptance Criteria:** $\tau_{\text{slip}} \ge 1.8\text{ N}\cdot\text{cm}$ ($1.2\text{ N}$ pull force at $r=15\text{ mm}$). Zero pole-slipping events during the $1200\text{ RPM}$ slurry spin up (acceleration ramp $0\text{ to } 1200\text{ RPM}$ in $0.5\text{ s}$).
*   **Failure Modes Caught:** Incorrect magnet polarity orientation during glue-up (N-N instead of N-S pairing), degraded magnet flux from overheating during epoxy cure ($>80^\circ\text{C}$ for N42 grade), excessive hull floor thickness in the print slice exceeding the $3.0\text{ mm}$ design budget.

---

### 3. Temperature Subsystem: NTC & DS18B20 Cross-Calibration

**Equipment:**
*   Julabo CORIO CD-BC4 refrigerated/heating circulator bath filled with 50/50 ethylene glycol/water.
*   Fluke 1504 Tweener Thermometer read-out with a 5615-6 Secondary Reference PRT ($\pm 0.012^\circ\text{C}$ accuracy).
*   Rigol DM3058E 5.5-digit DMM.

**Procedure:**
1.  Bundle the probe's waterproof DS18B20 (stainless tube), the epoxy-potted NTC ($10\text{ k}\Omega$, $\beta = 3950\text{ K}$), and the Fluke PRT tip together using Kapton tape so sensing elements are within a $10\text{ mm}$ sphere. Submerge $100\text{ mm}$ deep in the stirred bath.
2.  Step bath through 4 setpoints: $2.00^\circ\text{C}$, $10.00^\circ\text{C}$, $20.00^\circ\text{C}$, and $30.00^\circ\text{C}$.
3.  Hold at each plateau for $12\text{ minutes}$ until PRT drift is $< 0.01^\circ\text{C/min}$.
4.  Log 60 samples ($1\text{ Hz}$) from the probe telemetry (NTC ADC raw counts + calculated Steinhart-Hart temp, and DS18B20 12-bit hex output).
5.  Perform a sudden step-change test: move sensors from room air ($22^\circ\text{C}$) directly into the $2.00^\circ\text{C}$ stirred bath and log at $10\text{ Hz}$ for NTC and $1.3\text{ Hz}$ (max conversion rate) for DS18B20 to measure $\tau_{63.2\%}$.

*   **Duration:** $60\text{ minutes}$.
*   **Acceptance Criteria:**
    *   NTC derived temperature within $\pm 0.15^\circ\text{C}$ of PRT across all 4 points after 3-point Steinhart-Hart coefficient fitting ($A, B, C$).
    *   DS18B20 within $\pm 0.4^\circ\text{C}$ of PRT (must verify it is not a counterfeit chip exhibiting $\pm 2^\circ\text{C}$ offset or locked $12\text{-bit}$ resolution bits).
    *   Thermal time constant $\tau_{63.2\%} \le 8.0\text{ s}$ for NTC, $\le 25.0\text{ s}$ for DS18B20.
    *   Difference $|T_{\text{NTC}} - T_{\text{DS18B20}}| \le 0.3^\circ\text{C}$ at steady state.
*   **Failure Modes Caught:** Counterfeit Maxim DS18B20 clones (fail high-res conversion or lack parasitic power robustness), self-heating of the NTC due to excessive bias current (if pull-up $< 10\text{ k}\Omega$ at $3.3\text{V}$ continuous), air voids inside the thermal potting compound inside the sensor tip.

---

### 4. pH Subsystem: PH-4502C Front-End & Temp-Comp Validation

**Equipment:**
*   BNC Shorting Cap and Precision Voltage Source (Calibrator: Fluke 715 or ADR4525 + $10\text{ k}\Omega$ 10-turn Bourns pot monitored by 5.5-digit DMM).
*   NIST-traceable pH Buffers: Oakton pH $4.01$, $7.00$, and $10.01$ ($\pm 0.01\text{ pH}$ at $25^\circ\text{C}$).
*   Two water baths set to $5.0^\circ\text{C}$ and $25.0^\circ\text{C}$.

**Procedure:**
1.  **Electrical Trim (PH-4502C):** Attach BNC shorting cap ($0.000\text{ V}$ input). Power board with regulated $5.00\text{ V}$ (or target rail). Adjust the `PO` (offset) multi-turn trimmer (Blue Bourns 3296W closest to BNC) until the `Po` analog output pin reads exactly $2.500\text{ V} \pm 0.005\text{ V}$ on the DMM.
2.  **Gain Verification:** Remove shorting cap. Inject $+177.4\text{ mV}$ (simulating $\text{pH } 4.00$ at $25^\circ\text{C}$) and $-177.4\text{ mV}$ ($\text{pH } 10.00$) via BNC adapter. Verify `Po` pin swings symmetrically with a gain of $G = -3.046\text{ V/V}$ (delivering the target $0.180\text{ V/pH}$ slope: $\Delta V / \Delta \text{pH} = 0.05916\text{ V} \times 3.046 = 0.1802\text{ V/pH}$).
3.  **Input Bias / Leakage Check:** Connect the $+177.4\text{ mV}$ source through a $100\text{ M}\Omega$ glass-encapsulated resistor (Ohmite MOX-200001006FE) in series with the BNC center pin. Measure voltage drop at `Po`.
4.  **Wet 3-Point Calibration ($25^\circ\text{C}$):** Connect glass electrode. Rinse with DI water, blot dry with Kimwipes (do not rub—creates triboelectric charge). Submerge electrode and DS18B20 in pH $7.00$, $4.01$, and $10.01$ buffers equilibrated at $25.0^\circ\text{C}$. Wait $90\text{ s}$ per buffer. Record ADC voltage.
5.  **Nernstian Temp-Comp Verification ($5^\circ\text{C}$):** Transfer both pH electrode and DS18B20 into pH $4.01$ and pH $10.01$ buffers chilled to $5.0^\circ\text{C}$ (where true buffer values are $4.00$ and $10.25$ respectively, and physical electrode slope drops from $59.16\text{ mV/pH}$ to $55.19\text{ mV/pH}$). Verify firmware applies:
    $$\text{pH}_{\text{comp}} = 7.00 + \frac{(V_{\text{meas}} - V_{\text{pH7}})}{0.180 \times \left(\frac{T_{\text{DS18B20}} + 273.15}{298.15}\right)}$$

*   **Duration:** $45\text{ minutes}$.
*   **Acceptance Criteria:**
    *   Series $100\text{ M}\Omega$ insertion shift at `Po` $\le 15\text{ mV}$ (proves TL072/TLC4502 input bias current + PCB flux leakage $< 50\text{ pA}$).
    *   Wet electrode asymmetry potential (at pH $7.00$) within $\pm 15\text{ mV}$ of the shorted-BNC $2.500\text{ V}$ baseline ($\pm 45\text{ mV}$ at `Po`).
    *   Calculated slope efficiency between $95\%$ and $102\%$ of theoretical ($0.171\text{ to } 0.184\text{ V/pH}$ at $25^\circ\text{C}$).
    *   $95\%$ response time ($t_{95}$) when switching from pH $7.00$ to $4.01 < 15\text{ seconds}$.
    *   $5.0^\circ\text{C}$ temperature-compensated reading within $\pm 0.08\text{ pH}$ of the buffer's $5^\circ\text{C}$ NIST table value.
*   **Failure Modes Caught:** Hygroscopic no-clean solder flux residue around the BNC footprint on the PH-4502C board (shunts high-Z glass bulb), cracked glass bulb (causes slope to approach $0\text{ V/pH}$), poisoned/depleted Ag/AgCl reference gel (causes $>30\text{ mV}$ offset at pH 7), dehydrated glass hydrated layer (slow $t_{95} > 45\text{ s}$), firmware sign inversion on the DS18B20 Nernstian temperature compensation term.

---

### 5. Electrical Conductivity (EC): Cell Constant ($K$) & Ground Loop Isolation

**Equipment:**
*   Potassium Chloride (KCl) conductivity standards: $84\ \mu\text{S/cm}$, $1413\ \mu\text{S/cm}$, and $12,880\ \mu\text{S/cm}$ at $25^\circ\text{C}$ (Hanna Instruments HI7033, HI7031, HI7030).
*   Precision axial metal-film resistors ($0.1\%$, $15\text{ ppm}$): $100\ \Omega$, $1.00\text{ k}\Omega$, $10.0\text{ k}\Omega$.

**Procedure:**
1.  **Dry Dummy Load Check:** Before wetting electrodes, clip precision resistors across the EC probe pins. Record excitation frequency ($f_{\text{exc}}$ on scope, must be $1\text{ kHz to } 10\text{ kHz}$ AC with $<10\text{ mV}$ DC offset) and ADC conductance readings.
2.  **Wet Calibration ($25.0^\circ\text{C}$):** Submerge EC cell in $84$, $1413$, and $12,880\ \mu\text{S/cm}$ standards in a tall glass beaker, keeping the probe tip $\ge 30\text{ mm}$ away from beaker walls and bottom to prevent fringe-field compression. Shake probe vigorously to dislodge trapped air bubbles in the shroud.
3.  Compute cell constant $K = G_{\text{meas}} / \sigma_{\text{std}}\ [\text{cm}^{-1}]$ at each concentration.
4.  **Cross-Talk / Ground Loop Check:** Place both the EC probe and the pH probe simultaneously into the $1413\ \mu\text{S/cm}$ solution. Log pH output with the EC excitation circuit turned ON, then toggle EC power/excitation OFF via GPIO.

*   **Duration:** $30\text{ minutes}$.
*   **Acceptance Criteria:**
    *   DC offset across EC electrodes $< 10\text{ mV}$ (prevents electrolysis and platinum black stripping).
    *   Cell constant $K$ linearity across the $84\text{ to } 1413\ \mu\text{S/cm}$ river range within $\pm 3.0\%$.
    *   pH reading shift when EC excitation toggles ON/OFF in the same beaker $\le 0.03\text{ pH}$ ($\le 5.4\text{ mV}$ at `Po`).
*   **Failure Modes Caught:** Missing galvanic isolation or shared return path between EC AC drive and pH single-ended reference junction, electrode polarization (if $f_{\text{exc}}$ is too low at $12,880\ \mu\text{S/cm}$, $K$ will artificially spike), air bubble entrapment inside the EC flow-through slots.

---

### 6. Turbidity: Formazin Calibration & Stray-Light Rejection

**Equipment:**
*   StablCal Stabilized Formazin Turbidity Standards: $<0.1\text{ NTU}$ (DI water filtered through $0.2\ \mu\text{m}$ PES syringe filter), $20\text{ NTU}$, $100\text{ NTU}$, and $800\text{ NTU}$ (Hach 2660153, 2660542).
*   Matte black anodized aluminum or flat-black painted 1 L calibration vessel (non-reflective walls).
*   Halogen or high-CRI LED work light ($50,000\text{ Lux}$ at $150\text{ mm}$ distance, verified by Extech LT300).

**Procedure:**
1.  Degass all standards in an ultrasonic bath for $2\text{ minutes}$ (except $800\text{ NTU}$, invert gently 10 times to resuspend without creating microbubbles).
2.  Submerge turbidity optical head $60\text{ mm}$ deep in the black vessel, with $\ge 50\text{ mm}$ clearance in the forward $90^\circ$ optical cone.
3.  Record photodetector voltage/ADC counts at $0, 20, 100,$ and $800\text{ NTU}$ in dark ambient conditions ($< 5\text{ Lux}$).
4.  **Ambient Light Rejection Test:** While submerged in the $20\text{ NTU}$ standard, shine the $50,000\text{ Lux}$ broadband lamp directly onto the water surface at a $45^\circ$ angle aimed at the optical window.

*   **Duration:** $30\text{ minutes}$.
*   **Acceptance Criteria:**
    *   Monotonic response curve; $R^2 \ge 0.995$ on 2nd-order polynomial fit from $0\text{ to } 800\text{ NTU}$.
    *   Dark noise floor (in $0\text{ NTU}$) standard deviation over 60 samples $\le 0.3\text{ NTU}$ equivalent.
    *   Reading shift under $50,000\text{ Lux}$ solar-simulating illumination $\le 1.5\text{ NTU}$ (if using modulated $850\text{ nm}$ IR with synchronous demodulation) or $\le 5.0\text{ NTU}$ (if using optical daylight-blocking filter + shroud).
*   **Failure Modes Caught:** Unmodulated DC IR emitter saturating the phototransistor in shallow sunlit riffles, internal optical cross-talk (IR light piping directly from LED to photodiode through clear epoxy or translucent 3D-printed housing walls—shows up as an abnormally high $0\text{ NTU}$ baseline voltage), micro-scratches on the acrylic optical window.

---

### 7. Depth Subsystem: MS5837-30BA / -02BA Hydrostatic & Barometric Tare

**Equipment:**
*   Vaisala PTB330 Class A Digital Barometer (or calibrated BME280 reference bench unit).
*   Clear PVC standpipe: $100\text{ mm}$ ID, $2.50\text{ m}$ vertical height, with a laser-engraved steel tape rule ($\pm 0.5\text{ mm}$) bonded to the exterior wall.

**Procedure:**
1.  **Dry Barometric Tare:** With the probe in dry room air, log MS5837 pressure ($P_{\text{dry}}$) and internal temperature ($T_{\text{MS}}$) at $OSR = 4096$ for $5\text{ minutes}$ alongside the reference barometer ($P_{\text{ref}}$). Compute static zero-offset $\Delta P_0 = P_{\text{dry}} - P_{\text{ref}}$.
2.  **Hydrostatic Standpipe Test:** Fill the $2.5\text{ m}$ column with tap water equilibrated to room temperature ($20.0^\circ\text{C}$, $\rho = 998.2\text{ kg/m}^3$).
3.  Lower the probe using a braided Kevlar line (non-stretch) so the MS5837 white gel ceramic port is positioned at depths $h = 0.250\text{ m}, 0.500\text{ m}, 1.000\text{ m}, 1.500\text{ m},$ and $2.000\text{ m}$ below the meniscus.
4.  At each depth, hold for $2\text{ minutes}$ and log 30 samples. Calculate depth:
    $$h_{\text{calc}} = \frac{(P_{\text{meas}} - \Delta P_0 - P_{\text{baro\_live}}) \times 100}{\rho(T_{\text{NTC}}) \cdot g}$$
    *(where $P$ is in $\text{mbar}$, $g = 9.809\text{ m/s}^2$ for Central Europe / Slovakia latitude $48^\circ\text{N}$)*.

*   **Duration:** $40\text{ minutes}$.
*   **Acceptance Criteria:**
    *   Dry barometric offset $|\Delta P_0| \le 2.0\text{ mbar}$ (for MS5837-02BA) or $\le 50\text{ mbar}$ (for MS5837-30BA).
    *   Peak-to-peak RMS noise at $h = 1.000\text{ m}$ (OSR 4096) $\le 0.2\text{ mbar}$ ($\sim 2.0\text{ mm H}_2\text{O}$ for -02BA) or $\le 2.5\text{ mbar}$ ($\sim 25\text{ mm H}_2\text{O}$ for -30BA).
    *   Linearity error across the $0.25\text{ m to } 2.00\text{ m}$ column $\le \pm 5\text{ mm}$ (-02BA) or $\le \pm 20\text{ mm}$ (-30BA).
*   **Failure Modes Caught:** Corrupted PROM CRC-4 factory calibration words C1–C6 over the $\text{I}^2\text{C}$ bus, mechanical stress induced on the ceramic sensor package by over-tightening the face-seal cap or swelling of an incompatible O-ring, air bubble trapped inside the protective mud-guard cap over the dielectric gel (causes nonlinear Boyles-law compression error at shallow depths), failure to account for local atmospheric pressure drift in an unvented absolute gauge.

---

### 8. Field Validation: River A/B Co-Location Against SHMÚ Reference Gauge

**Site & Equipment:**
*   Active SHMÚ (Slovenský hydrometeorologický ústav) automated hydrological station equipped with a radar/pressure water stage recorder (e.g., OTT PLS / Vegapuls WL 61) and calibrated discharge rating curve $Q = f(H)$.
*   Portable reference multiparameter sonde for spot verification: YSI ProDSS or WTW Multi 3630 IDS (freshly calibrated that morning).
*   Handheld acoustic Doppler velocimeter (SonTek FlowTracker2) or OTT C2 hydrometric current meter on a wading rod.
*   Stainless steel perforated stilling pipe ($150\text{ mm}$ ID) or concrete bridge pier mounting bracket.

**Procedure:**
1.  **Installation & Datum Survey:** Mount the river probe at the SHMÚ station cross-section, positioned at the exact same hydraulic transect as the SHMÚ orifice/radar footprint, submerged $\ge 0.30\text{ m}$ below the minimum expected stage and $\ge 0.20\text{ m}$ above the bed to avoid bedload gravel impact.
2.  Using a surveyor's optical level (Leica NA720) and staff, measure the vertical elevation offset ($\Delta Z_{\text{datum}}$) between the SHMÚ "0" staff gauge plate (vodočetná lata) and the MS5837 sensor diaphragm to $\pm 2\text{ mm}$.
3.  **Atmospheric Reference:** Place the local barometric reference logger (inside the dry shore telemetry box) in the shade at the station to continuously subtract $P_{\text{baro}}(t)$ from the submerged MS5837 absolute pressure.
4.  **Velocity Transfer Function Calibration:** Use the FlowTracker2 / OTT C2 positioned $100\text{ mm}$ laterally from the probe's rotor to measure true point velocity $v_{\text{ref}}$ ($\text{m/s}$) averaged over $60\text{ seconds}$ at 3 distinct vertical or lateral flow regimes during deployment. Map rotor frequency $f_{\text{RPM}}$ to linear velocity: $v = a \cdot f_{\text{RPM}} + b$.
5.  **72-Hour Continuous Co-Location:** Log all parameters at $1\text{-minute}$ intervals, synchronized via NTP/GNSS to match SHMÚ's $15\text{-minute}$ synoptic reporting timestamps ($:00, :15, :30, :45$).
6.  **Spot Water Quality Audits:** At $t = 0\text{ h}, 24\text{ h},$ and $72\text{ h}$, submerge the YSI/WTW reference sonde directly beside the probe intake for $15\text{ minutes}$ (logging at $1\text{ min}$) to capture diurnal temperature, pH, EC, and turbidity swings.

*   **Duration:** $72\text{ hours}$ continuous ($3\text{ hours}$ active on-site labor).
*   **Acceptance Criteria (Probe vs. SHMÚ & YSI Reference):**
    *   **Water Stage ($H$):** RMSE against SHMÚ stage record $\le 10\text{ mm}$ (for -02BA) or $\le 25\text{ mm}$ (for -30BA) over $72\text{ h}$; zero phase lag during diurnal snowmelt or hydro-peaking waves.
    *   **Water Temperature:** $|\Delta T| \le 0.20^\circ\text{C}$ against SHMÚ PT100 / YSI reference across the full diurnal cycle.
    *   **Flow Velocity ($v$):** Within $\pm 5\%$ or $\pm 0.03\text{ m/s}$ (whichever is greater) of FlowTracker2 point velocity at $t = 0\text{ h}$ and $t = 72\text{ h}$.
    *   **pH:** $|\Delta\text{pH}| \le 0.15\text{ pH}$ against YSI reference at $t = 0\text{ h}$ and $t = 72\text{ h}$.
    *   **EC (Temp-compensated to $25^\circ\text{C}$):** Within $\pm 5\%$ of YSI reference.
    *   **Turbidity:** Within $\pm 10\%$ or $\pm 2\text{ NTU}$ of YSI reference.
*   **Failure Modes Caught:**
    *   **Bernoulli Drawdown Error:** High river velocity ($>1.5\text{ m/s}$) sweeping directly across an unbaffled MS5837 port creates a dynamic pressure drop ($\Delta P = -\frac{1}{2}\rho v^2$), making the river level appear artificially low during flood surges compared to the SHMÚ radar gauge.
    *   **Streaming Potential on pH:** Low-ionic-strength mountain river water ($< 100\ \mu\text{S/cm}$) flowing rapidly past an unshielded pH reference junction induces a velocity-dependent electrokinetic voltage offset (shows up as pH varying with rotor RPM).
    *   **Biofouling & Filamentous Algae:** Diatom slime coating the turbidity optics (causes steady upward baseline creep over 72h) or Cladophora strands wrapping around the rotor hub spindle (causes step-drop in RPM vs. SHMÚ stage-derived velocity).
    *   **Solar Thermal Barometric Drift:** If the shore-side barometer heats up in direct sun without proper temperature compensation, the calculated water level will exhibit a false $1\text{ to } 3\text{ cm}$ diurnal sine wave at $14:00$ local time that is absent in the SHMÚ radar trace.

---

### Summary Sign-Off Matrix

| Step | Test Name | Duration | Critical Pass Limit | Primary Failure Mode Caught |
| :--- | :--- | :--- | :--- | :--- |
| **1** | Vacuum-Submerge ($-85\text{ kPa}$) | $75\text{ min}$ | $0\text{ bubbles}$, $\Delta m < 0.05\text{ g}$ | Layer delamination, O-ring pinch, epoxy weep |
| **2A** | Back-EMF & Cogging | $25\text{ min}$ | $V_{pp}\text{ var} < 8\%$, start $\le 1.5\text{ g}$ | Eccentric rotor, cocked magnets, bearing drag |
| **2B** | Mag-Coupling Slip Jig | $15\text{ min}$ | $\tau_{\text{slip}} \ge 1.8\text{ N}\cdot\text{cm}$ | Flipped magnet pole, thick hull floor, heat demag |
| **3** | NTC & DS18B20 Bath | $60\text{ min}$ | $\pm 0.15^\circ\text{C}$ (NTC), $\tau \le 8\text{ s}$ | Fake DS18B20, NTC self-heating, potting air void |
| **4** | PH-4502C & Nernst Comp | $45\text{ min}$ | $\Delta V_{100\text{M}\Omega} \le 15\text{ mV}$, $\pm 0.08\text{ pH}$ | PCB flux leakage, cracked bulb, bad temp-comp math |
| **5** | EC Cell $K$ & Isolation | $30\text{ min}$ | $K \pm 3\%$, $\Delta\text{pH}_{\text{EC}} \le 0.03$ | Ground loop into pH ref, electrode polarization |
| **6** | Turbidity Formazin & Sun | $30\text{ min}$ | $R^2 \ge 0.995$, $\Delta_{50\text{kLux}} \le 1.5\text{ NTU}$ | DC sunlight saturation, internal wall light-piping |
| **7** | MS5837 Standpipe | $40\text{ min}$ | $\text{Err} \le 5\text{ mm}$ (-02BA) / $20\text{ mm}$ (-30BA) | Gel bubble, O-ring package stress, bad CRC/PROM |
| **8** | SHMÚ 72h River A/B | $72\text{ hr}$ | Stage $\text{RMSE} \le 10\text{ mm}$, $v \pm 5\%$ | Bernoulli drawdown, streaming pH offset, fouling |

# risk

| ID | Failure Mode | Trigger | Detectable-By | Consequence Severity (1-5) | Likelihood (1-5) | Mitigation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RR-01** | **Bearing fouling** (Turbine rotor seizure) | Silt ingress (>50 µm suspended solids) and calcium carbonate scaling inside raceways. | Rotor RPM drops to 0 while baseline acoustic/ADCP flow velocity > 0.5 m/s. | 4 | 4 | Replace steel bearings with Igus Iglidur J polymer plain bearings (PN: JFM-0810-10) running on a hard-anodized 316L shaft; machine a 1.5 mm radial labyrinth purge gap flushed by bypass flow. |
| **RR-02** | **Algae film on optics** (Turbidity/fluorometer blinding) | Biofilm growth driven by euphotic zone deployment (<1.5 m depth) and water temps >15°C. | Gradual asymptotic saturation of backscatter ADC counts over a 72-hour rolling window; loss of diurnal variance. | 3 | 5 | Install a recessed sapphire optical window (Edmund Optics PN: 43-630) surrounded by a sintered CuNi 90/10 anti-fouling guard ring; integrate a 6 RPM mechanical EPDM wiper actuated by a 6V micro-gearhead motor (Pololu PN: 2366) wiping 1x/hour. |
| **RR-03** | **Leaf jam at weed guard** (Flow occlusion) | Autumnal leaf fall and fibrous macro-debris mat accumulation during high-stage events. | Sudden step-drop in rotor RPM (>40% drop in <5 minutes) uncorrelated with hydrograph stage drop. | 3 | 4 | Fabricate a swept-back 35° wedge-wire screen (316L, 4 mm bar spacing) oriented parallel to the thalweg; eliminate all leading-edge fasteners using full-penetration TIG welds ground flush to 32 Ra. |
| **RR-04** | **Mag-cup slip in surge** (Magnetic coupling decoupling) | Flash flood surge velocities >3.5 m/s exceeding breakaway torque of the wet-to-dry magnetic coupling. | Hall-effect sensor on dry side reads 0 RPM while wet-side index magnet accelerometer registers high-frequency vibration. | 4 | 3 | Upgrade to a 6-pole radially magnetized NdFeB N52 coupling (K&J Magnetics custom ring array, 1.8 Nm breakaway torque at 3.0 mm wall gap); add a 40° mechanical spring-loaded relief vane ahead of the rotor to spill flow >3.0 m/s. |
| **RR-05** | **Supercap aging** (Loss of hold-up capacitance / high ESR) | Thermal cycling (-10°C to +45°C) and continuous float voltage stress over >18 months. | Coulomb counter (TI BQ35100) measures >1.2V voltage droop during the 150 mA LoRa/cellular TX burst. | 4 | 3 | Use LIC (Lithium-Ion Capacitor, Eaton XLR-4R0507, 500F) instead of standard EDLC; derate charge voltage from 3.8V to 3.55V via hardware resistor divider on the buck-boost charger (Analog Devices LT8491). |
| **RR-06** | **Condensation in sealed pod** (PCB corrosion / short circuit) | Moisture permeation through dynamic/static elastomer seals followed by rapid night-time river cooling. | Internal onboard BME280 sensor registers Relative Humidity >65% or calculated dew point margin <2°C. | 5 | 3 | Double O-ring piston/face seals (Parker 2-228, 70A Durometer FKM) greased with Dow Corning Molykote 111; vacuum-bake internal assembly at 60°C for 4 hours, purge with dry Nitrogen (Grade 4.8) via Schrader valve, and clamp in 2x 10g molecular sieve desiccant packs (Clariant Desi Pak). |
| **RR-07** | **Vandalism** (Theft, cable severing, ballistic impact) | Exposed visual profile near public boat ramps, bridges, or fishing access points. | Accelerometer shock interrupt (>8g on ADXL345) followed by immediate loss of telemetry and GPS geofence exit. | 5 | 2 | Submerge pod 0.5 m below low-water datum painted matte river-bed olive (RAL 6003); armor tether in 1/2" Schedule 80 316L conduit anchored to bank with Hilti HIT-RE 500 V3 epoxy and tamper-proof Penta-head nuts (McMaster PN: 91802A230). |
| **RR-08** | **Ice** (Crushing or anchor shearing via frazil/surface ice) | Sub-zero ambient air temperatures (<0°C) combined with supercooled turbulent flow or spring ice-out. | Water temperature thermistor reads ≤0.1°C concurrent with strain gauge overload on the mounting strut. | 5 | 2 | Mount deployment frame below historical maximum ice-keel depth (minimum 1.2 m below surface) behind a 6 mm thick AR400 steel angled ice-deflector nose cone bolted to the concrete bridge pier. |
| **RR-09** | **Arm flutter fatigue** (Cantilever strut weld fracture) | Kármán vortex shedding locking into the structural natural frequency (~12–18 Hz) at 1.5–2.5 m/s flow. | IMU (STMicro ISM330DHCX) FFT bin shows sustained narrow-band peak acceleration >1.5g RMS between 10–25 Hz. | 5 | 3 | Weld helical strakes (height = 0.12D, pitch = 5D) along the 38.1 mm OD 316L Schedule 40 deployment arm; gusset the root flange with 8 mm thick triangular ribs and specify 100% dye-penetrant inspection on all fillet welds. |
| **RR-10** | **Sensor drift** (pH/DO/Conductivity calibration shift) | Reference electrode electrolyte depletion, membrane fouling, or thermistor aging. | Cross-check violation against dual-redundant reference thermistor (>0.3°C delta) or out-of-bounds night-time baseline stability. | 2 | 5 | Switch from analog to digital RS-485 Modbus smart sensors with isolated titanium ground paths (Atlas Scientific EZO-EC with K=1.0 4-pole graphite probe); enforce automated 2-point field swap-out every 90 days using pre-calibrated wet-mateable SubConn Micro Circular 8-pin connectors (MCIL8F). |
| **RR-11** | **Gateway loss** (Telemetry blackout, data buffer overflow) | Bankside LoRaWAN/Cellular gateway power failure, antenna misalignment, or foliage attenuation. | Probe fails to receive MAC-layer `LinkADRReq` or ACK frames for 6 consecutive transmission windows. | 3 | 4 | Solder a 512 Mbit industrial SPI NOR Flash (Winbond W25Q512JV, -40°C to +85°C) onto the mainboard configured as a wear-leveled LittleFS ring buffer capable of storing 180 days of 5-minute packets; implement exponential backoff retry and fallback to Iridium SBD (RockBLOCK 9603) for daily summary heartbeat. |
| **RR-12** | **Firmware watchdog** (MCU hard-fault or I2C bus hang) | UnhandledRTOS task deadlock, EMI spike on sensor bus, or brown-out during peripheral power-up. | `RCC_CSR` register flags `IWDGRSTF` (Independent Watchdog Reset) or `LPWRRSTF` upon reboot telemetry frame. | 4 | 3 | Add an external hardware watchdog timer with power-cycling FET output (Texas Instruments TPL5010, timeout set to 30 s via 36.5 kΩ resistor) driving the enable pin of the main 3.3V buck regulator; wire all I2C buses through resettable multiplexers (TI TCA9548A) with hardware reset lines tied to MCU GPIO. |