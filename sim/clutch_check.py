#!/usr/bin/env python3
"""
Magnetic coupling - how much torque can 8 + 8 N52 discs actually carry?

Force model: uniformly magnetised cylinder = two charged discs (magnetic pole
model), exact for the axial force between coaxial discs. Integrated over
radial rings + angular sectors, so no dipole approximation at short range.

Torque model: peak tangential force on a magnet in a ring of alternating
poles is taken as 0.6 x its axial attraction to the opposite cup (typical for
a radial-flux coupling with the flux closed through neighbouring poles).
That factor is the honest weak point - measure the real slip torque with a
spring balance on the bench and replace it.
"""
import math

MU0 = 4 * math.pi * 1e-7
BR = 1.42          # N52 remanence, T (typical 1.42-1.47)
A_MAG = 0.005      # magnet radius, m (D10)
L_MAG = 0.005      # magnet height, m
N_MAG = 8
CUP_D = 0.070      # cup diameter, m
R_PITCH = CUP_D / 2 - 0.005 - 0.002   # magnet pitch radius: 28 mm
K_TAN = 0.6        # tangential / axial force ratio at peak


def disc_force(sigma, r1, r2, z, nr=26, nth=40):
    """Axial force between two coaxial uniformly charged discs (pole model)."""
    if z <= 1e-9:
        return float("inf")
    q1 = sigma * math.pi * r1 ** 2
    q2 = sigma * math.pi * r2 ** 2
    total = 0.0
    dq1 = q1 / (nr * nth)
    dq2 = q2 / (nr * nth)
    for i in range(nr):
        rad1 = r1 * math.sqrt((i + 0.5) / nr)          # equal-area rings
        for j in range(nr):
            rad2 = r2 * math.sqrt((j + 0.5) / nr)
            for a in range(nth):
                t1 = 2 * math.pi * a / nth
                x1, y1 = rad1 * math.cos(t1), rad1 * math.sin(t1)
                for b in range(nth):
                    t2 = 2 * math.pi * b / nth
                    x2, y2 = rad2 * math.cos(t2), rad2 * math.sin(t2)
                    dx, dy = x2 - x1, y2 - y1
                    d2 = dx * dx + dy * dy + z * z
                    d = math.sqrt(d2)
                    total += dq1 * dq2 * z / (4 * math.pi * MU0 * d ** 3)
    return total


def magnet_force(gap):
    """Net axial force between two N52 discs facing each other across `gap`."""
    # magnet A occupies z in [-L,0], magnet B in [gap, gap+L]
    # faces: A top at 0 (+), A bottom at -L (-); B bottom at gap (-), B top gap+L (+)
    top_a, bot_a = 0.0, -L_MAG
    bot_b, top_b = gap, gap + L_MAG
    f = (disc_force(BR, A_MAG, A_MAG, abs(bot_b - top_a))      # +/-
         - disc_force(BR, A_MAG, A_MAG, abs(top_b - top_a))    # +/+
         - disc_force(BR, A_MAG, A_MAG, abs(bot_b - bot_a))    # -/-
         + disc_force(BR, A_MAG, A_MAG, abs(top_b - bot_a)))   # -/+
    return f


def torque(gap):
    f = magnet_force(gap)
    return N_MAG * K_TAN * f * R_PITCH, f


def main():
    print("magnets: %d x N52 D10x5 per cup, pitch radius %.1f mm" % (N_MAG, R_PITCH * 1000))
    print("gap = magnet face to magnet face (wall 5 mm + potting + clearance)\n")
    print("  gap mm   axial force/magnet   slip torque   vs 0.164 Nm load")
    for g_mm in (4.0, 4.2, 5, 6, 7, 8, 10):
        t, f = torque(g_mm / 1000)
        print("  %5.1f    %8.2f N          %6.3f N·m      %5.2fx"
              % (g_mm, f, t, t / 0.164))

    print("\n  wall 4 mm + 0.2 mm epoxy recess each side -> magnets sit")
    print("  4.2 mm apart -> read the 4.2 mm row. Axial pull is what the")
    print("  wet carrier's thrust face has to carry.")


if __name__ == "__main__":
    main()
