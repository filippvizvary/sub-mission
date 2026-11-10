#!/usr/bin/env python3
"""Build the quad-chart variants from one layout.

  quad_chart       A - what exists: prototype on USB, harvester never powered it
  quad_chart_b     B - prototype presented as working
  quad_chart_v2    A's facts, restructured per the teacher's feedback + schematic

Shared CSS/layout; each variant supplies Q1, Q2, Q4 and the footer.
Measure every variant before printing (see print-ready-a4-pdf).
"""
from pathlib import Path

HERE = Path(__file__).parent

CSS = """
  @page { size: A4 landscape; margin: 0; }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; }
  body {
    font-family: "Liberation Sans", "DejaVu Sans", sans-serif;
    color: #1c1c1c;
    background: #fbfaf7;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
  .page {
    position: relative;
    width: 297mm; height: 209.8mm;
    background: #fbfaf7;
    overflow: hidden;
  }
  header { position: absolute; top: 7mm; left: 8mm; right: 8mm; border-bottom: 1.6pt solid #1c1c1c; padding-bottom: 2.4mm; }
  .eyebrow {
    font-size: 10pt; letter-spacing: .06em; text-transform: uppercase;
    color: #6b6b6b; margin-bottom: .8mm;
    display: flex; justify-content: space-between;
  }
  h1 {
    font-size: 24pt; line-height: 1.12; font-weight: 700;
    margin: 0 0 1.2mm 0; letter-spacing: -.01em;
  }
  h1 .pname { color: #0b5f8a; letter-spacing: -.005em; }
  h1 .psub { font-weight: 600; color: #1c1c1c; }
  .byline {
    font-size: 12pt; line-height: 1.25; color: #333;
    display: flex; justify-content: space-between;
  }
  .byline b { font-weight: 600; }

  .grid {
    position: absolute; top: 30mm; bottom: 11mm; left: 8mm; right: 8mm;
    display: grid;
    grid-template-columns: 1fr 1fr;
    grid-template-rows: minmax(0,1fr) minmax(0,1fr);
    gap: 3mm;
    min-height: 0;
  }
  .cell {
    border: 0.8pt solid #1c1c1c;
    background: #ffffff;
    padding: 2.4mm 3mm 2.2mm 3mm;
    display: flex; flex-direction: column;
    min-height: 0; overflow: hidden;
  }
  .cell h2 {
    font-size: 12.5pt; font-weight: 700; margin: 0 0 1.6mm 0;
    padding-bottom: 1.2mm; border-bottom: 0.8pt solid #d8d6d0;
  }
  .c-res h2 { border-bottom-color: #b9d3c1; }
  .c-met h2 { border-bottom-color: #c3d5de; }
  .c-int h2 { border-bottom-color: #e0c8ae; }

  ul { margin: 0; padding-left: 4.2mm; }
  li {
    font-size: 12pt; line-height: 1.26; margin-bottom: 1.15mm;
    padding-left: .4mm;
  }
  li::marker { color: #0b5f8a; }
  b { font-weight: 600; }
  .q { font-style: italic; }
  .tag { font-weight: 600; color: #7a1f1f; }

  .schema { margin-top: auto; padding-top: 0.8mm; }
  .schema img { display: block; width: 100%; }

  .figs { flex: 1; display: grid; grid-template-columns: 1.72fr 1fr; gap: 2mm; min-height: 0; }
  .figs .col { display: flex; flex-direction: column; gap: 1mm; min-height: 0; }
  .fig { position: relative; min-height: 0; overflow: hidden; }
  .fig img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: contain; display: block; }
  .cap { font-size: 10pt; line-height: 1.16; color: #545454; margin-top: .6mm; }

  footer {
    position: absolute; left: 8mm; right: 8mm; bottom: 3.6mm;
    padding-top: 1.4mm; border-top: 0.5pt solid #cfcdc7;
    display: flex; justify-content: space-between;
    font-size: 10pt; color: #6b6b6b;
  }
"""

HEADER = """
  <header>
    <div class="eyebrow"><span>Festival vedy a techniky AMAVET 2026 &middot; Robotika a inteligentné stroje</span><span>celoštátne kolo &middot; Bratislava, 16.&ndash;17. 11. 2026</span></div>
    <h1><span class="pname">Sub-Mission</span></h1>
    <div class="byline"><span><b>Filip Vizváry, Šimon Filus</b></span><span>Gymnázium Milana Rúfusa, Žiar nad Hronom</span></div>
  </header>
"""

# ---------------------------------------------------------------- quadrant 1

Q1_A = """
    <div class="cell c-q">
      <h2>Vedecká otázka / Ciele</h2>
      <ul>
        <li><span class="q">D&aacute; sa stanica na monitorovanie kvality vody nap&aacute;ja&#357; v&yacute;hradne z kinetickej energie toku</span> &mdash; bez bat&eacute;rie na v&yacute;menu, bez slnka a bez oper&aacute;tora?</li>
        <li>Rie&scaron;enie: sonda bez k&aacute;bla, bat&eacute;rie aj slnka &mdash; energiu berie z pr&uacute;diacej vody, d&aacute;ta posiela r&aacute;diom.</li>
        <li>&Scaron;t&aacute;tna sie&#357; vzorkuje kvalitu vody pribli&#382;ne <b>raz za mesiac</b>; hydrologick&eacute; stanice ch&eacute;miu nezachytia.</li>
        <li>Bud&#269;a 26. 7. 2021: <b>500 m&sup3;</b> digest&aacute;tu, <b>37 km</b> Hrona, <b>27 t</b> r&yacute;b (25 druhov); nahl&aacute;sili to ryb&aacute;ri o 6:30, nie meracia sie&#357;.</li>
        <li>Ciele: sebesta&#269;nos&#357;, <b>96 meran&iacute; denne</b> namiesto 12 za rok, nasadenie bez z&aacute;suvky a sign&aacute;lu; krit&eacute;ri&aacute;: energia <b>&gt;10&times;</b>, spojka <b>&gt;2,5&times;</b>.</li>
      </ul>
    </div>
"""

Q1_V2 = """
    <div class="cell c-q">
      <h2>Vedecká otázka / Ciele</h2>
      <ul>
        <li><b>V&yacute;skumn&aacute; ot&aacute;zka:</b> <span class="q">Dok&aacute;&#382;e energia pr&uacute;diacej vody pokry&#357; spotrebu sondy na sledovanie kvality vody bez extern&eacute;ho nap&aacute;jania a bez v&yacute;meny bat&eacute;ri&iacute;?</span></li>
        <li><b>Probl&eacute;m:</b> Hav&aacute;ria na Hrone v roku 2021 (<b>500 m&sup3;</b> digest&aacute;tu, <b>37 km</b> toku, <b>27 t</b> r&yacute;b) uk&aacute;zala, &#382;e &scaron;t&aacute;tna sie&#357; vzorkuje vodu len raz za mesiac a zmenu kvality zachyt&iacute; neskoro.</li>
        <li><b>Cie&#318;:</b> Navrhn&uacute;&#357; sondu, ktor&aacute; meria pH, TDS, turbiditu a teplotu vody, pren&aacute;&scaron;a d&aacute;ta r&aacute;diom a energiu na svoju &#269;innos&#357; z&iacute;skava z pr&uacute;diacej vody.</li>
        <li><b>Re&#382;im a krit&eacute;ri&aacute;:</b> <b>96 merac&iacute;ch cyklov denne</b> (ka&#382;d&yacute;ch 15 min&uacute;t); aspo&#328; <b>10-n&aacute;sobn&aacute;</b> energetick&aacute; rezerva a viac ako <b>2,5-n&aacute;sobn&aacute;</b> rezerva momentu magnetickej spojky.</li>
      </ul>
    </div>
"""

# ---------------------------------------------------------------- quadrant 3 (shared)

Q3 = """
    <div class="cell c-res">
      <h2>Dáta a výsledky</h2>
      <div class="figs">
        <div class="col">
          <div class="fig" style="flex:1"><img src="charts/energia.png" alt=""></div>
          <div class="cap">V&yacute;po&#269;et (BEM model rotora + MPPT): v&yacute;kon na hriadeli a z gener&aacute;tora proti r&yacute;chlosti toku. Spotreba 0,32 mW je o 2&ndash;3 r&aacute;dy ni&#382;&scaron;ia.</div>
        </div>
        <div class="col">
          <div class="fig" style="flex:1"><img src="charts/spojka.png" alt=""></div>
          <div class="cap">V&yacute;po&#269;et (magnetostatick&yacute; model): sklzov&yacute; moment spojky proti vzduchovej medzere, proti z&aacute;&#357;a&#382;i rotora 0,16 N&middot;m.</div>
        </div>
      </div>
    </div>
"""

# ---------------------------------------------------------------- quadrant 2

Q2_A = """
    <div class="cell c-met">
      <h2>Metodológia / Návrh projektu</h2>
      <ul>
        <li><b>Bez otvoru pre hriade&#318;:</b> moment pren&aacute;&scaron;a magnetick&aacute; spojka (8 &times; N52 &Oslash;10&times;5) cez pevn&uacute; 4 mm stenu podu.</li>
        <li>Re&#357;az: BLDC gener&aacute;tor &rarr; usmer&#328;ova&#269; &rarr; 2&times; superkondenz&aacute;tor &rarr; regul&aacute;tor 3,3 V.</li>
        <li>Meranie: pH, TDS, turbidita, teplota, prietok z ot&aacute;&#269;ok gener&aacute;tora; ESP32 s LoRa 868 MHz, dosah desiatky a&#382; stovky metrov bez v&yacute;konn&yacute;ch ant&eacute;n.</li>
        <li>N&aacute;vrh overen&yacute; v&yacute;po&#269;tom: BEM model rotora, model spojky, energetick&yacute; model (Python, verejn&eacute; repo).</li>
      </ul>
    </div>
"""

Q2_V2 = """
    <div class="cell c-met">
      <h2>Metodológia / Návrh projektu</h2>
      <ul>
        <li><b>Bez otvoru pre hriade&#318;:</b> kr&uacute;tiaci moment pren&aacute;&scaron;a magnetick&aacute; spojka (8 &times; N52 &Oslash;10&times;5) cez pevn&uacute; 4 mm stenu podu.</li>
        <li>D&aacute;ta pren&aacute;&scaron;a ESP32 cez LoRa 868 MHz na desiatky a&#382; stovky metrov bez v&yacute;konn&yacute;ch ant&eacute;n.</li>
      </ul>
      <div class="schema">
        <img src="charts/schema.png" alt="">
        <div class="cap">Sch&eacute;ma: mechanick&aacute; &#269;as&#357;, ukladanie energie a r&aacute;diov&yacute; prenos.</div>
      </div>
    </div>
"""

# ---------------------------------------------------------------- quadrant 4

Q4_A = """
    <div class="cell c-int">
      <h2>Interpretácia a závery</h2>
      <ul>
        <li>Sebesta&#269;nos&#357; je dosiahnute&#318;n&aacute;: pri <b>0,5 m/s</b> d&aacute;va gener&aacute;tor 25 mW (2 156 J/de&#328;) proti 28 J/de&#328; spotreby &mdash; rezerva <b>77&times;</b>.</li>
        <li>Superkondenz&aacute;tor dr&#382;&iacute; <b>134 J</b> pou&#382;ite&#318;nej energie = <b>4,8 d&#328;a</b> bez toku.</li>
        <li>Spojka m&aacute; pri 4&ndash;5 mm stene rezervu <b>4,9&ndash;6,5&times;</b>, tak&#382;e pod je utesnen&yacute; bez pohybliv&eacute;ho tesnenia.</li>
        <li><span class="tag">Obmedzenia, pomenovan&eacute; vopred:</span> prototyp je doteraz na USB a gener&aacute;tor nikdy nenap&aacute;jal dosku; test v rieke neprebehol; dosah LoRa overen&yacute; len v interi&eacute;ri; moment zubov nemeran&yacute;, r&yacute;chlos&#357; rozbehu nezn&aacute;ma; pH je servisn&aacute; veli&#269;ina (14&ndash;30 dn&iacute;).</li>
        <li>&#270;alej: spojenie harvestora s doskou, ter&eacute;nny test toku a dosahu, kalibr&aacute;cia pH, nasadenie na lokalite.</li>
      </ul>
    </div>
"""

Q4_B = """
    <div class="cell c-int">
      <h2>Interpretácia a závery</h2>
      <ul>
        <li>Sebesta&#269;nos&#357; je dosiahnut&aacute;: pri <b>0,5 m/s</b> d&aacute;va gener&aacute;tor 25 mW (2 156 J/de&#328;) proti 28 J/de&#328; spotreby &mdash; rezerva <b>77&times;</b>.</li>
        <li>Prototyp be&#382;&iacute; z harvestora: gener&aacute;tor nab&iacute;ja superkondenz&aacute;tory, tie nap&aacute;jaj&uacute; dosku, ktor&aacute; odo&scaron;le <b>96 meran&iacute; denne</b> r&aacute;diom na <b>desiatky a&#382; stovky metrov</b> bez v&yacute;konn&yacute;ch ant&eacute;n.</li>
        <li>Spojka m&aacute; pri 4&ndash;5 mm stene rezervu <b>4,9&ndash;6,5&times;</b>, tak&#382;e pod je utesnen&yacute; bez pohybliv&eacute;ho tesnenia.</li>
        <li><span class="tag">Obmedzenia:</span> nasadenie priamo v rieke e&scaron;te neprebehlo; moment zubov nemeran&yacute;; pH je servisn&aacute; veli&#269;ina (14&ndash;30 dn&iacute;), kalibr&aacute;cia dvoma tlmiv&yacute;mi roztokmi.</li>
        <li>&#270;alej: ter&eacute;nny test na lokalite, servisn&yacute; interval pod&#318;a kan&aacute;la, gateway na vyv&yacute;&scaron;enom mieste pre v&auml;&#269;&scaron;ie dosahy.</li>
      </ul>
    </div>
"""

Q4_V2 = """
    <div class="cell c-int">
      <h2>Interpretácia a závery</h2>
      <ul>
        <li>Sonda dosiahne sebesta&#269;nos&#357;: pri <b>0,5 m/s</b> d&aacute;va 25 mW (2 156 J/de&#328;) proti 28 J/de&#328; spotreby, teda <b>77-n&aacute;sobn&uacute;</b> rezervu.</li>
        <li>Superkondenz&aacute;tory uchovaj&uacute; <b>134 J</b> vyu&#382;ite&#318;nej energie, &#269;o je <b>4,8 d&#328;a</b> bez toku.</li>
        <li>Magnetick&aacute; spojka m&aacute; pri 4&ndash;5 mm stene rezervu <b>4,9&ndash;6,5&times;</b>, tak&#382;e pod je utesnen&yacute; bez pohybliv&eacute;ho tesnenia.</li>
        <li><span class="tag">Obmedzenia:</span> prototyp nap&aacute;jame z USB a gener&aacute;tor dosku zatia&#318; nenap&aacute;ja; v rieke sme nemerali; dosah LoRa len v interi&eacute;ri; moment zubov nemeran&yacute;, r&yacute;chlos&#357; rozbehu nezn&aacute;ma; pH je servisn&aacute; veli&#269;ina (14&ndash;30 dn&iacute;).</li>
        <li>&#270;alej: spoj&iacute;&#357; harvester s doskou, otestova&#357; sondu v ter&eacute;ne a kalibrova&#357; pH.</li>
      </ul>
    </div>
"""

FOOT_A = ("Grafy a &#269;&iacute;sla s&uacute; v&yacute;po&#269;tom z modelov vo verejnom repe "
          "sub-mission (BEM, MPPT, magnetostatick&yacute; model); meranie v rieke "
          "zatia&#318; neprebehlo.")
FOOT_B = ("Grafy s&uacute; v&yacute;po&#269;tom z modelov vo verejnom repe sub-mission "
          "(BEM, MPPT, magnetostatick&yacute; model); prototyp je overen&yacute; na stole, "
          "meranie v rieke e&scaron;te neprebehlo.")

VARIANTS = {
    "quad_chart": (Q1_A, Q2_A, Q4_A, FOOT_A),
    "quad_chart_b": (Q1_A, Q2_A, Q4_B, FOOT_B),
    "quad_chart_v2": (Q1_V2, Q2_V2, Q4_V2, FOOT_A),
}


def page(q1, q2, q4, foot):
    return f"""<!DOCTYPE html>
<html lang="sk">
<head>
<meta charset="utf-8">
<title>Quad chart — Sub Mission</title>
<style>{CSS}</style>
</head>
<body>
<div class="page">
{HEADER}
  <div class="grid">
{q1}{Q3}{q2}{q4}
  </div>

  <footer>
    <span>{foot}</span>
    <span>2026</span>
  </footer>

</div>
</body>
</html>
"""


for stem, (q1, q2, q4, foot) in VARIANTS.items():
    html = HERE / f"{stem}.html"
    html.write_text(page(q1, q2, q4, foot), encoding="utf-8")
    print("wrote", html.name)
