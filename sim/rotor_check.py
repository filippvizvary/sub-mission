#!/usr/bin/env python3
"""
Rotor check - is the blade actually built for the river it will sit in?

Wilson-Lissaman optimum for a = 1/3, then blade element momentum with
Prandtl tip losses to verify. NACA 4412 polars from a table at Re ~1e5.

Note on the geometry that shipped before this check: the old twist table
gave NEGATIVE angle of attack at every station (blades set against the
flow). This script is what caught it.
"""
import math

RHO = 1000.0
R = 0.110
B = 3
V = 1.0

ALPHA = [-4, 0, 2, 4, 6, 8, 10, 12, 14]
CL = [-0.15, 0.40, 0.63, 0.86, 1.10, 1.30, 1.42, 1.45, 1.30]
CD = [0.020, 0.012, 0.011, 0.012, 0.015, 0.020, 0.030, 0.048, 0.075]


def interp(a, xs, ys):
    if a <= xs[0]:
        return ys[0]
    if a >= xs[-1]:
        return ys[-1]
    for i in range(len(xs) - 1):
        if xs[i] <= a <= xs[i + 1]:
            t = (a - xs[i]) / (xs[i + 1] - xs[i])
            return ys[i] + t * (ys[i + 1] - ys[i])
    return ys[-1]


def polar(al):
    return interp(al, ALPHA, CL), interp(al, ALPHA, CD)


def prandtl(rr, phi):
    f = B / 2 * (1 - rr) / (rr * math.sin(phi) + 1e-6)
    return max(2 / math.pi * math.acos(max(min(math.exp(-f), 1), -1)), 1e-3)


def wilson(tsr, alpha_opt, rrs=(0.20, 0.35, 0.50, 0.65, 0.80, 1.00)):
    """Optimal chord and twist for a = 1/3."""
    cl, _ = polar(alpha_opt)
    out = []
    for rr in rrs:
        lr = tsr * rr
        phi = math.atan((1 - 1 / 3) / lr)
        c = 8 * math.pi * (rr * R) * math.sin(phi) / (3 * B * cl * lr)
        out.append((rr, c, math.degrees(phi) + alpha_opt))
    return out


def bem(st, tsr, n=300):
    r0 = st[0][0]

    def at(rr):
        for i in range(len(st) - 1):
            if st[i][0] <= rr <= st[i + 1][0]:
                t = (rr - st[i][0]) / (st[i + 1][0] - st[i][0])
                return (st[i][1] + t * (st[i + 1][1] - st[i][1]),
                        st[i][2] + t * (st[i + 1][2] - st[i][2]))
        return st[-1][1], st[-1][2]

    omega = tsr * V / R
    P = T = 0.0
    for k in range(n):
        rr = r0 + (1 - r0) * (k + 0.5) / n
        dr = (1 - r0) / n * R
        c, pitch = at(rr)
        r = rr * R
        a, ap = 1 / 3, 0.0
        for _ in range(300):
            phi = math.atan(V * (1 - a) / (omega * r * (1 + ap)))
            cl, cd = polar(pitch - math.degrees(phi))
            cn = cl * math.cos(phi) + cd * math.sin(phi)
            ct = cl * math.sin(phi) - cd * math.cos(phi)
            sig = B * c / (2 * math.pi * r)
            F = prandtl(rr, phi)
            a_n = 1 / ((4 * F * math.sin(phi) ** 2) / (sig * cn) + 1) if sig * cn > 0 else 0.0
            den = (4 * F * math.sin(phi) * math.cos(phi)) / (sig * ct) - 1 if sig * ct > 0 else -0.5
            ap_n = 1 / den if den > 0.001 else 0.0
            a_n = min(max(a_n, 0.0), 0.6)
            ap_n = min(max(ap_n, 0.0), 0.3)
            if abs(a_n - a) < 1e-7 and abs(ap_n - ap) < 1e-7:
                a, ap = a_n, ap_n
                break
            a, ap = 0.7 * a + 0.3 * a_n, 0.7 * ap + 0.3 * ap_n
        phi = math.atan(V * (1 - a) / (omega * r * (1 + ap)))
        cl, cd = polar(pitch - math.degrees(phi))
        cn = cl * math.cos(phi) + cd * math.sin(phi)
        ct = cl * math.sin(phi) - cd * math.cos(phi)
        W = V * (1 - a) / math.sin(phi)
        P += omega * 0.5 * RHO * W ** 2 * B * c * ct * r * dr
        T += 0.5 * RHO * W ** 2 * B * c * cn * dr
    return P / (0.5 * RHO * math.pi * R ** 2 * V ** 3), P, T


def main():
    best = None
    print("  TSR  alpha   Cp      P[W]")
    for tsr in (4, 5, 6, 7):
        for ad in (4, 5, 6, 7):
            st = wilson(tsr, ad)
            cp, P, T = bem(st, tsr)
            print("  %3d  %5.1f  %5.3f  %6.2f" % (tsr, ad, cp, P))
            if 0.15 < cp < 0.5 and (best is None or cp > best[0]):
                best = (cp, tsr, ad, st, P, T)

    cp, tsr, ad, st, P, T = best
    omega = tsr * V / R
    print("\n  chosen: TSR %d, alpha %.0f deg" % (tsr, ad))
    print("  Cp %.3f | shaft %.2f W | thrust %.1f N | %.0f rpm at %.1f m/s"
          % (cp, P, T, omega * 60 / (2 * math.pi), V))
    print("  torque %.3f N·m (coupling slip 0.35 N·m -> %.2fx margin)"
          % (P / omega, 0.35 / (P / omega)))
    print("\n  r/R   chord mm   pitch deg")
    for rr, c, p in st:
        print("  %4.2f   %7.1f    %6.1f" % (rr, c * 1000, p))
    print("\nSTATIONS =", [(rr, round(c * 1000, 1), round(p, 1)) for rr, c, p in st])


if __name__ == "__main__":
    main()
