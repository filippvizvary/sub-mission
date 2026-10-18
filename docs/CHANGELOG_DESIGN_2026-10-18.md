# design change log — 2026-10-18, Haven

## What changed after the frontier review (v1 -> v1r1)

1. **Blade twist fixed**: was constant pitch 28deg -> now 28deg at root -> 2deg at tip.
   Reason: at TSR 5.5 tip inflow angle is atan(0.67/5.5) = 6.9deg; a 28deg pitch there
   gives angle-of-attack -12.8deg = braking. Real prop twist, not decoration.
2. **Cogging torque re-classified**: it's a conservative reluctance interaction with
   zero integral over a revolution. It sets cut-in, not running loss. Sim v1 was wrong.
3. **Cut-in model**: now post-stall flat-plate static torque (Hoerner) vs cogging.
4. **Generator model**: line-to-line KV -> per-phase RMS = KE*omega/sqrt(6), 3ph bridge
   bus = 0.955*KE*omega - 2*Vf, max-power-transfer solved against phase resistance,
   copper loss inside the solve. No flat fake eta anywhere.
5. **Rectifier**: eta = vcap/(vcap+2*Vf), no longer a constant 0.9. Boost stage
   (LTC3105-class) engages when bus_raw < vcap.
6. **Bearings on wet shaft**: two PEEK bushings in a 316SS carrier tube, 31mm apart,
   flanged for axial preload. Rotor was previously hanging on magnetic attraction alone.
7. **Magnet cups**: N52 -> canned N52 (stainless can) after corrosion review.
8. **Weed/debris guard ring added upstream of rotor** (F6).
9. **Yaw strut added to arm** (vortex-shedding flutter mitigation).
10. **TL431 clamp + 3.3R dump resistor** added on the supercap bus (F8).
11. **MS5837 aliasing weather pressure** -> barometer in dry box must be outside the
    potted volume (BME280 inside a sealed box cannot serve this) — open action.
12. **pH/EC no longer galvanically isolated** — probe floats; sequential load-switching
    of the two front-ends removes ground loops for much cheaper.

## Key sim v3 numbers (computed; nothing measured)

- Cp_eff 0.335 with twist fix at TSR 5.5.
- Cut-in 0.13 m/s (cog-limited, assumed 2mNm).
- Net positive daily energy from v >= ~0.45 m/s.
- Supercap autonomy when flow dies: ~2-3 days at 15-min sense+TX cadence.
- LoRa 868 SF12 14 dBm effective range 11-13 km; bounded by radio horizon, not link budget.

## The hard honesty ledger (v0 + design)

- Generator still has not powered the board.
- No cogging, slip-torque, or Cp measurement exists.
- No river test ever.
- Vortex-ingestion risk at 420mm depth (0.35*D below surface of blade tip) is flagged
  as HIGH by the adversarial review and needs a depth margin decision before build.
