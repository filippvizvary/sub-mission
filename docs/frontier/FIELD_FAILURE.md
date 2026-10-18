### Baseline Engineering Parameters & Working
To evaluate the failure modes quantitatively, we establish the baseline hydro-mechanical and electrical budget for a Slovak lowland river (e.g., Little Danube, Váh, or Hron) in October:
*   **Flow & Stage:** Base flow $v = 0.5\text{ m/s}$, autumn rain pulse $v = 1.8\text{ m/s}$. Water temperature $T_w = 8^\circ\text{C} \text{ to } 14^\circ\text{C}$. Ambient air $T_a = -2^\circ\text{C} \text{ to } 18^\circ\text{C}$.
*   **Hydrodynamics:** Pod dimensions $D = 0.08\text{ m}$, $L = 0.42\text{ m}$, cross-sectional area $A \approx 0.0336\text{ m}^2$. Turbine swept area $A_t$ ($D_t = 0.06\text{ m}$) $= 0.0028\text{ m}^2$.
    *   *Clean Drag Force ($F_d$):* $\frac{1}{2} \rho v^2 C_d A = 0.5(1000)(0.5^2)(1.0)(0.0336) = 4.2\text{ N}$.
    *   *Fouled/Flooded Drag Force:* Leaf collection increases effective area to $0.25\text{ m}^2$, $C_d = 1.5$. At $v = 1.8\text{ m/s}$: $F_d = 0.5(1000)(1.8^2)(1.5)(0.25) = 607.5\text{ N}$.
    *   *Cantilever Torque on Bank Pole:* $M = F_d \times L_{\text{arm}} = 607.5\text{ N} \times 1.2\text{ m} = 729\text{ Nm}$.
*   **Power Budget:** 
    *   *Hydro Kinetic Power:* $P_{\text{avail}} = \frac{1}{2} \rho A_t v^3 = 0.5(1000)(0.0028)(0.5^3) = 0.175\text{ W}$. At $20\%$ total system efficiency ($\eta$), harvested power $P_{\text{in}} = 35\text{ mW}$.
    *   *Load:* ESP32-S3 + SX1262 + Sensors. Active duty: $120\text{ mA at } 3.3\text{V for } 3\text{s every } 15\text{ mins}$ ($E = 1.188\text{ J}$). Deep sleep: $150\text{ }\mu\text{A}$ ($P = 0.5\text{ mW}$). Average load $P_{\text{load}} \approx 1.8\text{ mW}$.
    *   *Storage:* $50\text{ F}$ hybrid/EDLC supercap array ($V_{\text{max}} = 5.0\text{V}$, $V_{\text{cutoff}} = 3.0\text{V}$). Usable energy $E = \frac{1}{2} C (V_{\text{max}}^2 - V_{\text{min}}^2) = 0.5(50)(25 - 9) = 400\text{ J}$.
    *   *Zero-generation runtime:* $t = \frac{400\text{ J}}{0.0018\text{ W}} \approx 222,222\text{ s} \approx 61.7\text{ hours}$.

---

### Top 20 Field Failure Modes (Ordered by Probability $\times$ Severity)

#### 1. Leaf-Mat Stagnation of the Wet Turbine (Power Starvation)
*   **Mechanism:** October abscission of *Populus* and *Salix* leaves creates high suspended load. Wet-side rotor intake screens or blades catch a single leaf, initiating a cascade that forms a high-drag mat, dropping inflow velocity $v \to 0\text{ m/s}$ while blocking the rotor.
*   **Working:** Turbine torque $\tau_{\text{hydro}} < \tau_{\text{cogging}}$. $P_{\text{in}} = 0\text{ W}$. Supercap discharges linearly at $dV/dt = -I_{\text{avg}}/C = -550\text{ }\mu\text{A} / 50\text{ F} = -0.0396\text{ V/hr}$. System dies in $50\text{–}62\text{ hours}$.
*   **Telemetry Tell-Tale:** Generator RPM drops from nominal ($150\text{–}300\text{ RPM}$) to $0$ over $<15\text{ minutes}$ while Depth (MS5837) remains constant (ruling out dewatering). Supercap voltage $V_{\text{cap}}$ transitions to a constant negative slope of $-0.04\text{ V/hr}$ with zero diurnal recovery.

#### 2. Cantilever Yield / Soil Shear of the Bank Pole (Debris Raft Impact)
*   **Mechanism:** Autumn rain triggers a $0.5\text{ m}$ stage rise, mobilizing woody debris. A branch catches the $420\text{ mm}$ pod, catching leaves until effective area $A \approx 0.25\text{ m}^2$. 
*   **Working:** As calculated in the baseline, $729\text{ Nm}$ torque is applied to the bank pole anchored in wet, cohesive/silty bank soil (low shear strength, $c_u \approx 20\text{ kPa}$). The pole rotates in the mud, or the $1.2\text{ m}$ arm yields, swinging the pod downstream and up onto the bank margin.
*   **Telemetry Tell-Tale:** MS5837 pressure shows a sharp spike (hydrodynamic downforce of the debris strike) followed by an immediate drop to near-atmospheric pressure ($\approx 1013\text{ mbar}$). LoRa RSSI drops by $10\text{–}20\text{ dB}$ due to antenna polarization shift as the pole tilts $>45^\circ$.

#### 3. Ferromagnetic Silt Bridging the Magnetic Coupling Air Gap
*   **Mechanism:** Slovak rivers carry magnetite/hematite silt fractions from alpine/mining origins. The high-gradient magnetic field of the wet-side NdFeB rotor acts as a magnetic separator, packing ferromagnetic particles into the $1.5\text{ mm}$ radial clearance around the containment shroud.
*   **Working:** Viscous friction transforms to Coulomb friction. Frictional torque $\tau_f = \mu F_{\text{normal}} r$. Once $\tau_f$ exceeds the hydrodynamic torque at $0.5\text{ m/s}$ ($\approx 2\text{ mNm}$), the rotor seizes.
*   **Telemetry Tell-Tale:** Progressive decay in the $\text{RPM} / \text{Depth}$ ratio over $5\text{–}10\text{ days}$. Generator RPM exhibits "stick-slip" behavior: $0\text{ RPM}$ at base flow, jumping suddenly to $400\text{ RPM}$ only during high-stage events, before permanently locking at $0\text{ RPM}$.

#### 4. Low-Stage Stranding (Pod Exposed to Air)
*   **Mechanism:** Upstream hydro-peaking (common on the Váh/Hron) or dry autumn spells drop the river stage by $>420\text{ mm}$, leaving the fixed-arm pod hanging in the air.
*   **Working:** Submergence depth $h \le 0\text{ m}$. $P_{\text{in}} = 0\text{ W}$. Furthermore, the pH glass bulb dries out, causing KCl reference crystal precipitation and permanent junction potential shift.
*   **Telemetry Tell-Tale:** MS5837 depth declines steadily to $0.00\text{ m}$. NTC temperature begins tracking ambient diurnal air swings ($\Delta T > 12^\circ\text{C}$ day/night vs. river $\Delta T < 1.5^\circ\text{C}$). EC drops instantly to $0.0\text{ }\mu\text{S/cm}$.

#### 5. Optical Turbidity Window Occlusion (Diatom Biofilm + Silt)
*   **Mechanism:** Without a mechanical wiper, periphytic diatoms (*Navicula*, *Diatoma*) colonize the sapphire/epoxy optical window within $5\text{ days}$, secreting EPS (extracellular polymeric substances) that trap suspended clay.
*   **Working:** The $860\text{ nm}$ IR emitter/detector path (ISO 7027 $90^\circ$ scatter) experiences near-field backscattering directly off the window surface rather than the water column.
*   **Telemetry Tell-Tale:** Turbidity baseline follows a logistic growth curve ($S$-curve) from a nominal $15\text{ NTU}$ up to the sensor saturation ceiling ($1000\text{–}4000\text{ NTU}$) over $8\text{–}12\text{ days}$, completely decoupled from river stage (MS5837) and conductivity changes.

#### 6. MS5837 Gel Diaphragm Fouling / Silt Plugging
*   **Mechanism:** The MS5837 relies on a tiny port filled with fluoro-silicone gel. Suspended silt settles into the port cavity; bacteria consume organic matter, calcifying or stiffening the plug, or a small aquatic gastropod (*Potamopyrgus*) crawls into the recess.
*   **Working:** The mechanical compliance of the gel drops. Pressure transmission becomes damped and thermally coupled to the mechanical expansion of the trapped silt plug rather than hydrostatic head.
*   **Telemetry Tell-Tale:** Depth reading becomes artificially "flat-lined" (loss of high-frequency wave/turbulence noise variance), and develops a strong inverse correlation with NTC temperature due to thermal expansion of the trapped mud plug against the piezo-resistive bridge.

#### 7. pH Reference Junction Fouling & Sulfide Poisoning
*   **Mechanism:** Decomposing autumn leaf litter around the pod creates a localized anoxic micro-environment. Sulfate-reducing bacteria produce $\text{H}_2\text{S}$, which diffuses through the porous PTFE/ceramic junction, reacting with the $\text{Ag/AgCl}$ reference wire to form insoluble $\text{Ag}_2\text{S}$.
*   **Working:** Nernstian slope ($56\text{ mV/pH}$ at $10^\circ\text{C}$) degrades, and the asymmetry potential ($E_0$) drifts massively as the reference impedance climbs past $100\text{ M}\Omega$.
*   **Telemetry Tell-Tale:** pH values drift monotonically in one direction (usually downward to apparent pH $4.0\text{–}5.0$ in a buffered pH $7.8$ river) and the diurnal photosynthetic pH swing ($\pm 0.3\text{ pH}$ units) vanishes into flat, high-impedance electrical noise.

#### 8. Dynamic Seal Failure / Thermal-Vacuum Water Ingress
*   **Mechanism:** The pod sits in sun on a cool morning ($T_{\text{pod}} = 20^\circ\text{C}$), then is submerged by a cold mountain rain pulse ($T_{\text{water}} = 7^\circ\text{C}$). 
*   **Working:** Ideal gas law: $\Delta P = P_0 (1 - \frac{280\text{ K}}{293\text{ K}}) \approx -4.5\text{ kPa}$ ($-0.045\text{ bar}$) vacuum inside the pod. This negative pressure draws river water past the static O-rings or sensor cable glands,which are optimized for positive external pressure, not vacuum flexing.
*   **Telemetry Tell-Tale:** ESP32-S3 internal temperature sensor diverges from external NTC due to short-circuit Joule heating on the PCB; $V_{\text{cap}}$ drops erratically (high leakage current $>10\text{ mA}$); final transmission shows corrupted sensor ADC bit-states before sudden silence.

#### 9. Plain Bearing Wear-Out on Wet Turbine Rotor
*   **Mechanism:** The wet rotor runs on a water-lubricated polymer/ceramic plain bearing (e.g., PTFE/PEEK on 316SS shaft). Quartz silt ($D_{50} = 30\text{ }\mu\text{m}$, Mohs hardness $7$) enters the bearing clearance ($50\text{ }\mu\text{m}$), acting as three-body abrasive lapping compound.
*   **Working:** At $200\text{ RPM}$, the rotor executes $8.64 \times 10^6\text{ revolutions}$ in $30\text{ days}$. Radial wear of $1.0\text{ mm}$ allows the wet magnets to eccentricity-Precess and physically rub against the containment shroud.
*   **Telemetry Tell-Tale:** High variance (jitter) in RPM readings taken over short intervals. Average $P_{\text{in}}$ drops by $50\%$ at constant depth, and RPM occasionally spikes to $0$ as the eccentric rotor mechanically binds, then breaks free.

#### 10. Galvanic / Stray-Current Corrosion of 4-Pole EC Electrodes
*   **Mechanism:** Improper isolation between the ESP32 ground, the LoRa antenna shield (grounded to the steel bank pole), and the water creates a galvanic cell, or the EC excitation AC signal has a small DC offset ($>50\text{ mV}$) due to a leaky coupling capacitor.
*   **Working:** Faraday's law of electrolysis: even $1\text{ }\mu\text{A}$ of DC leakage over $20\text{ days}$ dissolves $0.5\text{ mg}$ of metal from the drive electrodes and plates calcium carbonate ($\text{CaCO}_3$) scale onto the cathode in hard Slovak river water.
*   **Telemetry Tell-Tale:** EC reading steadily declines by $2\text{–}5\%$ per day (due to insulating $\text{CaCO}_3$ scale increasing cell constant $K$) despite constant or falling river depth (when EC should naturally rise or stay stable).

#### 11. Vortex-Induced Vibration (VIV) Fatigue of Antenna Coax
*   **Mechanism:** The cylindrical pod ($D = 0.08\text{ m}$) or the vertical support tube in a $1.0\text{ m/s}$ flow sheds Kármán vortices.
*   **Working:** Strouhal number $St \approx 0.2$. Shedding frequency $f = \frac{St \cdot v}{D} = \frac{0.2 \times 1.0}{0.08} = 2.5\text{ Hz}$. Over $30\text{ days}$, the arm undergoes $6.48 \times 10^6\text{ cycles}$. The rigid RG-316 or U.FL-to-SMA coax cable work-hardens at the strain relief or solder joint and fractures the center conductor.
*   **Telemetry Tell-Tale:** LoRa SNR and RSSI at the gateway drop precipitously by $>25\text{ dB}$ from one packet to the next. If packet reception continues via near-field leakage, the ESP32-S3 reports a reduced voltage drop $\Delta V_{\text{cap}}$ during TX (SX1262 protection circuit folds back power due to $\text{VSWR} > 10:1$).

#### 12. Magnetic Decoupling (Slip) During Flash Flood Pulse
*   **Mechanism:** An autumn storm pushes flow velocity to $v = 2.2\text{ m/s}$. The generator is loaded heavily to charge the supercap.
*   **Working:** Hydrodynamic torque scales with $v^2$: $\tau_{\text{hydro}} \propto (2.2 / 0.5)^2 = 19.3\times$ base torque. This exceeds the peak break-away torque of the magnetic coupling ($\tau_{\text{max}} \approx 50\text{ mNm}$). The wet rotor slips out of synchronous lock with the dry generator rotor.
*   **Telemetry Tell-Tale:** During a rising stage event (MS5837 depth increasing rapidly), Generator RPM suddenly drops to $0$ or oscillates wildly at low values (as the slipping magnets pole-pass without locking, inducing high-frequency AC ripple but zero net rotation), while charging current drops to $0\text{ mA}$.

#### 13. Supercapacitor Over-Voltage Venting (Shunt Failure)
*   **Mechanism:** During sustained high flow ($v = 1.5\text{ m/s}$), available power $P_{\text{avail}} \propto v^3 = 27\times$ base power ($\approx 1\text{ W}$). Once the supercap reaches $5.0\text{V}$, the excess $1\text{ W}$ must be dissipated by a Zener/FET shunt regulator inside the sealed plastic/metal pod.
*   **Working:** $1\text{ W}$ continuous dissipation in a small sealed volume raises local PCB temperature by $40^\circ\text{C}$, desoldering or failing the shunt FET open-circuit. Generator open-circuit voltage spikes to $>12\text{V}$, exceeding the $2.7\text{V}$/cell limit of the supercaps, causing acetonitrile electrolyte boiling and venting.
*   **Telemetry Tell-Tale:** $V_{\text{cap}}$ climbs past the $5.0\text{V}$ clamp limit up to $5.8\text{V}$ during high RPM; subsequent nights/low-flow periods show the effective capacitance $C$ has dropped from $50\text{ F}$ to $<5\text{ F}$ (calculated from $\Delta V$ per TX cycle jumping from $10\text{ mV}$ to $>100\text{ mV}$), accompanied by massive ESR voltage sag during SX1262 TX bursts.

#### 14. Internal Condensation Dew-Point Bridge on pH Analog Front-End
*   **Mechanism:** The pod is assembled in a workshop at $22^\circ\text{C}$ and $60\%$ RH (dew point $= 13.9^\circ\text{C}$). If the silica gel desiccant pack is omitted or saturated, submerging the pod in $9^\circ\text{C}$ October river water drops the internal wall and PCB temperature below the dew point.
*   **Working:** Liquid water micro-droplets condense on the PCB. The pH glass electrode has an impedance of $100\text{ M}\Omega\text{ to }1\text{ G}\Omega$. A single condensation bridge across the guard ring of the LMP91200 / op-amp input shunts the signal to ground or $V_{\text{ref}}$.
*   **Telemetry Tell-Tale:** As NTC water temperature drops below $13^\circ\text{C}$, the pH reading locks precisely to $7.00$ (0 mV differential, shorted input) or rails to $0.00 / 14.00$ (shorted to supply rail), temporarily recovering if solar heating warms the pod during low water.

#### 15. Bank-Margin Siltation / Sandbar Burial
*   **Mechanism:** A $1.2\text{ m}$ arm places the pod directly in the deceleration shear zone between the main channel and the grassy bank. As an autumn flood pulse recedes, bedload sediment (fine sand and silt) drops out of suspension right at the bank toe.
*   **Working:** A local dune/bar builds up by $300\text{–}500\text{ mm}$, completely burying the lower half of the $420\text{ mm}$ deep pod in saturated sediment.
*   **Telemetry Tell-Tale:** RPM drops to $0$; Turbidity pegs at maximum ($>4000\text{ NTU}$); EC drops by $30\text{–}50\%$ (measuring pore-water tortuosity in sand rather than bulk water); NTC thermal time-constant increases dramatically (diurnal temperature phase-lags the river by $4\text{–}6\text{ hours}$ and damps in amplitude).

#### 16. Rodent (Beaver / Muskrat / Nutria) Gnawing of Exposed Cabling
*   **Mechanism:** Slovak lowland rivers have high densities of *Castor fiber* (beaver), *Ondatra zibethicus* (muskrat), and invasive *Myocastor coypus* (nutria). The grassy bank pole and $1.2\text{ m}$ arm serve as a haul-out/grooming perch. Soy-based or soft TPU cable jackets attract gnawing.
*   **Working:** Rodent incisors exert bite forces of $500\text{ N}$ at the tip, easily shearing through exposed sensor or antenna cables routed along the exterior of the $1.2\text{ m}$ arm.
*   **Telemetry Tell-Tale:** Instantaneous, simultaneous transition of multiple sensors to hardware-fault states (e.g., NTC reads $-40^\circ\text{C}$ [open] or $+125^\circ\text{C}$ [shorted to $3.3\text{V}$]; MS5837 $\text{I}^2\text{C}$ bus returns `0xFFFF` / NACK) within a single $15\text{-minute}$ sleep window, always occurring at night (between $20:00\text{ and }05:00$).

#### 17. Hydrodynamic Lift / Pitch Instability of the Arm
*   **Mechanism:** The $420\text{ mm}$ pod is suspended from a $1.2\text{ m}$ arm. If the clamping collar on the bank pole lacks a positive mechanical key (relying only on friction), asymmetric flow over the pod body generates hydrodynamic lift and pitching moments.
*   **Working:** At $v = 1.5\text{ m/s}$ with a $10^\circ$ angle of attack, lift coefficient $C_L \approx 0.4$. Lift force $F_L = \frac{1}{2} \rho v^2 C_L A \approx 15\text{ N}$, pulsing with turbulence. Over days, the collar creeps/rotates around the pole, or the arm pivots upward, planing the pod toward the surface.
*   **Telemetry Tell-Tale:** MS5837 depth shows a sudden inverse correlation with flow velocity (RPM): as RPM increases during high flow, measured depth *decreases* (the pod is planing upward toward the surface rather than getting deeper).

#### 18. Frazil / Surface Ice Formation on the Bank Arm (Late October Freeze)
*   **Mechanism:** A clear, calm late-October night brings air temperatures of $-5^\circ\text{C}$. While the river bulk stays at $+6^\circ\text{C}$, the metallic $1.2\text{ m}$ arm acts as a radiative cooling fin, and surface border ice forms at the grassy bank interface.
*   **Working:** Border ice freezes around the upper shaft of the pod and the $1.2\text{ m}$ arm. As river stage drops by $100\text{ mm}$ the next morning, the pod is momentarily held up by the ice sheet, then breaks free, or the ice sheet crushes the exposed cable entry gland.
*   **Telemetry Tell-Tale:** Internal ESP32 temperature drops below $0^\circ\text{C}$ while submerged NTC reads $+4^\circ\text{C}\text{ to }+6^\circ\text{C}$. Depth reading shows a flat plateau during a falling tide (held up by ice), followed by a sudden step-change drop of $50\text{–}100\text{ mm}$ when the ice cantilevers and snaps.

#### 19. Brownout-Loop Latch-Up of ESP32-S3 + SX1262
*   **Mechanism:** At low supercap voltage ($V_{\text{cap}} \approx 3.1\text{V}$), the cold October temperature ($5^\circ\text{C}$) increases the supercap ESR from $50\text{ m}\Omega\text{ to }250\text{ m}\Omega$. 
*   **Working:** When the ESP32-S3 boots ($I_{\text{peak}} = 350\text{ mA}$ RF calibration spike) or fires the SX1262 at $+22\text{ dBm}$ ($120\text{ mA}$), the voltage drop $\Delta V = I \cdot R_{\text{ESR}} = 0.35\text{ A} \times 0.25\text{ }\Omega = 0.087\text{V}$, plus DC-DC converter inrush, pulling the $3.3\text{V}$ rail below the $2.8\text{V}$ brownout detector threshold. The MCU resets, immediately attempts to boot again, and locks into a $10\text{ Hz}$ reboot oscillation that drains the remaining $400\text{ J}$ in minutes without ever transmitting.
*   **Telemetry Tell-Tale:** The last received packet before a multi-day blackout shows $V_{\text{cap}}$ at a seemingly safe $3.15\text{V}$ while NTC temperature is at a minimum ($<6^\circ\text{C}$). When flow increases days later and the unit finally recovers, the non-volatile boot-counter register increments by $+15,000$ instead of $+1$.

#### 20. Vandalism / Angler Snagging (Braided Fishing Line Ingress)
*   **Mechanism:** October is peak pike/zander (*Esox lucius* / *Sander lucioperca*) spinning season in Slovakia. A $1.2\text{ m}$ overhang from a grassy bank looks like prime predator cover. An angler casts a lure across the arm; $0.20\text{ mm}$ braided UHMWPE (Dyneema) line wraps around the wet turbine shaft.
*   **Working:** The angler pulls with $100\text{ N}$ force to free the snag, cinching the $0.20\text{ mm}$ braided line tightly into the gap between the rotor hub and the housing, locking the rotor solid and bending the mounting arm.
*   **Telemetry Tell-Tale:** Occurs exclusively during daylight/twilight hours (especially weekends). MS5837 shows violent, erratic depth oscillations ($\pm 300\text{ mm}$ over $60\text{ seconds}$ as the angler yanks the rod), followed by a permanent offset in resting depth (bent arm) and an instantaneous, permanent drop of Generator RPM to $0$.