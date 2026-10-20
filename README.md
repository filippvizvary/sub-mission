# sub-mission

River water-quality probe for AMAVET. A bank-mounted pole carries a swing arm
over the stream; a sealed pod hangs from it on a drop tube. A 3-blade rotor
drives the generator through a magnetic coupling that works **through a solid
4 mm wall** - no shaft ever pierces the shell. Sensors report over 868 MHz LoRa
to a gateway on a Raspberry Pi.

## Where things are

```
cad/
  probe_cq.py        parametric CadQuery model - the single source of truth
  explode.py         exploded elevation drawings + coupling section (PNG)
  check_overlap.py   clash check between parts
  cq/                GENERATED meshes and STEP  (gitignored)

sim/
  rotor_check.py     BEM + Prandtl: Cp, rpm, torque at a given flow
  clutch_check.py    magnetic coupling: force and slip torque vs gap
  simulate.py        energy budget over a flow cycle

docs/
  DESIGN.md          geometry, joints, sealing, why each choice was made
  BOM.md             bill of materials with sources and prices
  BUILD_PROCEDURE.md nine build phases, each with a gate
  SENSORS.md         which sensors, accuracy, service interval
  parts.xlsx         GENERATED order sheet for the school (by shop, with spares)
  reviews/           external frontier-model design reviews
  legacy/            pre-probe (v0 ESP-NOW) documentation

firmware/
  sender/            PlatformIO project - probe node
  receiver/          PlatformIO project - ESP-NOW -> USB bridge (v0, to be replaced by LoRa)

web/
  3d.html            landing page for the viewer
  scene.html         three.js exploded assembly (materials, labels, slider)
  index.html         v0 serial dashboard
  parts/             GENERATED meshes served to the viewer (gitignored)

tools/
  build_parts_xlsx.py  builds docs/parts.xlsx from docs/PARTS_LIST.csv
  build_order_sheet.py adds the by-shop order sheets
  sync_parts.sh        copy fresh meshes into web/parts and restart the service
archive/            superseded OpenSCAD, old renders, FreeCAD bridge
```

## Build the model

```bash
PYTHONPATH=~/.local/lib/python3.14/site-packages python3 cad/probe_cq.py
tools/sync_parts.sh
```

`probe_cq.py` prints a sensor-fit report and writes STL + STEP per part into
`cad/cq/`. It refuses nothing - if a sensor does not fit the cage, the report
says so before anything is ordered.

## See it

```bash
systemctl --user status submission-web.service
# http://<host>:8899/3d.html
```

Keys: `1` assembled, `2` explode, `3` wide explode, `d` drivetrain,
`s` bank structure. There is also a slider.

## Numbers that matter

| quantity | value | from |
|---|---|---|
| rotor Cp at TSR 5, 1.0 m/s | 0.393 | `sim/rotor_check.py` |
| rotor rpm / shaft power | 434 rpm / 7.46 W | `sim/rotor_check.py` |
| shaft torque | 0.164 N.m | `sim/rotor_check.py` |
| coupling slip torque | 1.00 N.m at 4.2 mm gap | `sim/clutch_check.py` |
| coupling margin | 6.1x | both |
| coupling axial pull | 59.5 N | `sim/clutch_check.py` |

## Open items

- cogging torque of the chosen motor is **not measured**; the cut-in speed
  depends on it (build procedure phase 1)
- coupling slip coefficient (0.6 tangential/axial) is an engineering estimate,
  not a measurement - verify with a spring balance
- pH electrode is a 14-30 day serviceable module, not a 90-day channel
