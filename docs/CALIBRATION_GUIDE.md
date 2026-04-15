# Calibration Guide

This guide focuses on pH calibration using RAW voltage values from the dashboard.

## 1. Preparation

1. Ensure analog pH output is wired to sender pH pin.
2. Confirm dashboard shows `pH ADC` and `pH Voltage` values.
3. Let sensor stabilize before recording values.

## 2. Collect Calibration Points

Use at least two known buffers (recommended: pH 7.00 and pH 4.00).

For each buffer:

1. Place probe in solution.
2. Wait until RAW voltage is stable.
3. Record `(voltage, known pH)`.

## 3. Compute Linear Calibration

Use:

$$
\text{pH} = mV + b
$$

With two points `(V1, pH1)` and `(V2, pH2)`:

$$
m = \frac{pH2 - pH1}{V2 - V1}, \quad b = pH1 - mV1
$$

## 4. Apply In Firmware

Update constants in `esp-sender/src/main.cpp`:

- `kPhCalibrationSlope`
- `kPhCalibrationOffset`

Rebuild and flash sender.

## 5. Validate

1. Re-test in your known buffers.
2. Check error per point.
3. If needed, re-fit constants with better stabilized readings.

## 6. Notes

1. Rail readings (`ADC=0` or `ADC=4095`) are clipping/saturation and should not be used as calibration points.
2. RAW diagnostics are for calibration; processed pH is only trustworthy after good calibration.
