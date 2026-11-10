#!/usr/bin/env python3
"""Final buying list for the v1 river probe - generated from docs/PARTS_LIST.csv.

Usage:
    python3 tools/build_final_list.py          # English part names -> docs/final-list.xlsx
    python3 tools/build_final_list.py --sk     # Slovak text -> docs/finalny-zoznam-sk.xlsx

Scope: everything needed for a prototype that runs and sends data over LoRa.
The gateway/receiver owns Web Serial, so no dashboard work is on this list.

Deliberate differences from the CSV (decisions, not accidents):
  - C08 generator is the iFlight GM3506 (EU stock, 2-5 day delivery). The CSV
    line still says XTG3506 from a China-shipping shop; sync it when convenient.
  - G03/I01 are the ESP32-S3 variant of the Seeed kit (SEE319), not the nRF52840
    one: on the S3 kit the radio control lines go through the B2B connector, so
    D0-D5 stay usable as ADC. The nRF52840 kit uses D0-D5 for those lines.
  - A01 blade spec carries the VALIDATED twist (TSR 5, alpha 5: 38.7 -> 12.6 deg
    from r/R 0.2 to the tip per sim/rotor_check.py), not the stale 28/2 table.
  - J09 enamel wire, B05 extra magnets and G19 5 V boost are optional lines.

Run: python3 tools/build_final_list.py [--sk]
"""
import csv
import os
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV = os.path.join(HERE, "docs", "PARTS_LIST.csv")

SK = "--sk" in sys.argv
OUT = os.path.join(HERE, "docs", "finalny-zoznam-sk.xlsx" if SK else "final-list.xlsx")

# ---------------------------------------------------------------- decisions ---
# Rows that changed after a decision or that the CSV describes wrongly.
# These get a price and a link; every other row stays a bare name on purpose.
OVERRIDES = {
    "C08": {
        "name": "Generátor - iPower GM3506 gimbal BLDC s encoderom AS5048A",
        "spec": ("24N/22P, 5,6 ohm, 72 g, dutá hriadeľ Ø12/8,6, no-load 2149-2375 rpm "
                 "pri 16 V (KV ~147 rpm/V), 610 mm kábel, dupont konektor"),
        "note": ("Objednať DNES - sklad v Rakúsku, GLS/UPS, 2-5 dní. "
                 "Pri 434 rpm: E_ll 2,95 V, ~97 mW. Encoder = RPM/prietok zdarma."),
        "qty": 1,
        "price": 50.90,
        "link_text": "iflight-rc.eu  ->  GM3506 (klikni)",
        "link": "https://iflight-rc.eu/en/products/ipower-gm3506-gimbal-motor-with-encoder",
    },
    "G03": {
        "name": "MCU + rádio - Seeed XIAO ESP32S3 + Wio-SX1262 kit (SEE319)",
        "spec": ("ESP32-S3R8 240 MHz, 9x ADC ale 6 použiteľných (D0-D5), 11x GPIO, "
                 "SX1262 862-930 MHz, LoRa anténa v balení"),
        "note": ("339 Kč, skladom 5+. Riadenie rádiа ide cez zadný B2B konektor, "
                 "preto D0-D5 zostávajú ako ADC. D8/D9/D10 sú SPI rádiа."),
        "qty": 1,
        "price": 13.90,
        "link_text": "rpishop.cz  SEE319 (klikni)",
        "link": "https://rpishop.cz/?s=Wio-SX1262&post_type=product",
    },
    "I01": {
        "name": "Rádio brány - Seeed XIAO ESP32S3 + Wio-SX1262 kit (SEE319)",
        "spec": "ten istý kit ako v sonde, aby bol firmware identický",
        "note": "339 Kč, skladom 5+. Spolu 2 ks (sonda + brána).",
        "qty": 1,
        "price": 13.90,
        "link_text": "rpishop.cz  SEE319 (klikni)",
        "link": "https://rpishop.cz/?s=Wio-SX1262&post_type=product",
    },
}

# --------------------------------------------------------------- Slovak text --
# id -> (nazov, specifikacia). Specs keep the numbers, part numbers and units;
# only the wording is translated.
SK_ROWS = {
    "A01": ("List rotora", "NACA4412, D220 mm, TSR 5, uhol 38,7° na päte -> 12,6° na hrote"),
    "A02": ("Náboj rotora", "Ø64x46 mm, 2x zalisovaná vložka M4, diera Ø5 H7"),
    "A03": ("Mokrý hriadeľ", "316L Ø5 h6 x 115 mm, brúsená, 2 plôšky na koncoch"),
    "A04": ("Mokré ložisko", "klzné puzdro igus iglidur J, 5x7x5 mm (JSM-0507-05)"),
    "A06": ("Zaisťovacia skrutka", "M4x8, 316SS, hrot s dôlkom (ISO 4029)"),
    "B01": ("Magnet", "N52 Ø10x5, axiálne magnetizovaný, epoxidom zaliate"),
    "B02": ("Magnetová miska", "Ø70, 8 puzdier Ø10,2x5,2, tlačená ASA"),
    "B03": ("Prepadová stena", "Ø106 x 4 mm, súčasť prepážky podu, nie samostatný diel"),
    "B04": ("Zalievácia hmota", "3M Scotch-Weld DP270 čierna, 25 ml"),
    "C01": ("Valec podu", "Ø110x120 mm, ASA 2,4 mm + epoxidová bariéra"),
    "C02": ("Zadný kužeľ", "tlačený, integrálny s valcom"),
    "C03": ("O-krúžok podu", "NBR 70, Ø100x2,5"),
    "C04": ("Drážka pre O-krúžok", "2,2 mm šírka x 1,8 mm hĺbka, v okraji podu"),
    "C05": ("Skrutky svorníka podu", "M4x30 A4 + podložky"),
    "C06": ("Sikativ", "5 g silikagél s indikátorom"),
    "C07": ("Káblová priechodka - mokrá strana", "Lapp Skintop MS-M 12x1,5 + Scotchcast 2131"),
    "C09": ("Držiak generátora", "tlačený + 4x M3x8 A4"),
    "D04": ("Teplota vody", "DS18B20, vodotesný, 1 m kábel"),
    "D06": ("Vodivosť / TDS", "DFRobot SEN0244 Gravity, analógový modul + sonda"),
    "D07": ("Zákal", "DFRobot SEN0189, analógový výstup 0-4,5 V"),
    "E01": ("Klietka senzorov", "Ø130x150, tlačená ASA, 12 drážok"),
    "E02": ("Spojovací materiál klietky", "M3x10 A4 + samosvorné matice"),
    "E03": ("Úchytky senzorov", "tlačené pre pH / TDS / zákal / teplotu / hladinu"),
    "F01": ("Kábel", "8x0,5 mm² PUR, ponorný, 6 m"),
    "F02": ("Priechodka do prepážky", "zaliata priechodka (nie SubConn)"),
    "G04": ("Anténa na sondu", "868 MHz 5 dBi, SMA, omni, 195 mm"),
    "G05": ("Pigtail u.FL -> SMA", "u.FL (IPEX) -> SMA, 10-15 cm, RG178"),
    "G06": ("MPPT boost", "LTC3105EFE"),
    "G07": ("Buck", "TPS62A02DRC, step-down"),
    "G08": ("Usmerňovač", "Nexperia PMEG2010AEB, 20 V 1 A, SOD-523, 6 ks"),
    "G09": ("Clamp", "TL431LIAQ + MJD127T4G + PWR263S 3,3R záťaž"),
    "G10": ("Superkondenzátor", "Eaton XLR-4R0507 LIC, 500 F, 4,0 V"),
    "G11": ("Napäťový supervisor", "TLV840, nanoprúdový"),
    "G12": ("Load switch", "TPS22860, 2 ks, spínanie pH/EC"),
    "G14": ("DPS", "vlastná 2-vrstvová, 60x80 mm"),
    "G15": ("Konektory", "sada JST-PH/XH + krimpy"),
    "G16": ("Ochrany", "poistka 0,5 A + TVS + ESD pole"),
    "G17": ("Káblové priechodky", "M12 IP68 zaliate, 3 ks"),
    "H01": ("Zemná skrutka", "M68 x 800 mm, pre solárne ploty"),
    "H02": ("Stožiar", "lešenárska trubka Ø48,3x3,2 x 3000 mm, pozinkovaná"),
    "H04": ("Rameno", "Al Ø28x1,5 x 1300 mm"),
    "H05": ("Závesná trubka", "Al Ø22x1,5 x 900 mm"),
    "H06": ("Objímka závesu", "tlačená ASA + skrutka M8 A4"),
    "H07": ("Strižný kolík", "M4 316SS + 2 náhradné"),
    "H09": ("Výťažné lano", "3 mm Dyneema 2x4 m + napínaky"),
    "H10": ("Kotva lana", "zemná skrutka 300 mm, 2 ks"),
    "H11": ("Bezpečnostné lanko", "3 mm pozinkované + objímky, istí pod proti stožiaru"),
    "I02": ("Výpočtová jednotka", "Raspberry Pi 4 4GB + zdroj + SD karta"),
    "I05": ("Stožiar brány", "3 m Al stožiar + nástenný držiak"),
    "J01": ("Filament ASA", "Prusament ASA 850 g"),
    "J03": ("Epoxidová bariéra", "West System 105 + 206"),
    "J05": ("Silikónová vazelína", "Molykote 111, 100 g"),
    "J07": ("Zalisované vložky", "mosadzné M3/M4, sada"),
    "K03": ("Pružinová váha", "0-5 N, na meranie sklzu spojky"),
    # fáza 2
    "D01": ("pH elektróda", "DFRobot SEN0161-V2 Gravity pH kit + E201 BNC sonda"),
    "D02": ("Náhradná pH elektróda", "E201-C BNC, 2 ks"),
    "D03": ("pH pufre", "2x 250 ml pH 7 + pH 10"),
    "D09": ("Rozpustený kyslík", "DFRobot SEN0237-A Gravity, 0-20 mg/l, BNC, 2 m"),
    "D05": ("Hladinová sonda", "ponorná IP68 316L, 0-1 m H2O, 0,5-4,5 V, 5 m kábel"),
    "D08": ("Kábel senzorov", "4x2x0,5 mm² tienený PUR, vonkajší"),
    "G01": ("Krabica na brehu", "IP68 hotová, 190x130x80 mm"),
    "G13": ("Barometer", "BME280, mimo zaliatia, v odvetranej komôrke"),
    "H03": ("Objímka prijímača", "Ø52 trubka 300 mm + diery na kolík"),
    "H08": ("Smerová vzpera", "Al Ø22x600 mm + 2 objímky"),
    "H12": ("Bezpečnostný spoj", "jednosmerný Torx M5 + oceľová páska"),
    "H13": ("Štítok lokality", "gravýrovaný, projekt + kontakt"),
    "I03": ("Anténa brány", "MikroTik 868_Omni 6,5 dBi IP66, 862-876 MHz + držiak"),
    "I04": ("Krabica brány", "IP65 + PoE injektor"),
    "I06": ("Koncentrátor (voliteľný)", "RAK2287 SX1302 mini-PCIe + Pi HAT"),
    "J02": ("Filament PC Blend", "Prusament PC Blend 970 g"),
    "J04": ("Konformný lak", "Electrolube akryl, 200 ml"),
    "J06": ("Závitová poistka", "Loctite 243 + 406"),
    "J08": ("Sada O-krúžkov", "NBR metrická sada"),
    "K01": ("Vákuová komora", "Bel-Art F42025 + manometer + pumpa"),
    "K02": ("Momentový skrutkovač", "Wiha 28506, 1,2 Nm"),
    # zrušené
    "A05": ("Nosič ložiska (zrušené)", "316L Ø12xØ8x55 mm"),
    "A07": ("Kruh proti riasam (zrušené)", "Ø250 tlačený prstenec + 3 vzpery"),
    "A08": ("Lanko listu (zrušené)", "3 mm nerez + objímka"),
    "G02": ("MCU ESP32-S3 devkit (zrušené)", "LaskaKit ESP32-S3-DEVKit - v jednoduchej stavbe sa nepoužije"),
    # voliteľné / doplnené
    "J09": ("Lakovaný drôt 0,5 mm", "smaltovaný (CUL/DN2E), 50 m - min. 26 m na 12 cievok"),
    "B05": ("Magnety navyše pre verziu s cievkou", "N52 Ø10x5, 20 ks na čelo x 2 čelá"),
    "G19": ("5 V boost pre senzory", "TPS61023, 3,3 V -> 5 V, 0,5 A"),
}

SK_NOTES = {
    "A01": "TLAČÍ SA | twist je z sim/rotor_check.py (TSR 5, alpha 5), nie stará tabuľka 28°/2°",
    "A02": "TLAČÍ SA | vložky M4 z TME",
    "B02": "TLAČÍ SA | puzdro 10,2 mm = magnet 10 + 0,2 lepidlo",
    "B03": "integrovať do prepážky - odstráni O-krúžok C03 a 4 skrutky cez stenu",
    "C01": "TLAČÍ SA",
    "C02": "TLAČÍ SA",
    "C04": "TLAČÍ SA | ZATIAĽ NIE JE V MODELI - doplniť do podu",
    "C07": "ZATIAĽ NIE JE V MODELI - doplniť boss",
    "C09": "TLAČÍ SA | rozteč dier podľa dielu, ktorý príde",
    "D04": "v modeli ako sensor_ntc",
    "D06": "+-10 % rozsahu je najslabší senzor - použiť ako trend, nie ako meranie",
    "D07": "2:1 delič 10k/10k POVINNÝ, výstup má 4,5 V",
    "E01": "TLAČÍ SA",
    "E03": "TLAČÍ SA",
    "F02": "ušetrené 85 EUR oproti mokrému konektoru",
    "G03": "MÁŠ KÚPIŤ DNES | 339 Kč, skladom 5+",
    "G04": "VOLITEĽNÉ - kit má LoRa anténu v balení; lepšia patrí na bránu",
    "G05": "kit má u.FL, nie SMA - bez pigtailu lepšiu anténu nepripojíš",
    "G10": "NIE gombíkový EDLC (50 ohm ESR zabije TX)",
    "G11": "otvára buck až pri 4,8 V na capu",
    "G12": "odstraňuje potrebu galvanického oddelenia",
    "G19": "VOLITEĽNÉ: XIAO má 5 V len z USB. V teréne bez tohoto boostu zákal nepobeží.",
    "H02": "vyberateľný stožiar, zapichnutý do zemnej skrutky",
    "H07": "povolí pod pri náraze nad ~150 N",
    "H09": "45° hore/dolu prúdu",
    "H11": "proti krádeži a pri povodni",
    "I02": "MÁŠ DOMA - Raspberry Pi 4",
    "I05": "výškou sa kupuje dosah rádia",
    "I06": "len pre viac SF / kanálov / verejnú TTN - nie pre v1",
    "J01": "MÁŠ DOMA - ABS z domáceho spoolu, nie ASA; over UV",
    "J05": "MÁŠ DOMA",
    "J09": "VOLITEĽNÉ - len ak staviaš verziu s vlastnou cievkou. NIE šperkársky drôt.",
    "B05": "VOLITEĽNÉ - voľná axiálna mašina, 10 pólových párov, 72 Hz pri 434 rpm",
    "K01": "nástroj, nie súčiastka - požičať alebo kúpiť",
    "K02": "nástroj, nie diel",
    "D09": "175 EUR, membrána 1-2 mesiace - prvý kandidát na vynechanie",
    "D05": "110 EUR, quote; bez varovania pred povodňou nemá zmysel",
    "D01": "14-30 dní servis - jediný kanál, ktorý nie je 90-dňový",
    "A05": "nahradené tlačeným nosičom",
    "A07": "nahradené nosovým kužeľom - prstenec je kosa na riasy",
    "A08": "lanko na liste je flail, Filip ho sám zamietol",
    "G02": "jedna doska XIAO nahradila dve",
}

SECTIONS = {
    "rotor":    (1, "1. ROTOR A HRIADEĽ"),
    "coupling": (2, "2. MAGNETICKÁ SPOJKA"),
    "pod":      (3, "3. TELESO PODU"),
    "cage":     (3, "3. TELESO PODU"),
    "interface": (3, "3. TELESO PODU"),
    "sensors":  (4, "4. SENZORY (prototyp: teplota + TDS + zákal)"),
    "drybox":   (5, "5. ELEKTRONIKA - SUCHÁ SCHRÁNKA"),
    "gateway":  (6, "6. RÁDIO A BRÁNA"),
    "consumable": (7, "7. MATERIÁL A SPOTREBNÝ"),
    "tooling":  (8, "8. MERANIE A PRÍPRAVA"),
    "site":     (9, "9. STAVBA NA BREHU (aby to šlo do vody)"),
}

PRINTED = {"A01", "A02", "B02", "C01", "C02", "C04", "C09", "E01", "E03", "H06"}

# rows that exist only in this list, not in the CSV: (subsystem, id, qty)
EXTRA_ROWS = [
    ("consumable", "J09", 1),
    ("coupling", "B05", 40),
    ("drybox", "G19", 1),
]

HDR = ["#", "Súčiastka / špecifikácia", "Ks", "Poznámka", "Cena (EUR)", "Odkaz", "Kúpiť (x)"]

THIN = Side(style="thin", color="D9D9D9")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
HEAD_FILL = PatternFill("solid", fgColor="1F3864")
SEC_FILL = PatternFill("solid", fgColor="DCE6F1")
ALT_FILL = PatternFill("solid", fgColor="F7F9FC")
MARK_FILL = PatternFill("solid", fgColor="FFF2CC")


def qty_of(row):
    return sum(int(row[k] or 0) for k in ("qty_probe", "qty_site", "qty_gateway"))


def note_of(row):
    if row["id"] in SK_NOTES:
        return SK_NOTES[row["id"]]
    bits = []
    if row["owned"] == "YES":
        bits.append("MÁŠ DOMA")
    if row["id"] in PRINTED:
        bits.append("TLAČÍ SA")
    return " | ".join(bits)


def main():
    rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
    missing = [r["id"] for r in rows if r["id"] not in SK_ROWS and r["id"] not in OVERRIDES]
    if missing:
        raise SystemExit(f"no Slovak text for: {', '.join(missing)}")

    buy, late = {}, {}
    for r in rows:
        bucket = buy if r["phase"] == "1" else late if r["phase"] == "2" else None
        if bucket is not None:
            bucket.setdefault(r["subsystem"], []).append(r)
    cut = [r for r in rows if r["phase"] == "cut"]
    for sub, rid, qty in EXTRA_ROWS:
        buy.setdefault(sub, []).append(
            {"id": rid, "subsystem": sub, "part": SK_ROWS[rid][0],
             "spec": SK_ROWS[rid][1], "qty_probe": str(qty), "qty_site": "0",
             "qty_gateway": "0", "owned": "NO", "notes": ""}
        )

    wb = Workbook()
    ws = wb.active
    ws.title = "Finálny zoznam"

    ws["A1"] = "SUB-MISSION - finálny zoznam na objednanie"
    ws["A1"].font = Font(bold=True, size=14, color="1F3864")
    ws["A2"] = ("Cieľ: prototyp, ktorý sa točí, posiela dáta cez LoRa a drží vo vode. "
                "Brána si Web Serial rieši sama, dashboard na tomto zozname nie je.")
    ws["A3"] = ("Ceny a obchody sú zámerne prázdne - vyberáte si sami. "
                "Vypnutý je len generátor a rádio (skladom v EÚ, objednať dnes).")
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

    n = 0
    for head, items in sorted(grouped.items()):
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
            name, spec = (ov["name"], ov["spec"]) if ov else SK_ROWS[row["id"]]
            note = ov["note"] if ov else note_of(row)
            qty = ov["qty"] if ov else qty_of(row)
            vals = [n, f"{name} - {spec}", qty, note,
                    ov["price"] if ov else None,
                    ov["link_text"] if ov else None, ""]
            for i, v in enumerate(vals, start=1):
                cell = ws.cell(row=r, column=i, value=v)
                cell.border = BOX
                cell.alignment = Alignment(vertical="top", wrap_text=i in (2, 4),
                                           horizontal="center" if i in (1, 3, 5, 7) else "left")
                if ov:
                    cell.fill = MARK_FILL
                    cell.font = Font(bold=True, size=9)
                elif n % 2 == 0:
                    cell.fill = ALT_FILL
                    cell.font = Font(size=9)
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
                ws.cell(row=r, column=4).font = Font(size=8, color="595959")
            lines = max(len(str(vals[1])) // 60 + 1, len(str(vals[3])) // 45 + 1, 1)
            ws.row_dimensions[r].height = 13 * lines + 3
            r += 1

    def banner(text, r):
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=len(HDR))
        cell = ws.cell(row=r, column=1, value=text)
        cell.font = Font(bold=True, size=10, color="7F7F7F")
        cell.fill = SEC_FILL
        for c in range(1, len(HDR) + 1):
            ws.cell(row=r, column=c).border = BOX
        return r + 1

    r += 1
    r = banner("10. FÁZA 2 - NEKUPOVAŤ TERAZ (pH, rozpustený kyslík, hladina, IP68 krabica, anténa)", r)
    for sub, items in sorted(late.items(), key=lambda kv: SECTIONS.get(kv[0], (99, kv[0]))[0]):
        for row in items:
            n += 1
            name, spec = SK_ROWS[row["id"]]
            vals = [n, f"{name} - {spec}", qty_of(row), note_of(row), None, None, ""]
            for i, v in enumerate(vals, start=1):
                cell = ws.cell(row=r, column=i, value=v)
                cell.border = BOX
                cell.font = Font(size=8, color="808080")
                cell.alignment = Alignment(vertical="top", wrap_text=i in (2, 4),
                                           horizontal="center" if i in (1, 3, 5, 7) else "left")
            ws.row_dimensions[r].height = 13 * (len(str(vals[1])) // 60 + 1) + 3
            r += 1

    r += 1
    r = banner("11. ZRUŠENÉ - NEKUPOVAŤ (design ich zabil, uvádzame ich len pre poriadok)", r)
    for row in cut:
        name, spec = SK_ROWS[row["id"]]
        vals = ["-", f"{name} - {spec}", "-", note_of(row), None, None, ""]
        for i, v in enumerate(vals, start=1):
            cell = ws.cell(row=r, column=i, value=v)
            cell.border = BOX
            cell.font = Font(size=8, color="A6A6A6", strike=True)
            cell.alignment = Alignment(vertical="top", wrap_text=i in (2, 4))
        r += 1

    for col, w in {"A": 4, "B": 62, "C": 5, "D": 46, "E": 11, "F": 26, "G": 8}.items():
        ws.column_dimensions[col].width = w
    ws.sheet_view.showGridLines = False
    ws.print_title_rows = "5:5"
    ws.page_setup.orientation = "portrait"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    # ------------------------------------------------------------- poznámky ---
    ws2 = wb.create_sheet("Poznámky")
    ws2["A1"] = "Generátor GM3506 na našom rotore (434 rpm pri 1,0 m/s)"
    ws2["A1"].font = Font(bold=True, size=12, color="1F3864")
    data = [("v [m/s]", "otáčky", "E_ll [V]", "zbernica [V]", "P_elec [mW]"),
            (0.3, 130, 0.90, 0.32, 9), (0.5, 217, 1.50, 0.89, 25),
            (0.8, 347, 2.39, 1.75, 64), (1.0, 434, 2.99, 2.32, 97),
            (1.5, 651, 4.49, 3.75, 225)]
    for i, row in enumerate(data, start=3):
        for j, v in enumerate(row, start=1):
            cell = ws2.cell(row=i, column=j, value=v)
            cell.border = BOX
            cell.alignment = Alignment(horizontal="center")
            if i == 3:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = HEAD_FILL
    ws2["A10"] = "Denná potreba systému: 15-28 J (deep sleep + 96 reportov) -> rezerva 30-300x."
    ws2["A11"] = "Live streaming cez Web Serial (~150 mW) generátor neutiahne - demo beží z USB, generátor dobíja cap."
    ws2["A12"] = "Cogging, voľnobežný odpor a ložiská = zmerať na stole po doručení (gating #1)."

    ws2["A15"] = "Čo sa NEKUPUJE - tlačí sa doma"
    ws2["A15"].font = Font(bold=True, size=11, color="1F3864")
    for i, t in enumerate([
        "3x list rotora (ASA), náboj Ø64x46",
        "2x magnetová miska Ø70 (8 puzdier Ø10,2x5,2)",
        "valec podu Ø110x120 + kužeľ, prepadová stena Ø106x4 v prepážke",
        "klietka Ø130x150, úchytky senzorov, držiak generátora",
    ], start=16):
        ws2.cell(row=i, column=1, value="- " + t).font = Font(size=9)

    ws2["A21"] = "Čo na zozname NIE JE a prečo"
    ws2["A21"].font = Font(bold=True, size=11, color="1F3864")
    for i, t in enumerate([
        "dashboard / web - brána si Web Serial rieši sama",
        "pH, rozpustený kyslík, hladinová sonda - fáza 2",
        "Raspberry Pi - máš doma (I02)",
        "lepšia anténa na bránu - až s fázou 2, kit má stub v balení",
    ], start=22):
        ws2.cell(row=i, column=1, value="- " + t).font = Font(size=9)

    ws2.column_dimensions["A"].width = 30
    for col in "BCDE":
        ws2.column_dimensions[col].width = 13
    ws2.sheet_view.showGridLines = False

    wb.save(OUT)
    print(f"wrote {OUT}: {n} rows")


if __name__ == "__main__":
    main()
