#!/usr/bin/env python3
"""
sub-mission probe energy sim v3 - physics corrected (final review pass).
All 7 findings from gemini review applied:
 1. tip inflow angle: phi = atan((1-a)/tsr)            -> phi = arctan(0.67/TSR)
 2. stalled plate: tangential vs normal direction fix  -> ct = 0.9*sin(2th)*cos(th)
 3. KV is line-to-line peak; per-phase RMS = KE*omega/sqrt(6)
 4. 3ph rectifier bus ~= 0.955*KE*omega - 2*Vf  (not 1.65*sqrt2)
 5. R_PHASE is the 2-conducting-phase total; use R_SINGLE = R_PHASE/2 in per-phase formulas
 6. resolve P_cu inside the max-power-transfer solve, no double counting
 7. bus_raw <= 0 -> no conduction -> return 0
"""
import numpy as np

RHO=1000.0; MU=1.0e-3
ROTOR_D=0.220; ROTOR_R=ROTOR_D/2; BLADES=3
TIP_PITCH_DEG=2.0   # alpha_tip = atan(0.67/5.5) - 2 = 6.94-2 = ~5, near NACA4412 peak L/D
root_pitch_deg=28.0 # high root pitch for stall-start authority (post-stall plate regime)
TSR=5.5

KE=60/(2*np.pi*300)      # V/(rad/s) line-to-line sinusoidal-equivalent
R_PHASE_2W=0.5           # ohm across two conducting phases [est]
R_SINGLE=R_PHASE_2W/2
VF=0.35
TAU_SEAL=1.0e-3; TAU_VISC=2.0e-5
COG_TAU=2.0e-3

VBUS=5.2; VMIN=3.0; C_SCAP=0.47
I_SLEEP=45e-6; V_S=3.3
P_SENSE=0.012; T_SENSE=3.0
P_TX=0.090; T_TX=1.319
CYCLES=96

def cp(tsr=TSR, pitch_tip=TIP_PITCH_DEG):
    a=1-0.67  # axial induction
    phi_tip=np.arctan(0.67/tsr)
    alpha_tip=np.rad2deg(phi_tip)-pitch_tip
    pen=max(0.0, 1-0.012*(alpha_tip-6)**2)
    return 0.34*pen

def static_start_tau(v):
    th=np.deg2rad(root_pitch_deg)
    ct=0.9*np.sin(2*th)*np.cos(th)   # projection onto rotor plane
    return 0.5*RHO*v**2 * 3*(0.08*ROTOR_D)*(0.4*ROTOR_D) * (0.35*ROTOR_D) * ct

def cutin():
    lo,hi=1e-4,5.0
    for _ in range(80):
        m=(lo+hi)/2
        if static_start_tau(m)<COG_TAU: lo=m
        else: hi=m
    return (lo+hi)/2

def chain(v, vcap=4.0):
    if static_start_tau(v)<COG_TAU: return 0.0
    omega=TSR*v/ROTOR_R
    p_hydro=0.5*RHO*np.pi*ROTOR_R**2*v**3*cp()
    p_shaft=p_hydro-(TAU_SEAL+TAU_VISC*omega)*omega
    if p_shaft<=0: return 0.0
    p_elec_mech=max(p_shaft,0.0)*0.95  # bearing+misc efficiency

    # generator EMF / bus feasibility
    e_ll_pk = KE*omega                       # line-line peak EMF
    bus_raw = 0.955*e_ll_pk - 2*VF           # 3ph bridge
    if bus_raw <= 0: return 0.0
    eta_conv = 0.85 if bus_raw>=vcap else 0.60

    # max power transfer: P_elec_max_dc = (KE*omega)^2/(4*R_2w)
    e_ll_rms = e_ll_pk/np.sqrt(2)
    p_max = e_ll_rms**2/(4*R_PHASE_2W)
    if p_elec_mech >= p_max:
        p_out_raw = p_max
    else:
        # solve  P = p_mech - P_cu  with  P_cu = (P/e)^2 * R_2w
        # -> quadratic in P: a P^2 - P + p_mech = 0, a = R/e^2
        a = R_PHASE_2W/(e_ll_rms**2)
        disc = max(0.0, 1-4*a*p_elec_mech)
        p_out_raw = (1-np.sqrt(disc))/(2*a)
    p_out = max(p_out_raw,0.0)*eta_conv
    return p_out

def energy_balance(v):
    p=chain(v); ein=p*86400
    eout=I_SLEEP*V_S*86400 + CYCLES*(P_SENSE*T_SENSE + P_TX*T_TX)
    return ein,eout,ein-eout

def report():
    print("="*64); print("SUB-MISSION SIM v3 - fully corrected"); print("="*64)
    print(f"tip {TIP_PITCH_DEG}deg root {root_pitch_deg}deg TSR {TSR} Cp={cp():.3f}")
    print(f"cut-in = {cutin():.3f} m/s")
    for v in (0.1,0.15,0.2,0.3,0.5,0.8,1.0,1.5,2.0):
        p=chain(v); ein,eout,b=energy_balance(v)
        tag="SURPLUS" if b>0 else "DEFICIT"
        print(f"  v={v:4.2f}: P_elec={p*1000:8.1f} mW   daily {b:+13.1f} J ({tag})")
    print(f"supercap = {0.5*C_SCAP*(VBUS**2-VMIN**2):.2f} J usable")
    print("="*64)
    print("[honesty]")
    print(" - cogging 2mNm assumed -> MEASURE")
    print(" - TAU_SEAL/TAU_VISC estimated -> bench-measure")
    print(" - bus conversion efficiencies 0.85/0.60 are assumed")
    print(" - still no field data; every number is computed")

if __name__=="__main__": report()
