### 1. Analytical Framework & Working

**System Constants & Fluid Properties:**
*   Water density ($\rho$): $1000\text{ kg/m}^3$
*   Dynamic viscosity ($\mu$): $1.00 \times 10^{-3}\text{ Pa}\cdot\text{s}$
*   Breakaway/Wet-side friction torque ($\tau_f$): $0.004\text{ N}\cdot\text{m}$
*   Hub centerline depth ($h$): $0.420\text{ m}$
*   Number of blades ($B$): $3$, Baseline tip chord ($c$): $0.08 D$, Effective torque moment arm ($r_{\text{eff}}$): $0.35 D$

#### (a) Cut-in Speed ($v_{\text{cut-in}}$)
At startup ($\omega = 0$), the relative flow angle is $\phi = 90^\circ$. For a pitch angle $\theta$ (measured from the rotor rotation plane), the angle of attack at standstill is $\alpha_0 = 90^\circ - \theta$. For $\theta \in [20^\circ, 36^\circ]$, $\alpha_0 \in [54^\circ, 70^\circ]$, putting the NACA 4412 profile entirely in the deep post-stall flat-plate regime. 

Using Hoerner’s empirical flat-plate/post-stall airfoil relations, the normal force coefficient driving tangential startup torque is $C_T(\theta) \approx 1.8 \sin(90^\circ - \theta)\cos(90^\circ - \theta) \sin(\theta) = 0.9 \sin(2\theta)\sin(\theta)$ (accounting for post-stall lift-to-drag collapse). Integrating across $B=3$ blades with average chord $\bar{c} = 0.08D$ and span $L \approx 0.4D$:
$$\tau_{\text{start}} = \frac{1}{2} \rho v^2 B (\bar{c} L) r_{\text{eff}} C_T(\theta) = 16.8 \, D^3 C_T(\theta) v^2$$
Setting $\tau_{\text{start}} = \tau_f = 0.004\text{ N}\cdot\text{m}$, the cut-in velocity is:
$$v_{\text{cut-in}} = \sqrt{\frac{0.004}{16.8 \, D^3 C_T(\theta)}} = \frac{0.01543}{\sqrt{D^3 C_T(\theta)}}$$
*Startup Torque Coefficient $C_T(\theta)$ Evaluation:*
*   $\theta = 20^\circ \implies C_T = 0.198$
*   $\theta = 24^\circ \implies C_T = 0.272$
*   $\theta = 28^\circ \implies C_T = 0.350$
*   $\theta = 32^\circ \implies C_T = 0.428$
*   $\theta = 36^\circ \implies C_T = 0.503$

#### (b) Shaft Power ($P_{0.5}, P_{1.0}$)
While the prompt references a nominal BEM baseline of $C_p = 0.35$ (achieved at the $D=220\text{ mm}, \theta=28^\circ, \text{TSR}=5.5$ design point), real BEM performance across the sweep is governed by two modifiers: **Pitch Mismatch ($\eta_\theta$)** and **Reynolds Number Scaling ($\eta_{\text{Re}}$)**:
1.  **Pitch Penalty:** At $\text{TSR}=5.5$, the local inflow angle at $r/R = 0.7$ is $\phi = \arctan(1 / (5.5 \times 0.7)) = 14.5^\circ$. For NACA 4412 ($C_{l,\max}/C_d \text{ at } \alpha \approx 6^\circ$), high pitch angles drive the section into negative-incidence drag at design TSR unless TSR drops. Applying a parabolic BEM off-design envelope centered on the $28^\circ$ baseline:
    $$\eta_\theta = 1 - 0.0035(\theta - 28)^2$$
2.  **Reynolds Scaling:** Tip chord $c \propto D$, so $\text{Re}_c \propto D$. Using turbulent boundary layer skin-friction scaling:
    $$\eta_{\text{Re}} = \left(\frac{D}{0.220}\right)^{0.15}$$
3.  **Net Power Formulation:**
    $$C_{p,\text{eff}} = 0.35 \cdot \eta_\theta \cdot \eta_{\text{Re}}$$
    $$P(v) = \left[ \frac{1}{2} \rho \left(\frac{\pi}{4} D^2\right) v^3 C_{p,\text{eff}} \right] - \tau_f \omega_{\text{rated}}(v), \quad \text{where } \omega = \frac{5.5 v}{D/2}$$

#### (c) Axial Thrust on Carrier Bearing ($T_{0.5}, T_{1.0}, T_{\max}$)
At the optimal axial induction factor ($a \approx 0.28$), the baseline thrust coefficient is $C_{t0} = 4a(1-a) \approx 0.806$. Higher blade pitch feathers the blade toward the flow, reducing the projected solidity and normal force vector. Modeling the pitch sensitivity via BEM momentum-strip theory:
$$C_t(\theta) = 0.806 - 0.015(\theta - 28)$$
$$F_T(v) = \frac{1}{2} \rho \left(\frac{\pi}{4} D^2\right) v^2 C_t(\theta)$$
*(Evaluated at $v = 0.5\text{ m/s}$, $1.0\text{ m/s}$, and maximum survival flood flow $2.0\text{ m/s}$).*

#### (d) Free-Surface Vortex-Ingestion Risk
Free-surface air entrainment and performance-degrading tip cavitation/vortex ingestion are governed by the Top Tip Submergence Ratio ($S_{\text{top}}/D$) and the submergence Froude number ($Fr_S = v / \sqrt{g S_{\text{top}}}$), where top-tip depth is $S_{\text{top}} = h - D/2 = 0.420 - D/2$. 
*   **Low Risk:** $S_{\text{top}}/D > 1.25$ and $Fr_{S,\max} < 1.15$ (Fully submerged, negligible surface dimpling).
*   **Moderate Risk:** $0.85 \le S_{\text{top}}/D \le 1.25$ (Intermittent surface-vortex shedding at $v > 1.5\text{ m/s}$; $\sim 3\text{--}5\%$ $C_p$ loss).
*   **High/Critical Risk:** $S_{\text{top}}/D < 0.85$ (Continuous air-core vortex ingestion above $v = 1.2\text{ m/s}$, severe cyclic thrust oscillation on carrier bearing).

---

### 2. Design Space Sweep Table

| $D$ (mm) | Pitch $\theta$ (deg) | $C_{p,\text{eff}}$ | (a) $v_{\text{cut-in}}$ (m/s) | (b) $P_{0.5}$ (W) | (b) $P_{1.0}$ (W) | (c) $T_{0.5}$ (N) | (c) $T_{1.0}$ (N) | (c) $T_{2.0}$ (N) | (d) $S_{\text{top}}/D$ | (d) $Fr_{S,\max}$ (@ 2m/s) | (d) Vortex Ingestion Risk |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **150** | **20** | 0.258 | 0.594 | 0.00* | 2.13 | 2.05 | 8.19 | 32.8 | 2.30 | 1.09 | **Low** (Safe all speeds) |
| **150** | **24** | 0.318 | 0.507 | 0.00* | 2.66 | 1.92 | 7.66 | 30.6 | 2.30 | 1.09 | **Low** (Safe all speeds) |
| **150** | **28** | 0.330 | 0.447 | 0.21 | 2.77 | 1.78 | 7.12 | 28.5 | 2.30 | 1.09 | **Low** (Safe all speeds) |
| **150** | **32** | 0.318 | 0.404 | 0.20 | 2.66 | 1.65 | 6.59 | 26.4 | 2.30 | 1.09 | **Low** (Safe all speeds) |
| **150** | **36** | 0.258 | 0.373 | 0.14 | 2.13 | 1.51 | 6.06 | 24.2 | 2.30 | 1.09 | **Low** (Safe all speeds) |
| **180** | **20** | 0.266 | 0.452 | 0.30 | 3.26 | 2.95 | 11.8 | 47.2 | 1.83 | 1.12 | **Low** (Safe all speeds) |
| **180** | **24** | 0.327 | 0.385 | 0.40 | 4.04 | 2.76 | 11.0 | 44.1 | 1.83 | 1.12 | **Low** (Safe all speeds) |
| **180** | **28** | 0.340 | 0.340 | 0.42 | 4.20 | 2.56 | 10.3 | 41.0 | 1.83 | 1.12 | **Low** (Safe all speeds) |
| **180** | **32** | 0.327 | 0.307 | 0.40 | 4.04 | 2.37 | 9.49 | 38.0 | 1.83 | 1.12 | **Low** (Safe all speeds) |
| **180** | **36** | 0.266 | 0.283 | 0.30 | 3.26 | 2.18 | 8.73 | 34.9 | 1.83 | 1.12 | **Low** (Safe all speeds) |
| **220** | **20** | 0.274 | 0.335 | 0.55 | 5.01 | 4.40 | 17.6 | 70.4 | 1.41 | 1.14 | **Low-Mod** (Dimpling >1.8m/s) |
| **220** | **24** | 0.337 | 0.286 | 0.70 | 6.21 | 4.12 | 16.5 | 65.8 | 1.41 | 1.14 | **Low-Mod** (Dimpling >1.8m/s) |
| **220** | **28** | **0.350** | **0.252** | **0.73** | **6.45** | **3.83** | **15.3** | **61.3** | **1.41** | **1.14** | **Low-Mod** (Dimpling >1.8m/s) |
| **220** | **32** | 0.337 | 0.228 | 0.70 | 6.21 | 3.55 | 14.2 | 56.7 | 1.41 | 1.14 | **Low-Mod** (Dimpling >1.8m/s) |
| **220** | **36** | 0.274 | 0.210 | 0.55 | 5.01 | 3.26 | 13.0 | 52.2 | 1.41 | 1.14 | **Low-Mod** (Dimpling >1.8m/s) |
| **260** | **20** | 0.280 | 0.261 | 0.84 | 7.26 | 6.15 | 24.6 | 98.5 | 1.12 | 1.18 | **Moderate** (Vortex >1.5m/s) |
| **260** | **24** | 0.346 | 0.223 | 1.06 | 9.01 | 5.76 | 23.0 | 92.1 | 1.12 | 1.18 | **Moderate** (Vortex >1.5m/s) |
| **260** | **28** | 0.359 | 0.196 | 1.10 | 9.36 | 5.36 | 21.4 | 85.7 | 1.12 | 1.18 | **Moderate** (Vortex >1.5m/s) |
| **260** | **32** | 0.346 | 0.178 | 1.06 | 9.01 | 4.96 | 19.8 | 79.4 | 1.12 | 1.18 | **Moderate** (Vortex >1.5m/s) |
| **260** | **36** | 0.280 | 0.164 | 0.84 | 7.26 | 4.56 | 18.2 | 73.0 | 1.12 | 1.18 | **Moderate** (Vortex >1.5m/s) |
| **300** | **20** | 0.286 | 0.211 | 1.20 | 10.0 | 8.19 | 32.8 | 131.1 | 0.90 | 1.22 | **High** (Air ingestion >1.2m/s) |
| **300** | **24** | 0.352 | 0.180 | 1.50 | 12.3 | 7.66 | 30.6 | 122.6 | 0.90 | 1.22 | **High** (Air ingestion >1.2m/s) |
| **300** | **28** | 0.366 | 0.159 | 1.56 | 12.8 | 7.12 | 28.5 | 114.0 | 0.90 | 1.22 | **High** (Air ingestion >1.2m/s) |
| **300** | **32** | 0.352 | 0.143 | 1.50 | 12.3 | 6.59 | 26.4 | 105.5 | 0.90 | 1.22 | **High** (Air ingestion >1.2m/s) |
| **300** | **36** | 0.286 | 0.132 | 1.20 | 10.0 | 6.06 | 24.2 | 97.0 | 0.90 | 1.22 | **High** (Air ingestion >1.2m/s) |

*\*Note: At $D=150\text{ mm}$ and $\theta \le 24^\circ$, the rotor fails to self-start at $v=0.5\text{ m/s}$ ($v_{\text{cut-in}} > 0.50\text{ m/s}$), yielding $0.00\text{ W}$ unassisted.*

---

### 3. Rotor Selection Recommendation

Retain the **$D = 220\text{ mm}$ diameter** but increase the blade pitch from $28^\circ$ to **$\theta = 32^\circ$** (or select **$D = 260\text{ mm}, \theta = 32^\circ$** if the river site rarely exceeds $1.5\text{ m/s}$). While the $260\text{ mm}$ and $300\text{ mm}$ rotors satisfy the $0.20\text{ m/s}$ cut-in target outright, their top-tip submergence at a fixed $420\text{ mm}$ shaft depth falls to $290\text{ mm}$ ($S_{\text{top}}/D = 1.12$) and $270\text{ mm}$ ($S_{\text{top}}/D = 0.90$), respectively; at river speeds approaching $2.0\text{ m/s}$, this induces severe free-surface vortex ingestion, cyclic bearing hammer, and a $60\text{--}114\text{ N}$ peak axial thrust load. Conversely, the $150\text{ mm}$ and $180\text{ mm}$ rotors lack the swept area and moment arm to overcome the $4\text{ mN}\cdot\text{m}$ seal/bearing friction below $0.28\text{ m/s}$, sacrificing low-flow telemetry availability. Upgrading the $220\text{ mm}$ rotor to a $32^\circ$ pitch reduces the cut-in speed from $0.252\text{ m/s}$ to **$0.228\text{ m/s}$** (capturing nearly the entire $0.2\text{--}2.0\text{ m/s}$ regime), cuts maximum $2.0\text{ m/s}$ carrier bearing thrust by $7.5\%$ (from $61.3\text{ N}$ down to **$56.7\text{ N}$**), maintains safe submergence ($S_{\text{top}}/D = 1.41$), and incurs less than a $3.7\%$ BEM power penalty ($6.21\text{ W}$ vs. $6.45\text{ W}$ at $1.0\text{ m/s}$).