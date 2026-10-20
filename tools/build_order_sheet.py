#!/usr/bin/env python3
"""
Adds an "Order (by shop)" sheet to sub-mission_parts.xlsx.

The school orders per shop, so the list must be grouped by supplier, with a
buy-quantity that already includes spares. Spare rule:
  price < 5 EUR      -> +2 pcs   (cheap, breaks, postage costs more than the part)
  5 .. 30 EUR        -> +1 pc
  > 30 EUR           -> +0, except radios/MCU -> +1
"""
import csv, math
from collections import defaultdict
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

XLSX = "/home/filip/sub-mission/docs/sub-mission_parts.xlsx"
CSV = "/home/filip/sub-mission/docs/PARTS_LIST.csv"

SPARE_ALWAYS = {"G03", "I01", "G10", "G01"}   # radio, gateway radio, supercap, enclosure
SKIP = {"A08", "G02"}                          # dropped rows

thin = Side(style="thin", color="BFBFBF")
BORDER = Border(left=thin, right=thin, top=thin, bottom=thin)


def n(x):
    try:
        return float(x)
    except Exception:
        return 0.0


def shop_of(src):
    s = src.lower()
    for key, name in [
        ("techfun", "techfun.sk"), ("laskakit", "laskakit.cz"), ("tme", "TME"),
        ("prusa", "Prusa3D"), ("hornbach", "Hornbach / stavebniny"),
        ("i4wifi", "i4wifi.cz"), ("magsy", "magsy.sk"),
        ("supermagnet", "supermagneticshop"), ("neven", "neven.cz"),
        ("global-ic", "global-ic.sk"), ("botland", "botland.cz"),
        ("components-store", "components-store.cz"), ("rakwireless", "RAK reseller"),
        ("nerezmaterial", "nerezmaterial.cz"), ("jlcpcb", "JLCPCB"),
        ("x-teamrc", "x-teamrc.com"), ("tmotor", "T-Motor"),
        ("sensorsone", "sensorsone (quote)"), ("e-shop.magsy", "magsy.sk"),
    ]:
        if key in s:
            return name
    return "local / other"


# structural / one-off gear does not need spares - you would not buy two masts
NO_SPARE = ("H", "I04", "I05", "I02")


def buy_qty(qty, price, pid):
    q = int(math.ceil(qty))
    if pid.startswith(NO_SPARE):
        return q
    if pid in SPARE_ALWAYS:
        return q + 1
    if price < 5:
        return q + 2
    if price <= 30:
        return q + 1
    return q


def load_flags():
    wb = load_workbook(XLSX)
    ws = wb["Parts list"]
    flags = {}
    for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
        pid = row[0].value
        if isinstance(pid, str) and len(pid) <= 4 and pid[:1].isalpha():
            flags[pid] = row[7].value
    return flags


def build():
    flags = load_flags()
    rows = [r for r in csv.DictReader(open(CSV)) if r["id"] not in SKIP]
    by_shop = defaultdict(list)
    for r in rows:
        qty = n(r["qty_probe"]) + n(r["qty_site"]) + n(r["qty_gateway"])
        if qty <= 0:
            continue
        price = n(r["price_eur"])
        opt = flags.get(r["id"], "REQUIRED")
        bucket = "OPT" if opt in ("OPTIONAL", "RECOMMENDED") else "REQ"
        by_shop[(bucket, shop_of(r["source"]))].append((r, qty, buy_qty(qty, price, r["id"]), price))

    wb = load_workbook(XLSX)
    if "Order (by shop)" in wb.sheetnames:
        del wb["Order (by shop)"]
    s = wb.create_sheet("Order (by shop)", 1)

    s.merge_cells("A1:G1")
    s["A1"] = "ORDER SHEET - grouped by shop, quantities already include spares"
    s["A1"].font = Font(size=13, bold=True, color="FFFFFF")
    s["A1"].fill = PatternFill("solid", fgColor="1F3864")

    hdr = ["ID", "Part", "Qty needed", "BUY THIS", "Unit EUR", "Line EUR", "Note"]
    r0 = 3
    for c, h in enumerate(hdr, start=1):
        cell = s.cell(row=r0, column=c, value=h)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="2E5C8A")
        cell.border = BORDER
        cell.alignment = Alignment(horizontal="center", wrap_text=True)

    r = r0 + 1
    grand = 0.0
    opt_total = 0.0
    for bucket in ("REQ", "OPT"):
        if bucket == "OPT":
            s.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
            cc = s.cell(row=r, column=1,
                        value="OPTIONAL / RECOMMENDED add-ons - order only if budget allows")
            cc.font = Font(bold=True, color="7F6000")
            cc.fill = PatternFill("solid", fgColor="FFF2CC")
            r += 1
        for (b, shop) in sorted([k for k in by_shop if k[0] == bucket],
                                key=lambda k: -sum(x[2] * x[3] for x in by_shop[k])):
            items = by_shop[(b, shop)]
            s.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
            c = s.cell(row=r, column=1, value=shop)
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor="4472A8")
            r += 1
            sub = 0.0
            for item, qty, buy, price in items:
                line = buy * price
                sub += line
                vals = [item["id"], item["part"], qty, buy, price, line, (item["notes"] or "")[:70]]
                for col, v in enumerate(vals, start=1):
                    cell = s.cell(row=r, column=col, value=v)
                    cell.border = BORDER
                    cell.font = Font(size=9)
                    if col in (5, 6):
                        cell.number_format = '#,##0.00 "EUR"'
                    cell.alignment = Alignment(wrap_text=col in (2, 7))
                if buy > qty:
                    s.cell(row=r, column=4).fill = PatternFill("solid", fgColor="E2EFDA")
                r += 1
            s.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
            cell = s.cell(row=r, column=1, value=f"subtotal {shop}")
            cell.font = Font(bold=True, size=9)
            cell.alignment = Alignment(horizontal="right")
            lc = s.cell(row=r, column=6, value=sub)
            lc.number_format = '#,##0.00 "EUR"'
            lc.font = Font(bold=True, size=9)
            lc.border = BORDER
            for col in range(1, 8):
                s.cell(row=r, column=col).fill = PatternFill("solid", fgColor="D9E2F3")
            if bucket == "REQ":
                grand += sub
            else:
                opt_total += sub
            r += 2

    s.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
    cc = s.cell(row=r, column=1,
                value="optional add-ons subtotal: %.2f EUR (DO, depth probe, pH, tools, concentrator)" % opt_total)
    cc.font = Font(bold=True, size=10, color="7F6000")
    cc.fill = PatternFill("solid", fgColor="FFF2CC")
    r += 1

    s.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
    c = s.cell(row=r, column=1, value="GRAND TOTAL to order (required, with spares)")
    c.font = Font(bold=True, size=11)
    c.alignment = Alignment(horizontal="right")
    c.fill = PatternFill("solid", fgColor="C6E0B4")
    c2 = s.cell(row=r, column=6, value=grand)
    c2.number_format = '#,##0.00 "EUR"'
    c2.font = Font(bold=True, size=11)
    c2.fill = PatternFill("solid", fgColor="C6E0B4")
    c2.border = BORDER

    for w, col in zip([6, 30, 10, 10, 10, 10, 62], "ABCDEFG"):
        s.column_dimensions[col].width = w
    s.freeze_panes = "A4"
    s.page_setup.orientation = "landscape"
    s.sheet_properties.pageSetUpPr.fitToPage = True
    s.page_setup.fitToWidth = 1
    s.page_setup.fitToHeight = 0

    wb.save(XLSX)
    print("order sheet: required %.2f EUR | optional %.2f EUR" % (grand, opt_total))


if __name__ == "__main__":
    build()
