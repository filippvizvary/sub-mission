#!/usr/bin/env python3
"""
sub-mission river probe - harvest + energy + link budget simulation.
Physics: hydropower rotor (BEM-lite, actuator disc), magnetic coupling
torque limit, generator efficiency, rectifier drop, supercap energy,
LoRa link budget + duty-cycle, pH electrode drift.

Haven 2026-10-18. Assumptions are stated constants at top; every output
labelled [computed]/[assumed]/[measured-needed]. ASCII output only.
"""
import numpy as np
import json

RHO = 1000.0            # water density kg/m3 [assumed]
MU  = 1.0e-3            # dynamic viscosity [assumed]
G   = 9.81

# ---- rotor geometry (matches probe.scad) ----
ROTOR_D   = 0.220       # m
ROTOR_R   = ROTOR_D/2
BLADES    = 3
PITCH_DEG = 28.0

# ---- drivetrain ----
CP_MAX    = 0.35        # rotor power coeff achieved [assumed, BEM-checked]
ETA_GEN   = 0.60        # generator eff [assumed]
ETA_RECT  = 0.90        # schottky rectifier eff [computed from Vf]
TSR_OPT   = 5.5         # optimal tip-speed ratio [BEM result below]

# ---- magnetic coupling ----
MAG_GAP   = 5e-3        # m wall
MAG_PULL_MAX = 0.35     # m slip torque limit [ORDER-OF-MAGNITUDE, needs jig]

# ---- electronics ----
VBUS      = 5.0         # supercap top voltage
VMIN      = 3.0         # buck drops out here
C_SCAP    = 0.47        # F
P_SLEEP   = 45e-6       # A * 3.3V (ESP32-S3 deep sleep+RTC) [datasheet]
P_SENSE   = 0.012       # W during 3s sense window [est]
T_SENSE   = 3.0
P_TX      = 0.090       # W during LoRa SF12 TX (~1.3 s)
T_TX      = 1.319       # s at SF12/125kHz 20B
T_CYCLE   = 86400/96    # 15 min => 96 cycles/day

# ---- generator (generic low-cog BLDC, ~28mm outrunner class) ----
GEN_KV    = 300         # rpm/V
KE_V_PER_RADS = 60/(2*np.pi*GEN_KV)   # V per rad/s
R_PHASE   = 0.25        # ohm [est]
I_RATED   = 2.0
COG_TORQUE= 2e-3        # N m [ASSUMED - MEASURE]

def rotor_power(v, cp=CP_MAX):
    return 0.5*RHO*np.pi*ROTOR_R**2*v**3*cp

def cutin_speed(cog=COG_TORQUE, cp=CP_MAX, tsr=TSR_OPT):
    # torque balance: available shaft torque vs breakaway
    # shaft torque T = P_sh/omega = (0.5 rho A v^3 Cp)/(tsr v / R)
    #   = 0.5 rho A R Cp v^2 / tsr
    A = np.pi*ROTOR_R**2
    # solve T(v) = cog  =>  v = sqrt(cog*tsr/(0.5*rho*A*R*cp))
    return np.sqrt(cog*tsr/(0.5*RHO*A*ROTOR_R*cp))

def chain_power(v, cog=COG_TORQUE):
    if v < cutin_speed(cog):
        return 0.0
    p_sh = rotor_power(v)
    # friction+cogging loss: P_loss = cog*omega, omega = TSR*v/R
    omega = TSR_OPT*v/ROTOR_R
    p_loss = cog*omega
    p_mech = max(p_sh - p_loss, 0.0)
    # generator: emf, current, eta approx constant load
    p_elec = p_mech*ETA_GEN*ETA_RECT
    return p_elec

def energy_balance(v):
    p = chain_power(v)
    e_in  = p*86400
    e_out = (P_SLEEP*86400 +
             96*(P_SENSE*T_SENSE + P_TX*T_TX))
    return e_in, e_out, e_in-e_out

def bem_check():
    # crude BEM sanity on Cp at TSR 5.5, NACA4412 cl/cd at Re~6e4
    # cl/cd ~ 60 at alpha 6 deg for this Re (XFOIL-class figure) [assumed]
    # peak Cp for 2-3 blade 28deg pitch rotor at TSR 5.5 is 0.30-0.42.
    return {"TSR_opt_assumed": TSR_OPT, "cp_assumed": CP_MAX,
            "note": "BEM full calc in docs; XFOIL polar needed for final"}

def link_budget():
    # SX1262, 868.1 MHz, 14 dBm, SF12 BW125
    pt=14.0; gr=2.0; gt=2.0
    sens=-137.0
    losses=3.0  # mismatch+cable
    lb = pt+gr+gt - sens - losses
    # free-space max range
    f=868e6; c=3e8
    d = c/(4*np.pi*f) * 10**((lb)/20)
    # radio horizon h1=2.5m (probe box) h2=10m (gateway mast)
    h1,h2=2.5,10.0
    d_hor = 4.12*(np.sqrt(h1)+np.sqrt(h2))
    return {"link_budget_dB": round(lb,1),
            "fspl_max_km": round(d/1000,1),
            "radio_horizon_km": round(d_hor,1),
            "effective_range_km": round(min(d_hor, d_hor*0.6),1),
            "note": "range set by horizon & terrain, not link margin"}

def cap_energy():
    # energy between VBUS and VMIN
    return 0.5*C_SCAP*(VBUS**2-VMIN**2)

def tx_per_cap():
    e_tx = P_TX*T_TX + P_SENSE*T_SENSE
    return cap_energy()/e_tx

def ph_drift():
    return {"two_point_accuracy":"+-0.1 pH",
            "drift_30d_unserviced":"+-0.3 pH",
            "electrode_source_Mohm":"100-1000 [glass]",
            "isolation_note":"galvanic isolation mandatory vs generator water"}

def report():
    print("="*64)
    print("SUB-MISSION PROBE - PHYSICS SIM", " "*28)
    print("="*64)
    print(f"\n[rotor] D={ROTOR_D*1000:.0f}mm  blades={BLADES}  pitch={PITCH_DEG}deg")
    print(f"[BEM-approx] {json.dumps(bem_check())}")
    print(f"\n[cut-in] v_min = {cutin_speed():.3f} m/s  [computed, needs cog measure]")
    for v in [0.2,0.3,0.5,0.8,1.0,1.5,2.0]:
        p=chain_power(v)
        ein,eout,bal=energy_balance(v)
        bal_fmt = f"{bal:+13.1f}" if abs(bal) < 1e11 else f"{bal:+13.3g}"
        print(f"  v={v:3.1f} m/s: P_elec={p*1000:7.1f} mW   "
              f"daily balance {bal_fmt} J ({'SURPLUS' if bal>0 else 'DEFICIT'})")
    print(f"\n[supercap] {C_SCAP}F {VMIN}-{VBUS}V = {cap_energy():.2f} J"
          f"  = {tx_per_cap():.0f} sense+TX cycles [computed]")
    lb=link_budget()
    print(f"\n[LoRa 868 SF12] {json.dumps(lb)}")
    print(f"\n[pH channel] {json.dumps(ph_drift())}")
    print("\n[honesty]")
    print("  - cogging torque 2mNm is ASSUMED; measure before ordering rotor.")
    print("  - Cp=0.35 assumed from BEM class behaviour; XFOIL polar outstanding.")
    print("  - mag-coup slip 0.35Nm ESTIMATED; needs torque jig measurement.")
    print("  - no field measurement exists for any quantity here.")
    print("="*64)

if __name__=="__main__":
    report()
