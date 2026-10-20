#!/usr/bin/env python3
"""
Build sub-mission_parts.xlsx from docs/PARTS_LIST.csv.

Adds the columns that matter for actually buying things:
  - Optional?            (REQUIRED / OPTIONAL / RECOMMENDED / DROP)
  - Reuse from inventory (YES / CHECK / NO)
  - Install type         (soldered permanent / socketed reusable / printed / mechanical)
Grouped by category, with per-group and grand totals.

Run:  PYTHONPATH=~/.local/lib/python3.14/site-packages /usr/bin/python3 tools/build_parts_xlsx.py
"""
import csv, os
from collections import OrderedDict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

CSV = "/home/filip/sub-mission/docs/PARTS_LIST.csv"
OUT = "/home/filip/sub-mission/docs/sub-mission_parts.xlsx"

CATS = OrderedDict([
    ("rotor",     "1. Rotor & drivetrain (wet side)"),
    ("coupling",  "2. Magnetic coupling"),
    ("pod",       "3. Generator pod & sealing"),
    ("sensors",   "4. Sensors"),
    ("cage",      "5. Sensor cage & mounting"),
    ("interface", "6. Wet-dry interface (cable)"),
    ("drybox",    "7. Electronics (dry box)"),
    ("site",      "8. Structure & site"),
    ("gateway",   "9. Gateway (base station)"),
    ("consumable","10. Consumables"),
    ("tooling",   "11. Tooling (one-off)"),
])

# id -> (optional flag, reuse flag, install type, note override)
OVR = {
    "A01": ("REQUIRED", "NO", "printed", "blade is the mechanical fuse; carry 2 spares"),
    "A02": ("REQUIRED", "NO", "printed", ""),
    "A08": ("DROP", "NO", "mechanical", "REMOVED: wire lanyard becomes a flail at 250 rpm, and the hole is a stress riser"),
    "B01": ("REQUIRED", "NO", "permanent (potted)", "must be canned/epoxy - bare N52 corrodes in weeks"),
    "B03": ("REQUIRED", "NO", "machined", "solid 5 mm wall, no penetration"),
    "C07": ("REQUIRED", "NO", "permanent (potted)", ""),
    "C08": ("REQUIRED", "CHECK", "mechanical", "check your motor box first - v0 used a robot motor"),
    "D01": ("OPTIONAL", "NO", "mechanical", "pH is the fragile channel: 14-30 day service"),
    "D02": ("OPTIONAL", "NO", "consumable", "spare electrode"),
    "D03": ("OPTIONAL", "NO", "consumable", "buffers"),
    "D04": ("REQUIRED", "CHECK", "mechanical", "you have NTC 10K from v0, not DS18B20"),
    "D05": ("RECOMMENDED", "NO", "mechanical", "replaces MS5837 (which must dry daily)"),
    "D06": ("REQUIRED", "NO", "mechanical", "weakest accuracy in set (+-10% FS)"),
    "D07": ("REQUIRED", "CHECK", "mechanical", "v0 already has one - reuse if still working"),
    "D09": ("RECOMMENDED", "NO", "mechanical", "highest-value channel; but 30-day membrane service"),
    "F01": ("REQUIRED", "NO", "permanent", ""),
    "F02": ("REQUIRED", "NO", "permanent (potted)", ""),
    "G01": ("REQUIRED", "NO", "mechanical", "ready-made IP68 box, do not print"),
    "G02": ("REQUIRED", "CHECK", "socketed reusable", "you have classic ESP32 devkits; S3 is different"),
    "G03": ("REQUIRED", "NO", "socketed reusable", ""),
    "G04": ("REQUIRED", "NO", "mechanical", ""),
    "G05": ("REQUIRED", "NO", "socketed reusable", ""),
    "G06": ("REQUIRED", "NO", "soldered permanent", ""),
    "G07": ("REQUIRED", "NO", "soldered permanent", ""),
    "G08": ("REQUIRED", "NO", "soldered permanent", ""),
    "G09": ("REQUIRED", "NO", "soldered permanent", ""),
    "G10": ("REQUIRED", "NO", "soldered permanent", "LIC, not coin-cell EDLC (50 ohm ESR)"),
    "G11": ("REQUIRED", "NO", "soldered permanent", ""),
    "G12": ("REQUIRED", "NO", "soldered permanent", ""),
    "G13": ("REQUIRED", "CHECK", "socketed reusable", "BME280 modules are common in a parts box"),
    "G14": ("REQUIRED", "NO", "soldered permanent", "panel of 10 amortises"),
    "G15": ("REQUIRED", "CHECK", "mechanical", "you likely have JST/dupont assortments"),
    "G16": ("REQUIRED", "NO", "soldered permanent", ""),
    "G17": ("REQUIRED", "NO", "permanent (potted)", ""),
    "H01": ("REQUIRED", "NO", "mechanical", "1-2 kN lateral: this is what survives floods"),
    "H02": ("REQUIRED", "CHECK", "mechanical", "scaffold tube - any builder's merchant"),
    "H03": ("REQUIRED", "NO", "machined", ""),
    "H04": ("REQUIRED", "CHECK", "mechanical", ""),
    "H05": ("REQUIRED", "CHECK", "mechanical", ""),
    "H06": ("REQUIRED", "NO", "printed", ""),
    "H07": ("REQUIRED", "NO", "mechanical", "shear pin releases pod on debris hit"),
    "H08": ("RECOMMENDED", "NO", "mechanical", "anti-flutter strut; drop only if arm is very stiff"),
    "H09": ("REQUIRED", "NO", "mechanical", ""),
    "H10": ("REQUIRED", "NO", "mechanical", ""),
    "H11": ("REQUIRED", "NO", "mechanical", "anti-theft / anti-loss tether"),
    "H12": ("RECOMMENDED", "NO", "mechanical", "anti-theft"),
    "H13": ("RECOMMENDED", "NO", "mechanical", "label makes it unsellable"),
    "I01": ("REQUIRED", "NO", "socketed reusable", "single-channel Wio-E5 gateway: same radio as the probe, no concentrator needed"),
    "I06": ("OPTIONAL", "NO", "socketed reusable", "RAK2287 concentrator + Pi HAT, only for multi-SF/public TTN; module alone will not fit a Pi"),
    "I02": ("REQUIRED*", "YES", "socketed reusable", "YOU ALREADY HAVE THIS - reuse, zero soldering"),
    "I03": ("REQUIRED*", "NO", "mechanical", "range-critical part"),
    "I04": ("REQUIRED*", "CHECK", "mechanical", ""),
    "I05": ("REQUIRED*", "CHECK", "mechanical", ""),
    "J01": ("REQUIRED", "CHECK", "consumable", "you may only have PETG/PLA - ASA needed for UV/water"),
    "J02": ("REQUIRED", "CHECK", "consumable", ""),
    "J03": ("REQUIRED", "NO", "consumable", ""),
    "J04": ("REQUIRED", "NO", "consumable", ""),
    "J05": ("REQUIRED", "CHECK", "consumable", ""),
    "J06": ("REQUIRED", "CHECK", "consumable", ""),
    "J07": ("REQUIRED", "CHECK", "consumable", ""),
    "J08": ("REQUIRED", "CHECK", "consumable", ""),
    "K01": ("RECOMMENDED", "CHECK", "reusable tool", "acceptance test rig; borrow if possible"),
    "K02": ("RECOMMENDED", "CHECK", "reusable tool", ""),
    "K03": ("RECOMMENDED", "CHECK", "reusable tool", "needed for cogging/slip measurement"),
}

HDR = ["ID", "Part", "Spec", "Qty", "Source", "Unit EUR", "Total EUR",
       "Optional?", "Reuse from inventory?", "Install type", "Status", "Notes"]

C_HEAD = "1F3864"; C_GROUP = "2E5C8A"; C_TOTAL = "D9E2F3"
C_OPT = "FFF2CC"; C_REUSE = "E2EFDA"; C_DROP = "F2F2F2"

thin = Side(style="thin", color="BFBFBF")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)


def load():
    rows = list(csv.DictReader(open(CSV)))
    out = []
    for r in rows:
        opt, reuse, install, note = OVR.get(r["id"], ("REQUIRED", "NO", "mechanical", ""))
        notes = (note + (" | " + r["notes"] if note and r["notes"] else r["notes"])) if (note or r["notes"]) else ""
        try:
            unit = float(r["price_eur"])
        except ValueError:
            unit = 0.0
        qty = (float(r["qty_probe"] or 0) + float(r["qty_site"] or 0)
               + float(r["qty_gateway"] or 0))
        out.append(dict(id=r["id"], cat=r["subsystem"], part=r["part"], spec=r["spec"],
                        qty=qty, src=r["source"], unit=unit,
                        opt=opt, reuse=reuse, install=install, status=r["status"], notes=notes))
    return out


def build():
    rows = load()
    wb = Workbook()
    ws = wb.active
    ws.title = "Parts list"

    ws.merge_cells("A1:L1")
    ws["A1"] = "sub-mission river probe - parts list (v1)"
    ws["A1"].font = Font(size=14, bold=True, color="FFFFFF")
    ws["A1"].fill = PatternFill("solid", fgColor=C_HEAD)
    ws["A1"].alignment = Alignment(vertical="center")
    ws.row_dimensions[1].height = 26

    ws.merge_cells("A2:L2")
    ws["A2"] = ("Prices in EUR incl. VAT where listed. REUSE column: YES = you already own it and it needs no "
                "soldering; CHECK = look in your box first; NO = must be bought. Install type 'soldered permanent' "
                "= cannot come from inventory once used.")
    ws["A2"].font = Font(size=9, italic=True, color="404040")
    ws["A2"].alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[2].height = 30

    r = 4
    for col, name in enumerate(HDR, start=1):
        c = ws.cell(row=r, column=col, value=name)
        c.font = Font(bold=True, color="FFFFFF", size=10)
        c.fill = PatternFill("solid", fgColor=C_GROUP)
        c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        c.border = BORDER
    ws.row_dimensions[r].height = 28
    header_row = r
    r += 1

    grand_req = grand_opt = grand_reuse = 0.0
    for key, title in CATS.items():
        items = [x for x in rows if x["cat"] == key]
        if not items:
            continue
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=12)
        g = ws.cell(row=r, column=1, value=title)
        g.font = Font(bold=True, size=11, color="FFFFFF")
        g.fill = PatternFill("solid", fgColor="4472A8")
        g.alignment = Alignment(vertical="center", indent=1)
        ws.row_dimensions[r].height = 20
        r += 1

        sub_req = sub_opt = 0.0
        for it in items:
            total = it["unit"] * float(it["qty"] or 0)
            vals = [it["id"], it["part"], it["spec"], float(it["qty"] or 0), it["src"],
                    it["unit"], total, it["opt"], it["reuse"], it["install"], it["status"], it["notes"]]
            for col, v in enumerate(vals, start=1):
                c = ws.cell(row=r, column=col, value=v)
                c.border = BORDER
                c.font = Font(size=9)
                c.alignment = Alignment(vertical="top",
                                        wrap_text=col in (3, 5, 12),
                                        horizontal="center" if col in (4, 6, 7, 8, 9) else "left")
                if col in (6, 7):
                    c.number_format = '#,##0.00 "EUR"'
            if it["opt"] == "OPTIONAL":
                fill = C_OPT
            elif it["opt"] == "DROP":
                fill = C_DROP
            elif it["reuse"] in ("YES", "CHECK"):
                fill = C_REUSE
            else:
                fill = None
            if fill:
                for col in range(1, 13):
                    ws.cell(row=r, column=col).fill = PatternFill("solid", fgColor=fill)
            if it["opt"] == "DROP":
                for col in range(1, 13):
                    ws.cell(row=r, column=col).font = Font(size=9, strike=True, color="808080")
            if it["opt"] in ("REQUIRED", "REQUIRED*"):
                sub_req += total
            elif it["opt"] in ("OPTIONAL", "RECOMMENDED"):
                sub_opt += total
            if it["reuse"] == "YES":
                grand_reuse += total
            r += 1

        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
        c = ws.cell(row=r, column=1, value=f"subtotal - {title.split('. ')[1]}")
        c.font = Font(bold=True, size=9)
        c.alignment = Alignment(horizontal="right")
        c.fill = PatternFill("solid", fgColor=C_TOTAL)
        for col in (6, 7):
            cc = ws.cell(row=r, column=col, value=(sub_req + sub_opt) if col == 7 else None)
            cc.number_format = '#,##0.00 "EUR"'
            cc.font = Font(bold=True, size=9)
            cc.fill = PatternFill("solid", fgColor=C_TOTAL)
            cc.border = BORDER
        for col in range(1, 13):
            ws.cell(row=r, column=col).border = BORDER
        grand_req += sub_req
        grand_opt += sub_opt
        r += 2

    # grand totals
    def total_line(label, value, fill="FFF2CC", bold=True):
        nonlocal r
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=6)
        c = ws.cell(row=r, column=1, value=label)
        c.font = Font(bold=bold, size=10)
        c.alignment = Alignment(horizontal="right")
        c.fill = PatternFill("solid", fgColor=fill)
        cc = ws.cell(row=r, column=7, value=value)
        cc.number_format = '#,##0.00 "EUR"'
        cc.font = Font(bold=bold, size=10)
        cc.fill = PatternFill("solid", fgColor=fill)
        cc.border = BORDER
        for col in range(1, 8):
            ws.cell(row=r, column=col).border = BORDER
        r += 1

    total_line("REQUIRED (everything needed to build and deploy)", grand_req, "DDEBF7")
    total_line("recommended add-ons (DO, level probe, anti-theft, tools)", grand_opt, "FFF2CC")
    total_line("TOTAL if you buy everything", grand_req + grand_opt, "D9E2F3")
    total_line("saved by reusing what you already own", -grand_reuse, "E2EFDA")
    total_line("net if you reuse your Raspberry Pi etc.", grand_req + grand_opt - grand_reuse, "C6E0B4")

    widths = [6, 26, 48, 5, 22, 10, 10, 13, 15, 19, 10, 58]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.freeze_panes = f"C{header_row + 1}"
    ws.auto_filter.ref = f"A{header_row}:L{r - 1}"

    # ---------- summary sheet ----------
    s = wb.create_sheet("Summary")
    s.merge_cells("A1:D1")
    s["A1"] = "Cost by category"
    s["A1"].font = Font(size=13, bold=True, color="FFFFFF")
    s["A1"].fill = PatternFill("solid", fgColor=C_HEAD)
    for col, name in enumerate(["Category", "Required EUR", "Optional EUR", "Items"], start=1):
        c = s.cell(row=3, column=col, value=name)
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor=C_GROUP)
        c.border = BORDER
    rr = 4
    for key, title in CATS.items():
        items = [x for x in rows if x["cat"] == key]
        if not items:
            continue
        req = sum(x["unit"] * float(x["qty"] or 0) for x in items if x["opt"] in ("REQUIRED", "REQUIRED*"))
        opt = sum(x["unit"] * float(x["qty"] or 0) for x in items if x["opt"] in ("OPTIONAL", "RECOMMENDED"))
        for col, v in enumerate([title, req, opt, len(items)], start=1):
            c = s.cell(row=rr, column=col, value=v)
            c.border = BORDER
            if col in (2, 3):
                c.number_format = '#,##0.00 "EUR"'
        rr += 1
    for col in range(1, 5):
        s.cell(row=rr, column=col).border = BORDER
        s.cell(row=rr, column=col).font = Font(bold=True)
    s.cell(row=rr, column=1, value="TOTAL").fill = PatternFill("solid", fgColor="D9E2F3")
    s.cell(row=rr, column=2, value=grand_req).number_format = '#,##0.00 "EUR"'
    s.cell(row=rr, column=3, value=grand_opt).number_format = '#,##0.00 "EUR"'
    for w, col in zip([46, 16, 16, 8], "ABCD"):
        s.column_dimensions[col].width = w

    notes = [
        "",
        "HOW TO READ",
        "REUSE = YES  -> you already own it, no soldering needed (Raspberry Pi 4 for the gateway).",
        "REUSE = CHECK-> look in your parts box before buying (ESP32 devkits, JST, BME280, filament, tools).",
        "Install type 'soldered permanent' -> cannot come from inventory; once built it stays in the board.",
        "OPTIONAL -> pH module only. RECOMMENDED -> DO, level probe, anti-theft, tools.",
        "DROP -> blade lanyard, removed: flail risk plus a stress riser at the blade root.",
        "",
        "SENSOR NOTE",
        "DO (SEN0237-A) is the highest-value channel: the 2021 Budca fish kill was oxygen depletion.",
        "It is also the most maintenance-hungry: membrane 1-2 months in muddy water, so 30-day service.",
        "MS5837-30BA was rejected: datasheet requires the element to be dried daily, 24 h max submersion.",
        "TDS/EC is +-10% FS - a trend indicator, not an absolute measurement.",
    ]
    for n in notes:
        s.cell(row=rr + 2, column=1, value=n).font = Font(size=9, bold=n.isupper(), color="404040")
        rr += 1

    # print setup so it exports/prints as a readable wide table
    for sheet in (ws, s):
        sheet.page_setup.orientation = "landscape"
        sheet.page_setup.paperSize = sheet.PAPERSIZE_A4
        sheet.sheet_properties.pageSetUpPr.fitToPage = True
        sheet.page_setup.fitToWidth = 1
        sheet.page_setup.fitToHeight = 0
    ws.print_title_rows = f"{header_row}:{header_row}"

    wb.save(OUT)
    print("saved", OUT)
    print("required %.2f  optional %.2f  reusable %.2f  total %.2f"
          % (grand_req, grand_opt, grand_reuse, grand_req + grand_opt))


if __name__ == "__main__":
    build()
