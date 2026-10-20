### 1. Physics & Arithmetic Errors in the Energy Simulation

#### Error 1: Blade Pitch Angle vs. TSR 5.5 (Stalled Rotor)
At $TSR (\lambda) = 5.5$, the local inflow angle $\phi$ at the blade tip ($r/R = 1.0$) and root ($r/R = 0.3$) are:
$$\phi_{\text{tip}} = \arctan\left(\frac{1}{\lambda (1 - a)}\right) \approx \arctan\left(\frac{1}{5.5 \times 0.67}\right) = \arctan(0.271) = 15.2^\circ$$
$$\phi_{\text{root}} \approx \arctan\left(\frac{1}{5.5 \times 0.3 \times 0.67}\right) = \arctan(0.904) = 42.1^\circ$$

The local angle of attack is $\alpha = \phi - \beta$ (where $\beta$ is pitch). If the blade has a constant or tip pitch of $\beta = 28^\circ$:
$$\alpha_{\text{tip}} = 15.2^\circ - 28^\circ = -12.8^\circ$$
At $\alpha = -12.8^\circ$, a NACA 4412 produces strong **negative** lift ($C_l \approx -0.8$), acting as a brake. The rotor will never reach $\lambda = 5.5$; it will equilibrium-lock at $\lambda \approx 1.8$. 
* **Correction:** For optimal $\alpha \approx 6^\circ$ at $\lambda = 5.5$, the tip pitch must be $\beta_{\text{tip}} = 15.2^\circ - 6^\circ = \mathbf{9.2^\circ}$. ($28^\circ$ is only valid as the root twist angle at $r/R \approx 0.35$).

#### Error 2: Cogging Torque is Not a Continuous Shaft Power Loss
Using $P_{\text{loss}} = \tau_{\text{cog}} \cdot \omega$ is a fundamental physics error. Cogging torque is a conservative magnetic reluctance interaction; its integral over a full mechanical revolution is zero:
$$\oint \tau_{\text{cog}}(\theta) \, d\theta = 0$$
Cogging torque dictates the **cut-in velocity** ($v_{\text{cut-in}}$), not running friction. 
* **Correction:** Replace $\tau_{\text{cog}}\omega$ with bearing, seal, and viscous drag torque $\tau_{\text{drag}} = \tau_{\text{seal}} + b\omega$. Use $\tau_{\text{cog}}$ solely as a binary threshold condition for start-up against static hydrodynamic torque ($\tau_{\text{start}}$ at $\omega = 0$):
$$v_{\text{cut-in}} = \sqrt{\frac{2 \tau_{\text{cog}}}{\rho A R C_{q,\text{static}}}}$$

#### Error 3: Double-Counting Generator Friction vs. 0.60 Efficiency
Applying a flat $\eta_{\text{gen}} = 0.60$ *after* subtracting mechanical shaft torque double-counts mechanical losses and misrepresents copper ($I^2R$) losses, which vary with load current.
* **Correction:** Model the generator via its phase resistance $R_{\text{ph}}$ and torque/back-EMF constant $K_t$ (or $K_e$):
$$P_{\text{elec}} = P_{\text{hydro}} - \tau_{\text{drag}}\omega - I_{\text{rms}}^2 R_{\text{ph}}$$

#### Error 4: Constant Rectifier Efficiency ($\eta_{\text{rect}} = 0.90$) Violates Circuit Physics
With a 2-diode Schottky drop of $V_{\text{drop}} = 2 \times 0.35\text{ V} = 0.70\text{ V}$ charging a supercapacitor between $V_{\text{cap}} = 3.0\text{ V}$ and $5.0\text{ V}$, the rectifier efficiency cannot be 0.90.
$$\eta_{\text{rect}}(V_{\text{cap}}) = \frac{V_{\text{cap}}}{V_{\text{cap}} + 2V_f}$$
* At $V_{\text{cap}} = 3.0\text{ V}$: $\eta_{\text{rect}} = \frac{3.0}{3.0 + 0.7} = \mathbf{81.1\%}$
* At $V_{\text{cap}} = 5.0\text{ V}$: $\eta_{\text{rect}} = \frac{5.0}{5.0 + 0.7} = \mathbf{87.7\%}$
* **Correction:** $\eta_{\text{rect}} = 0.90$ is only achieved at $V_{\text{cap}} = 6.3\text{ V}$ (above your cap's rating). Use the voltage-dependent efficiency equation above, or model the generator open-circuit voltage requirement: $V_{\text{gen,pk}} \ge V_{\text{cap}} + 0.7\text{ V}$.

#### Error 5: Missing DC-DC Converter Efficiency and Supercap Leakage
1. The load is specified at $3.3\text{ V}$, while the supercap sweeps $3.0\text{–}5.0\text{ V}$. A buck-boost regulator is required. Its efficiency ($\eta_{\text{reg}} \approx 0.85\text{–}0.92$ active, $\approx 0.75$ in $\mu\text{A}$ sleep) is omitted from both the usable energy stored ($3.76\text{ J}$ is strictly raw capacitor energy: $\frac{1}{2}(0.47)(5^2 - 3^2) = 3.76\text{ J}$) and the load draw.
2. A $0.47\text{ F}$ EDLC (typically two $1.0\text{ F}$, $2.7\text{ V}$ cells in series to hit $5.0\text{ V}$) requires balancing resistors or active balancing, plus inherent dielectric leakage ($I_{\text{leak}} \approx 5\text{–}15\,\mu\text{A}$), increasing baseline sleep draw by 10–30%.

#### Error 6: LoRa $90\text{ mW}$ Power Assumption at $+14\text{ dBm}$
* **LoRa Time-on-Air ($1.319\text{ s}$):** Correct for SF12, BW 125 kHz, CR 4/5, explicit header, 18-byte payload, 8-symbol preamble.
* **Power ($90\text{ mW}$):** At $3.3\text{ V}$, $90\text{ mW}$ equates to $27.3\text{ mA}$. While an SX1262 radio IC alone draws $\sim 29\text{ mA}$ ($95.7\text{ mW}$) at $+14\text{ dBm}$, the host MCU must remain awake in active or DMA-sleep mode ($3\text{–}8\text{ mA}$) during the transmission, and an SX1276 draws $\sim 38\text{ mA}$ ($125\text{ mW}$). 
* **Correction:** Total system TX power is $\mathbf{110\text{–}140\text{ mW}}$, not $90\text{ mW}$.

#### Baseline Load Math Check (Before DC-DC Losses)
* **Sleep:** $45\,\mu\text{A} \times 3.3\text{ V} = 148.5\,\mu\text{W}$. Active time/day = $96 \times (3 + 1.319)\text{ s} = 414.6\text{ s}$. Sleep time = $86400 - 414.6 = 85985.4\text{ s}$.
  $$E_{\text{sleep}} = 148.5\,\mu\text{W} \times 85985.4\text{ s} = \mathbf{12.77\text{ J/day}}$$
* **Sensing:** $0.012\text{ W} \times 3\text{ s} \times 96 = \mathbf{3.46\text{ J/day}}$
* **LoRa TX (as stated):** $0.090\text{ W} \times 1.319\text{ s} \times 96 = \mathbf{11.40\text{ J/day}}$
* **Corrected Daily Energy Required from Cap (with $\eta_{\text{reg}} = 0.85$ and $I_{\text{leak}} = 10\,\mu\text{A}$):**
  $$E_{\text{day}} = \frac{12.77 + 3.46 + 11.40}{\eta_{\text{reg}}} + (10\,\mu\text{A} \times 4.0\text{ V}_{\text{avg}} \times 86400\text{ s}) = 32.51 + 3.46 = \mathbf{35.97\text{ J/day}}$$
  *(Without hydro input, the $3.76\text{ J}$ cap buffer only sustains the node for $2.5\text{ hours}$.)*

---

### 2. Realistic $C_p$ for a D220 mm NACA 4412 at $Re \approx 6 \times 10^4$

A $C_p$ of **0.35 is physically unachievable** for this rotor at $Re = 6 \times 10^4$ and $\lambda = 5.5$. A realistic hydrodynamic $C_p$ is **0.18 to 0.23**.

#### Step 1: Chord and Solidity Constraints at $Re = 6 \times 10^4$
For a water turbine ($\nu \approx 1.0 \times 10^{-6}\text{ m}^2/\text{s}$) with $R = 0.11\text{ m}$ operating at $\lambda = 5.5$:
* If $v_\infty = 0.25\text{ m/s}$, relative velocity at $r/R = 0.75$ is $W \approx v_\infty \sqrt{(1-a)^2 + (0.75\lambda)^2} \approx 0.25 \times 4.18 = 1.05\text{ m/s}$.
* To hit $Re = \frac{W \cdot c}{\nu} = 6 \times 10^4$, the blade chord at $0.75R$ must be:
  $$c_{0.75R} = \frac{6 \times 10^4 \times 10^{-6}}{1.05} = 0.057\text{ m } (57\text{ mm})$$
* For $B = 3$ blades, local solidity at $0.75R$ is $\sigma = \frac{B c}{2 \pi r} = \frac{3 \times 0.057}{2 \pi (0.0825)} = \mathbf{0.33}$. 
*(Note: $\sigma = 0.33$ is excessively high for $\lambda = 5.5$, causing severe blade-to-blade blockage; optimal BEM chord for $\lambda = 5.5$ is $\sim 18\text{ mm}$, which drops $Re$ to $\mathbf{1.9 \times 10^4}$.)*

#### Step 2: XFOIL Polars for NACA 4412 at $Re = 6 \times 10^4$ ($N_{\text{crit}} = 5\text{–}9$)
Thick, cambered airfoils (12% thickness, 4% camber) suffer from a severe laminar separation bubble (LSB) on the suction side below $Re = 10^5$:
* Maximum lift-to-drag ratio at $Re = 6 \times 10^4$ occurs around $\alpha = 5^\circ\text{–}6^\circ$:
  $$C_l \approx 0.85, \quad C_d \approx 0.032\text{–}0.038 \implies \left(\frac{C_l}{C_d}\right)_{\max} \approx \mathbf{22\text{ to }26}$$
*(If using the aerodynamically correct $18\text{ mm}$ chord at $Re = 2 \times 10^4$, XFOIL shows laminar stall with $C_l/C_d \le \mathbf{11}$.)*

#### Step 3: Glauert / Wilson-Lissaman $C_p$ Reduction Calculation
Starting from the Betz limit ($C_{p,\text{Betz}} = 0.5926$), we apply finite-tip-speed-ratio wake rotation losses, Prandtl tip-loss factor ($F$), and profile drag losses:

1. **Inviscid Limit with Wake Rotation & 3-Blade Tip Loss ($\lambda = 5.5, B = 3$):**
   Using Prandtl's tip loss approximation for $B=3$ at $\lambda = 5.5$, the effective inviscid ceiling is:
   $$C_{p,\text{inviscid}} \approx 0.5926 \times \left[1 - \frac{1.84}{B \lambda}\right] \approx 0.5926 \times \left(1 - \frac{1.84}{16.5}\right) = \mathbf{0.526}$$

2. **Profile Drag Penalty ($\Delta C_{p,\text{drag}}$):**
   From BEM theory (Wilson & Lissaman), the power loss coefficient due to finite $C_l/C_d$ at tip speed ratio $\lambda$ is:
   $$\frac{\Delta C_p}{C_{p,\text{inviscid}}} \approx \frac{1.07 \cdot \lambda}{C_l / C_d}$$
   Using $C_l/C_d = 24$ (at $Re = 6 \times 10^4$) and $\lambda = 5.5$:
   $$\frac{\Delta C_p}{C_{p,\text{inviscid}}} = \frac{1.07 \times 5.5}{24} = 0.245 \quad (24.5\%\text{ loss})$$
   $$C_{p,\text{BEM}} = 0.526 \times (1 - 0.245) = \mathbf{0.397}$$

3. **3D Micro-Rotor Corrections (Hub, Root Drag, and Rotational Augmentation):**
   For a $D = 220\text{ mm}$ hydro-rotor, the hub diameter is typically $d_{\text{hub}} \ge 45\text{ mm}$ ($r_{\text{hub}}/R \approx 0.20\text{–}0.25$) to house the generator/seal, and root struts have $C_d \approx 0.15$:
   * **Hub blockage & root vortex loss:** $\eta_{\text{hub}} \approx 0.88$
   * **High-solidity cascade interference** (since $c = 57\text{ mm}$ gives $\sigma = 0.33$ at $\lambda = 5.5$): $\eta_{\text{cascade}} \approx 0.65$.

   $$C_{p,\text{real}} = C_{p,\text{BEM}} \times \eta_{\text{hub}} \times \eta_{\text{cascade}} = 0.397 \times 0.88 \times 0.65 = \mathbf{0.227}$$

#### Summary Recommendation for Rotor Redesign
To maximize $C_p$ on a $220\text{ mm}$ rotor at $Re \approx 6 \times 10^4$:
1. **Drop design TSR from $5.5$ to $3.2\text{–}3.8$:** The profile drag penalty scales linearly with $\lambda$. Dropping $\lambda$ to $3.5$ cuts profile drag power loss by $36\%$ and matches the high solidity required to maintain $Re = 6 \times 10^4$.
2. **Change Airfoil:** Replace the 12% thick NACA 4412 with a thin low-$Re$ section (e.g., **SG6043**, **SD7037**, or a **6% curved plate**), which achieves $C_l/C_d \approx 38\text{–}45$ at $Re = 6 \times 10^4$, recovering $C_p$ to **$\sim 0.28\text{–}0.31$**.