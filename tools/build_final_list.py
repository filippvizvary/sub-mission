#!/usr/bin/env python3
"""Final buying list for the v1 river probe - generated from docs/PARTS_LIST.csv.

Scope: everything needed for a prototype that runs and sends data over LoRa.
The gateway/receiver owns Web Serial, so no dashboard work is on this list.

Deliberate differences from the CSV (they are decisions, not accidents):
  - C08 generator is the iFlight GM3506 (EU stock, 2-5 day delivery) instead of
    the XTG3506 line, which ships from China. Price and link carried here only.
  - J09 enamel wire is new (prototype of the hand-wound alternator, version B).
  - B05 extra magnets (version B) are an optional block, not a core line.
  - Every shop/price cell except the generator is left empty on purpose: Filip
    and the school pick the shops themselves.

Run: python3 tools/build_final_list.py
Out: docs/final-list.xlsx
"""
import csv
import os

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(HERE, "docs", "PARTS_LIST.csv")
OUT = os.path.join(HERE, "docs", "final-list.xlsx")

# Rows that the CSV still describes wrongly or that changed after a decision.
# They get a price and a link; everything else stays a bare name on purpose.
OVERRIDES = {
    "C08": {
        "name": "Generator - iPower GM3506 gimbal BLDC s encoderom AS5048A",
        "spec": ("24N/22P, 5.6 ohm, 72 g, duta hriadel D12/8.6, no-load 2149-2375 rpm "
                 "pri 16 V (KV ~147 rpm/V), 610 mm kabel, dupont konektor"),
        "note": ("Objednat DNES - sklad v Rakusku, GLS/UPS, 2-5 dni. "
                 "Pri 434 rpm: E_ll 2.95 V, ~97 mW. Encoder = RPM/prietok zdarma."),
        "qty": 1,
        "price": 50.90,
        "link_text": "iflight-rc.eu  ->  GM3506 (klikni)",
        "link": "https://iflight-rc.eu/en/products/ipower-gm3506-gimbal-motor-with-encoder",
    },
    "G03": {
        "name": "MCU + radio - Seeed XIAO ESP32S3 + Wio-SX1262 kit (SEE319)",
        "spec": ("ESP32-S3R8 240 MHz, 9x ADC ale 6 pouzitelnych (D0-D5), 11x GPIO, "
                 "SX1262 862-930 MHz, LoRa antena v baleni"),
        "note": ("Radio berie D0-D7 ako riadiace linky? NIE - na S3 kite idu cez spodny "
                 "B2B, takze D0-D5 zostavaju ako ADC. 339 Kc, skladom 5+."),
        "qty": 1,
        "price": 13.90,
        "link_text": "rpishop.cz  SEE319 (klikni)",
        "link": "https://rpishop.cz/?s=Wio-SX1262&post_type=product",
    },
    "I01": {
        "name": "Gateway radio - Seeed XIAO ESP32S3 + Wio-SX1262 kit (SEE319)",
        "spec": "ten isty kit ako v sonde, aby bol firmware identicky",
        "note": "339 Kc, skladom 5+. Spolu 2 ks (sonda + brana).",
        "qty": 1,
        "price": 13.90,
        "link_text": "rpishop.cz  SEE319 (klikni)",
        "link": "https://rpishop.cz/?s=Wio-SX1262&post_type=product",
    },
}

# section key from CSV subsystem -> (order, Slovak heading)
SECTIONS = {
    "rotor":    (1, "1. ROTOR A HRIADEL"),
    "coupling": (2, "2. MAGNETICKA SPOJKA"),
    "pod":      (3, "3. TELESO PODU"),
    "sensors":  (4, "4. SENZORY (prototyp: teplota + TDS + turbidita)"),
    "drybox":   (5, "5. ELEKTRONIKA - SUCHA SCHRANKA"),
    "gateway":  (6, "6. RADIO A GATEWAY"),
    "consumable": (7, "7. MATERIAL A SPOTREBNY"),
    "tooling":  (8, "8. MERANIE A PRIPRAVA"),
    "site":     (9, "9. STAVBA NA BREHU (aby to slo do vody)"),
    "cage":     (3, "3. TELESO PODU"),
    "interface": (3, "3. TELESO PODU"),
}

# rows that are printed in-house: they are listed so nothing looks missing, but
# nobody should try to buy them
PRINTED = {"A01", "A02", "B02", "C01", "C02", "C04", "C09", "E01", "E03", "H06"}

EXTRA_ROWS = [
    ("consumable", "J09", "Lakovany drot 0.5 mm (smaltovany, CUL/DN2E)",
     "50 m na civke - min. 26 m treba na 12 cievok x 18 zavitov", 1,
     "VOLITELNE - len ak stavias verziu s vlastnou cievkou. Nie dekoračny "
     "šperkarsky drot.", "", ""),
    ("coupling", "B05", "Magnet N52 D10x5 - naviac pre verziu s cievkou",
     "D10x5 axialne magnetizovany, 20 ks na celo x 2 cela", 40,
     "VOLITELNE - volna axialna masina, 10 polovych parov, 72 Hz pri 434 rpm.",
     "", ""),
    ("drybox", "G19", "5 V boost pre senzory (TPS61023)",
     "3.3 V -> 5 V, 0.5 A, napaja turbiditu a TDS modul", 1,
     "VOLITELNE: XIAO ma 5 V len z USB. V terene bez tohto boostu turbidita "
     "nepobezi. Na demo z USB netreba.", "", ""),
]

HDR = ["#", "Súčiastka / špecifikácia", "Ks", "Poznámka", "Cena EUR", "Odkaz", "Kúpiť (x)"]

THIN = Side(style="thin", color="D9D9D9")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HEAD_FILL = PatternFill("solid", fgColor="1F3864")
SEC_FILL = PatternFill("solid", fgColor="DCE6F1")
ALT_FILL = PatternFill("solid", fgColor="F7F9FC")
MOTOR_FILL = PatternFill("solid", fgColor="FFF2CC")


def qty_of(row):
    return sum(int(row[k] or 0) for k in ("qty_probe", "qty_site", "qty_gateway"))


def note_of(row):
    bits = []
    if row["owned"] == "YES":
        bits.append("MAS DOMA")
    if row["id"] in PRINTED:
        bits.append("tlaci sa")
    if row["id"] == "B03":
        bits.append("integrovat do bulkheadu, nie samostatny diel")
    n = (row.get("notes") or "").strip()
    if n:
        bits.append(n[:120])
    return " | ".join(bits)


def main():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    by_id = {r["id"]: r for r in rows}
    cut = [r for r in rows if r["phase"] == "cut"]

    buy = {}
    for r in rows:
        if r["phase"] == "1":
            buy.setdefault(r["subsystem"], []).append(r)
    for sub, rid, name, spec, qty, note, price, link in EXTRA_ROWS:
        buy.setdefault(sub, []).append(
            {"id": rid, "subsystem": sub, "part": name, "spec": spec,
             "qty_probe": str(qty), "qty_site": "0", "qty_gateway": "0",
             "owned": "NO", "notes": note, "price_eur": price, "link": link}
        )

    late = {}
    for r in rows:
        if r["phase"] == "2":
            late.setdefault(r["subsystem"], []).append(r)

    wb = Workbook()
    ws = wb.active
    ws.title = "Finalny zoznam"

    ws["A1"] = "SUB-MISSION - finalny zoznam na objednanie"
    ws["A1"].font = Font(bold=True, size=14, color="1F3864")
    ws["A2"] = ("Ciel: prototyp, ktory sa toci, posiela data cez LoRa a drzi vo vode. "
                "Gateway/receiver si Web Serial riesi sam, dashboard nie je na tomto zozname.")
    ws["A3"] = ("Ceny a obchody su zamerne prazdne - vyberate si sami. "
                "Vypnuty je len generator (skladom v EU, treba objednat dnes).")
    for c in ("A2", "A3"):
        ws[c].font = Font(italic=True, size=9, color="595959")

    r = 5
    for i, h in enumerate(HDR, start=1):
        cell = ws.cell(row=r, column=i, value=h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = HEAD_FILL
        cell.alignment = Alignment(horizontal="center", vertical="center")
        cell.border = BOX
    ws.freeze_panes = "A6"
    r += 1

    grouped = {}
    for sub, items in buy.items():
        head = SECTIONS.get(sub, (99, sub))[1]
        grouped.setdefault(head, []).extend(items)
    order = sorted(grouped.items(), key=lambda kv: kv[0])
    n = 0
    for head, items in order:
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(HDR))
        cell = ws.cell(row=r, column=1, value=head)
        cell.font = Font(bold=True, size=10, color="1F3864")
        cell.fill = SEC_FILL
        for c in range(1, len(HDR) + 1):
            ws.cell(row=r, column=c).border = BOX
        r += 1
        for row in items:
            n += 1
            ov = OVERRIDES.get(row["id"])
            name = ov["name"] if ov else f"{row['part']}"
            spec = ov["spec"] if ov else row["spec"]
            note = ov["note"] if ov else note_of(row)
            short = ov["link_text"] if ov else None
            vals = [n, f"{name} - {spec}", ov["qty"] if ov else qty_of(row),
                    note, ov["price"] if ov else None, short, ""]
            for i, v in enumerate(vals, start=1):
                cell = ws.cell(row=r, column=i, value=v)
                cell.border = BOX
                cell.alignment = Alignment(vertical="top",
                                           wrap_text=i in (2, 4),
                                           horizontal="center" if i in (1, 3, 5, 7) else "left")
                if ov:
                    cell.fill = MOTOR_FILL
                    cell.font = Font(bold=True, size=9)
                elif n % 2 == 0:
                    cell.fill = ALT_FILL
                else:
                    cell.font = Font(size=9)
            if ov:
                for col in (2, 6):
                    lc = ws.cell(row=r, column=col)
                    lc.hyperlink = ov["link"]
                    lc.font = Font(color="0563C1", underline="single", size=9, bold=True)
                ws.cell(row=r, column=5).number_format = '0.00 "EUR"'
                ws.cell(row=r, column=5).alignment = Alignment(horizontal="center", vertical="top")
            else:
                ws.cell(row=r, column=2).font = Font(size=9)
                ws.cell(row=r, column=4).font = Font(size=8, color="595959")
            # row height from the longest wrapped cell
            lines = max(len(str(vals[1])) // 60 + 1, len(str(vals[3])) // 45 + 1, 1)
            ws.row_dimensions[r].height = 13 * lines + 3
            r += 1

    # later phases, listed so nothing looks deleted
    r += 1
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(HDR))
    cell = ws.cell(row=r, column=1, value="10. FAZA 2 - NEKUPOVAT TERAZ (pH, DO, hladina, IP68 box, antena, vakua)")
    cell.font = Font(bold=True, size=10, color="7F7F7F")
    cell.fill = SEC_FILL
    for c in range(1, len(HDR) + 1):
        ws.cell(row=r, column=c).border = BOX
    r += 1
    for sub, items in sorted(late.items(), key=lambda kv: SECTIONS.get(kv[0], (99, kv[0]))[0]):
        for row in items:
            n += 1
            vals = [n, f"{row['part']} - {row['spec']}", qty_of(row), note_of(row), None, None, ""]
            for i, v in enumerate(vals, start=1):
                cell = ws.cell(row=r, column=i, value=v)
                cell.border = BOX
                cell.font = Font(size=8, color="808080")
                cell.alignment = Alignment(vertical="top", wrap_text=i in (2, 4),
                                           horizontal="center" if i in (1, 3, 5, 7) else "left")
            ws.row_dimensions[r].height = 13 * (len(str(vals[1])) // 60 + 1) + 3
            r += 1

    # dead lines
    r += 1
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(HDR))
    cell = ws.cell(row=r, column=1, value="11. ZRUSENE - NEKUPOVAT (design ich zabil, uvadzame ich len pre poriadok)")
    cell.font = Font(bold=True, size=10, color="7F7F7F")
    cell.fill = SEC_FILL
    for c in range(1, len(HDR) + 1):
        ws.cell(row=r, column=c).border = BOX
    r += 1
    for row in cut:
        vals = ["-", f"{row['part']} - {row['spec']}", "-", (row.get("notes") or "")[:110], None, None, ""]
        for i, v in enumerate(vals, start=1):
            cell = ws.cell(row=r, column=i, value=v)
            cell.border = BOX
            cell.font = Font(size=8, color="A6A6A6", strike=True)
            cell.alignment = Alignment(vertical="top", wrap_text=i in (2, 4))
        r += 1

    widths = {"A": 4, "B": 62, "C": 5, "D": 46, "E": 11, "F": 26, "G": 8}
    for col, w in widths.items():
        ws.column_dimensions[col].width = w
    ws.sheet_view.showGridLines = False
    ws.print_title_rows = "5:5"
    ws.page_setup.orientation = "portrait"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    # ---- sheet 2: what the generator gives, and what is not on this list ----
    ws2 = wb.create_sheet("Poznamky")
    ws2["A1"] = "Generator GM3506 na nasom rotore (434 rpm pri 1.0 m/s)"
    ws2["A1"].font = Font(bold=True, size=12, color="1F3864")
    data = [
        ("v [m/s]", "rpm", "E_ll [V]", "bus [V]", "P_elec [mW]"),
        (0.3, 130, 0.90, 0.32, 9),
        (0.5, 217, 1.50, 0.89, 25),
        (0.8, 347, 2.39, 1.75, 64),
        (1.0, 434, 2.99, 2.32, 97),
        (1.5, 651, 4.49, 3.75, 225),
    ]
    for i, row in enumerate(data, start=3):
        for j, v in enumerate(row, start=1):
            cell = ws2.cell(row=i, column=j, value=v)
            cell.border = BOX
            cell.alignment = Alignment(horizontal="center")
            if i == 3:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = HEAD_FILL
    ws2["A10"] = "Denná potreba systému: 15-28 J (deep sleep + 96 reportov) -> rezerva 30-300x."
    ws2["A11"] = "Live streaming cez Web Serial (~150 mW) generátor NEUTIAHNE - demo beží z USB, generátor dobíja cap."
    ws2["A12"] = "Cogging, no-load drag a ložiská = zmerat na stole po doručení (gating #1)."

    ws2["A15"] = "Co sa NEKUPUJE - tlaci sa doma"
    ws2["A15"].font = Font(bold=True, size=11, color="1F3864")
    printed = [
        "3x list rotora (ASA), hub D64x46",
        "2x magnetova miska D70 (8 pocketov D10.2x5.2)",
        "valec podu D110x120 + chvost, D106x4 spojkova stena v bulkheade",
        "klietka D130x150, drziaky senzorov, kolimator, lozko generatoru",
        "skrutky a vlozky: heat-set M3/M4 su na zozname ako spotrebny material",
    ]
    for i, t in enumerate(printed, start=16):
        ws2.cell(row=i, column=1, value="- " + t).font = Font(size=9)

    ws2["A23"] = "Co na zozname NIE JE a preco"
    ws2["A23"].font = Font(bold=True, size=11, color="1F3864")
    missing = [
        "dashboard / web - receiver gateway si Web Serial riesi sam",
        "pH, rozpusteny kyslik, hladinova sonda - faza 2 (pH 14-30 dni servis, DO 175 EUR)",
        "Raspberry Pi - mas doma (I02)",
        "antena na sondu - 2 dBi stub je v krabici kitu; lepsia antena patri na branu, faza 2",
    ]
    for i, t in enumerate(missing, start=24):
        ws2.cell(row=i, column=1, value="- " + t).font = Font(size=9)

    ws2.column_dimensions["A"].width = 26
    for col in "BCDE":
        ws2.column_dimensions[col].width = 12
    ws2.sheet_view.showGridLines = False

    wb.save(OUT)
    print(f"wrote {OUT}: {n} rows on the list")
    return n


if __name__ == "__main__":
    main()
