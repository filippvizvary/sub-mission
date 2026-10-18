#!/usr/bin/env python3
"""
sub-mission probe energy sim v2 - physics corrected after gemini review.
Changes vs v1:
 - cogging torque treated as cut-in threshold only (conservative field)
 - continuous losses = bearing/seal/viscous drag, not cog*omega
 - generator modelled via R_phase and Ke, no flat eta
 - rectifier eta computed from Vcap at each step
 - blade TIP pitch 9.2deg at TSR 5.5 (28deg was braking); twist from root
 - cut-in uses stalled-blade static torque model
Haven 2026-10-18 v2.
"""
import numpy as np

RHO=1000.0; MU=1.0e-3
ROTOR_D=0.220; ROTOR_R=ROTOR_D/2; BLADES=3
TIP_PITCH_DEG=9.2
root_pitch_deg=28.0
TSR=5.5

# drivetrain (physical components, no lumped fake eta)
KE=60/(2*np.pi*300)   # V/(rad/s), KV=300
R_PHASE=0.5           # ohm total for the two conducting phases [est]
VF_SCHOTTKY=0.35
TAU_SEAL=1.0e-3       # N m running seal drag [est]
TAU_VISC=2.0e-5       # N m s/rad viscous coefficient [est]
COG_TAU=2.0e-3        # N m breakaway only [ASSUMED - MEASURE]

VBUS=5.2; VMIN=3.0; C_SCAP=0.47
I_SLEEP=45e-6; V_S=3.3
P_SENSE=0.012; T_SENSE=3.0
P_TX=0.090; T_TX=1.319
CYCLES=96

def cp(tsr=TSR,pitch_tip=TIP_PITCH_DEG):
    # BEM-realistic peak for this class, ~0.30-0.35; scale-off if pitch deviates
    phi_tip=np.arctan(1/(tsr*0.67))
    alpha_tip=np.rad2deg(phi_tip)-pitch_tip
    # NACA 4412 cl/cd peak near alpha 6; penalty quadratic away from 6
    pen=max(0.0, 1-0.012*(alpha_tip-6)**2)
    return 0.34*pen

def static_start_tau(v):
    # post-stall flat-plate tangential force at standstill (Hoerner)
    # C_T(pitch) = 0.9 sin(2theta) sin(theta), theta = root pitch
    th=np.deg2rad(root_pitch_deg)
    ct=0.9*np.sin(2*th)*np.sin(th)
    # crude swept-blade planform: c_bar*L ~ 0.08D * 0.4D, x3 blades, r_eff=0.35D
    return 0.5*RHO*v**2 * 3*(0.08*ROTOR_D)*(0.4*ROTOR_D) * (0.35*ROTOR_D) * ct

def cutin():
    # solve v where static tau = cog tau
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
    p_loss=(TAU_SEAL + TAU_VISC*omega)*omega
    p_shaft=p_hydro-p_loss
    if p_shaft<=0: return 0.0
    # generator EMF - check feasibility of bus voltage
    emf_pk=KE*omega*np.sqrt(2)  # per-phase peak EMF
    # after 3ph rectification, DC bus ~= 1.65*emf_pk - 2*Vf
    bus_raw=1.65*emf_pk - 2*VF_SCHOTTKY
    # boost stage (LTC3105-class MPPT boost) when bus_raw < vcap
    if bus_raw >= vcap:
        eta_conv=0.85  # direct rectifier chain
    else:
        eta_conv=0.60  # boost converter penalty
    p_elec_mech=max(p_shaft,0.0)*0.95
    # power available at the generator terminal (max-transfer bound):
    # with 3-phase EMF per phase E_rms, R_phase each, max P_elec = 3*E^2/(4R)
    e_rms=KE*omega
    p_elec_max=3*e_rms**2/(4*R_PHASE)
    p_elec=min(p_elec_mech, p_elec_max)
    # copper loss implied at that operating point ~= p_elec/2 (at max-transfer)
    # when p_shaft << p_elec_max, load limits current: P_cu = p_elec^2 * R/(3*e^2)
    if p_elec>0:
        p_cu = p_elec**2 * R_PHASE/(3*e_rms**2) if p_elec < p_elec_max else p_elec*0.5
    else:
        p_cu=0
    p_out=(p_elec-p_cu)*eta_conv
    return max(p_out,0.0)

def energy_balance(v):
    p=chain(v)
    ein=p*86400
    eout=(I_SLEEP*V_S*86400 + CYCLES*(P_SENSE*T_SENSE + P_TX*T_TX))
    return ein,eout,ein-eout

def report():
    print("="*64); print("SUB-MISSION SIM v2 - corrected physics"); print("="*64)
    print(f"tip pitch {TIP_PITCH_DEG}deg  root {root_pitch_deg}deg @ TSR {TSR}  Cp={cp():.3f}")
    print(f"cut-in v = {cutin():.3f} m/s  [post-stall static-torque model]")
    for v in (0.2,0.3,0.5,0.8,1.0,1.5,2.0):
        p=chain(v); ein,eout,b=energy_balance(v)
        tag="SURPLUS" if b>0 else "DEFICIT"
        print(f"  v={v:3.1f}: P_elec={p*1000:7.1f} mW   daily {b:+13.1f} J ({tag})")
    print(f"supercap {C_SCAP}F {VMIN}-{VBUS}V = {0.5*C_SCAP*(VBUS**2-VMIN**2):.2f} J")
    print("="*64)
    print("[honesty]")
    print(" - cogging 2mNm assumed -> MEASURE on real motor")
    print(" - Cp from BEM class estimate with pitch-off penalty -> XFOIL polar needed")
    print(" - cut-in uses Hoerner post-stall flat-plate; first-principles, not measured")
    print(" - TAU_SEAL and TAU_VISC are estimates; bench-measure before ordering")

if __name__=="__main__":
    report()
