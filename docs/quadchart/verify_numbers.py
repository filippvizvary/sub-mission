#!/usr/bin/env python3
"""Every number quoted on the quad chart, recomputed from first principles and
printed with its source. Nothing here is a measurement."""
import math

RHO = 1000.0
D = 0.220
R = D / 2
A = math.pi * R**2
CP = 0.393          # sim/rotor_check.py, TSR 5 / alpha 5
TSR = 5.0
TAU_SEAL = 1.0e-3
TAU_VISC = 2.0e-5
KV = 128.0          # T-Motor GB2208
R_PH = 14.4         # ohm per phase
C_SERIES = 20.0     # 2 x 40 F in series
V_MAX, V_MIN = 5.0, 3.4
NEED_J_DAY = 28.0


def at(v):
    omega = TSR * v / R
    rpm = omega * 60 / (2 * math.pi)
    p_hyd = 0.5 * RHO * A * v**3 * CP
    p_loss = (TAU_SEAL + TAU_VISC * omega) * omega
    p_shaft = max(p_hyd - p_loss, 0.0)
    e_ll_pk = rpm / KV
    e_ph_rms = e_ll_pk / math.sqrt(6.0)
    p_el = 3 * e_ph_rms**2 / (4 * R_PH)
    return rpm, p_hyd, p_shaft, p_shaft / omega, p_el


print("v      rpm    P_hyd   P_shaft  torque   P_el(MPPT)")
for v in (0.3, 0.5, 1.0, 1.5):
    rpm, ph, ps, tq, pe = at(v)
    print("%.2f  %6.1f  %6.2f W  %6.2f W  %.3f Nm  %7.1f mW"
          % (v, rpm, ph, ps, tq, pe * 1e3))

J = lambda w: w * 86400.0
print()
print("energy per day at 0.5 m/s : %.0f J   -> reserve %.1fx of %.0f J/day"
      % (J(at(0.5)[4]), J(at(0.5)[4]) / NEED_J_DAY, NEED_J_DAY))
print("energy per day at 1.0 m/s : %.0f J   -> reserve %.0fx"
      % (J(at(1.0)[4]), J(at(1.0)[4]) / NEED_J_DAY))

e_win = 0.5 * C_SERIES * (V_MAX**2 - V_MIN**2)
print("supercap window 20 F, %.1f->%.1f V : %.1f J = %.2f days at %.0f J/day"
      % (V_MAX, V_MIN, e_win, e_win / NEED_J_DAY, NEED_J_DAY))

tau_load = at(1.0)[3]
print()
print("rotor load at 1 m/s: %.4f N·m (with seal+viscous losses)" % tau_load)
for gap, slip in ((4.0, 1.062), (4.2, 1.000), (5.0, 0.789)):
    print("  gap %.1f mm: slip %.3f N·m -> %.2fx" % (gap, slip, slip / tau_load))

print()
print("reports per year at 96/day: %d ; SHMU monthly grab: 12" % (96 * 365))
print("check Cp from rotor_check: 0.393 at TSR 5 alpha 5 (7.46 W hydraulic at 1 m/s)")
