#!/usr/bin/env python3
"""
Adds the phase-1 buying sheet to sub-mission_parts.xlsx.

PARTS_LIST.csv carries a `phase` column:
  1    = buy now (the order being placed)
  2    = later phase (site structure, gateway, pH, DO, tooling)
  cut  = dead line (superseded by the CAD or killed by a design decision)

This sheet is the phase-1 order grouped by shop, with no spares added, so the
total is what actually leaves the account. Shipping is NOT in the CSV, so it is
estimated separately at the bottom.

Run after build_parts_xlsx.py:
  PYTHONPATH=~/.local/lib/python3.14/site-packages /usr/bin/python3 tools/build_order_v1.py
"""
import csv
from collections import OrderedDict, defaultdict

from openpyxl import load_workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

XLSX = "/home/filip/sub-mission/docs/sub-mission_parts.xlsx"
CSV = "/home/filip/sub-mission/docs/PARTS_LIST.csv"
SHEET = "Order v1 (now)"

SHIPPING_EST = 25.0          # EUR, ~6 shops, nothing in the CSV covers it

SHOPS = [("tme.eu", "TME"), ("sensorsone", "sensorsone (quote)"),
         ("techfun", "techfun.sk"), ("prusa", "Prusa3D"),
         ("x-teamrc", "x-teamrc.com"), ("tmotor", "T-Motor"),
         ("magsy", "magsy.sk"), ("supermagnet", "supermagneticshop"),
         ("neven", "neven.cz"), ("nerezmaterial", "nerezmaterial.cz"),
         ("laskakit", "laskakit.cz"), ("jlcpcb", "JLCPCB"),
         ("local", "local / shop"), ("printed", "printed in-house"),
         ("in CAD", "in CAD")]

thin = Side(style="thin", color="BFBFBF")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)
C_HEAD, C_SHOP, C_TOT = "1F3864", "2E5C8A", "C6E0B4"


def n(x):
    try:
        return float(x)
    except Exception:
        return 0.0


def shop_of(src):
    s = (src or "").lower()
    for key, name in SHOPS:
        if key in s:
            return name
    return "local / shop"


def main():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    p1 = [r for r in rows if r.get("phase") == "1"]

    by_shop = defaultdict(list)
    by_id = {}
    for r in p1:
        by_id[r["id"]] = r
        by_shop[shop_of(r["source"])].append(r)

    wb = load_workbook(XLSX)
    if SHEET in wb.sheetnames:
        del wb[SHEET]
    ws = wb.create_sheet(SHEET, 0)

    ws["A1"] = "sub-mission phase 1 order - %s" % "PARTS_LIST.csv, phase=1"
    ws["A1"].font = Font(bold=True, size=14, color=C_HEAD)
    ws["A2"] = ("Grouped by shop because that is how it gets ordered. "
                "No spares added here; shipping is not in the CSV and is "
                "estimated at the bottom.")
    ws["A2"].font = Font(italic=True, size=9)

    hdr = ["ID", "Part", "Spec", "Qty", "Unit EUR", "Total EUR", "Status", "Notes"]
    row = 4
    for sh in sorted(by_shop, key=lambda k: -sum(n(x["price_eur"]) * n(x["qty_probe"])
                                                 for x in by_shop[k])):
        items = sorted(by_shop[sh], key=lambda x: -n(x["price_eur"]) * n(x["qty_probe"]))
        sub = sum(n(x["price_eur"]) * n(x["qty_probe"]) for x in items)
        ws.cell(row=row, column=1, value="%s   -   %.2f EUR" % (sh.upper(), sub))
        for c in range(1, 9):
            cell = ws.cell(row=row, column=c)
            cell.fill = PatternFill("solid", fgColor=C_SHOP)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.border = BORDER
        row += 1
        for c, h in enumerate(hdr, start=1):
            cell = ws.cell(row=row, column=c, value=h)
            cell.fill = PatternFill("solid", fgColor="D9E2F3")
            cell.font = Font(bold=True, size=9)
            cell.border = BORDER
        row += 1
        for x in items:
            q, p = n(x["qty_probe"]), n(x["price_eur"])
            vals = [x["id"], x["part"], x["spec"], int(q), p, round(q * p, 2),
                    x["status"], x["notes"]]
            for c, v in enumerate(vals, start=1):
                cell = ws.cell(row=row, column=c, value=v)
                cell.border = BORDER
                cell.font = Font(size=9)
                cell.alignment = Alignment(vertical="top", wrap_text=c in (3, 8))
                if c in (5, 6):
                    cell.number_format = '#,##0.00'
            row += 1
        row += 1

    goods = sum(n(r["price_eur"]) * n(r["qty_probe"]) for r in p1)
    row += 1
    for label, val, bold in (("GOODS SUBTOTAL", goods, True),
                             ("shipping, estimated (not in CSV)", SHIPPING_EST, False),
                             ("LANDED", goods + SHIPPING_EST, True)):
        ws.cell(row=row, column=5, value=label).font = Font(bold=bold, size=10)
        cell = ws.cell(row=row, column=6, value=round(val, 2))
        cell.number_format = '#,##0.00 "EUR"'
        cell.font = Font(bold=bold, size=10)
        cell.fill = PatternFill("solid", fgColor=C_TOT)
        cell.border = BORDER
        row += 1

    row += 1
    ws.cell(row=row, column=1, value="NOT in this order").font = Font(bold=True, size=11)
    row += 1
    for phase, title in (("2", "phase 2 - later"),
                         ("cut", "cut - dead line, do not buy")):
        ids = [r for r in rows if r.get("phase") == phase]
        ws.cell(row=row, column=1, value=title).font = Font(bold=True, size=9)
        row += 1
        for r in ids:
            val = "   %-4s %-46s %8s EUR" % (r["id"], r["part"][:46],
                                             r["price_eur"] if r["price_eur"] not in ("", "-") else "-")
            ws.cell(row=row, column=1, value=val).font = Font(size=9)
            ws.cell(row=row, column=6, value=r["notes"][:90]).font = Font(size=8, italic=True)
            row += 1
        row += 1

    for w, col in zip([6, 30, 52, 6, 9, 10, 11, 62], "ABCDEFGH"):
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A5"
    ws.page_setup.orientation = "landscape"
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0

    wb.save(XLSX)
    print("phase 1: %d lines, goods %.2f + shipping %.2f = %.2f EUR"
          % (len(p1), goods, SHIPPING_EST, goods + SHIPPING_EST))


if __name__ == "__main__":
    main()
