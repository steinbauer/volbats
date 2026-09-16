#!/usr/bin/env python3
"""Vyrobí volební plakát A5 ve třech variantách.

Plakát se vyvěšuje na pár míst ve městě, takže musí fungovat ze vzdálenosti
několika metrů. Varianty se liší tím, co je na nich to hlavní:

    temata   tři hesla z programu velkým písmem, fotka jako pruh dole
    lide     mřížka všech kandidátů — ve městě, kde se lidé znají
    fotka    společná fotka přes celou plochu a claim

    python3 tools/plakat.py               # všechny tři do plakaty/
    python3 tools/plakat.py temata        # jen jednu
    python3 tools/plakat.py temata <cesta>

Hesla plakátu žijí v src/data/plakat.json, ať se dají přeházet bez sahání
do sazby.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qr
from tiskoviny import (CERVENA, INKOUST, KOREN, OBRAZKY, ORANZOVA, PLOCHA, PRECHOD,
                       STYL_ZNACKY, ZLUTA, dataurl, do_pdf, fonty, ikona, logo,
                       nacti, nacti_web, znak, zmer)

ADRESA = 'https://volbats.cz/'
SIRKA_PORTRETU = 400   # na plakátu vychází portrét kolem 22 mm

STYL = f"""
@page {{ size: A5 portrait; margin: 0; }}

* {{ box-sizing: border-box; }}

body {{
  margin: 0;
  font-family: 'IBM Plex Sans', sans-serif;
  color: {INKOUST};
  background: #fff;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}}

.strana {{
  width: 148mm;
  height: 210mm;
  border: 6mm solid;
  border-image: {PRECHOD} 1;
  background: {PLOCHA};
  padding: 6mm 7mm 5mm;
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}}

h1, h2 {{
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800;
  letter-spacing: -0.025em;
  line-height: 1.02;
  margin: 0;
}}

p {{ margin: 0; }}

.nadtitulek {{
  display: flex;
  align-items: center;
  gap: 2.5mm;
  font-size: 7.5pt;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: #8f2614;
  font-weight: 600;
}}
.nadtitulek::before {{
  content: '';
  width: 7mm; height: 0.7mm;
  background: {PRECHOD};
}}

/* --- záhlaví --- */
.zahlavi {{
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 4mm;
}}
.zahlavi__vpravo {{ text-align: right; }}

/* --- tři témata --- */
.temata {{ margin-top: 4mm; }}
.tema {{
  display: flex;
  gap: 4mm;
  align-items: flex-start;
  padding: 3.6mm 0;
  border-top: 0.4mm solid {INKOUST};
}}
.tema:last-child {{ border-bottom: 0.4mm solid {INKOUST}; }}
.tema svg {{ flex: none; margin-top: 0.6mm; }}
.tema__nadpis {{
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 17pt; line-height: 1.02;
  letter-spacing: -0.025em;
  text-transform: uppercase;
}}
.tema__text {{ font-size: 8.4pt; line-height: 1.34; color: #40372f; margin-top: 1.6mm; }}

/* --- fotka --- */
.pruh {{
  margin: 0 -7mm;
  overflow: hidden;
}}
.pruh img {{ width: 100%; display: block; }}
.pruh--uzky {{ height: 42mm; }}
.pruh--uzky img {{ height: 100%; object-fit: cover; object-position: 50% 62%; }}

/* --- mřížka kandidátů --- */
.mrizka {{
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 2mm;
  margin-top: 3.5mm;
}}
.kandidat__foto {{ position: relative; }}
.kandidat__foto img {{
  width: 100%; display: block; aspect-ratio: 1/1.2;
  object-fit: cover; object-position: 50% 18%;
}}
.kandidat__cislo {{
  position: absolute; left: 0; bottom: 0;
  width: 5.6mm; height: 5.6mm;
  display: flex; align-items: center; justify-content: center;
  background: {PRECHOD};
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 7.5pt;
}}
.kandidat__jmeno {{ font-weight: 600; font-size: 5.6pt; line-height: 1.14; margin-top: 0.9mm; }}

/* --- pata --- */
.pata {{
  margin-top: auto;
  padding-top: 4mm;
  display: flex;
  align-items: center;
  gap: 4mm;
  border-top: 0.6mm solid {INKOUST};
}}
.pata__cislo {{ display: flex; align-items: center; gap: 2.5mm; }}
.pata__volte {{
  font-size: 7pt; letter-spacing: 0.18em; text-transform: uppercase;
  color: #6b5f55; font-weight: 600;
}}
.pata__ctyrka {{
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 30pt; line-height: 0.9; letter-spacing: -0.05em;
}}
.pata__termin {{ margin-left: auto; text-align: right; }}
.pata__termin strong {{
  display: block;
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 13pt; letter-spacing: -0.02em;
}}
.pata__qr {{ width: 17mm; flex: none; }}
.pata__qr svg {{ width: 100%; height: auto; display: block; }}
.pata__web {{ font-size: 7pt; color: #6b5f55; text-align: center; margin-top: 0.8mm; }}
"""


def zahlavi(web: dict, popisek: str, velikost=42) -> str:
    return f"""<div class="zahlavi">
  {logo(web, velikost)}
  <div class="zahlavi__vpravo">
    <div class="nadtitulek">{popisek}</div>
  </div>
</div>"""


def pata(web: dict, s_qr=True) -> str:
    kod = (f'<div><div class="pata__qr">{qr.svg(ADRESA, "Q", pozadi=None)}</div>'
           f'<div class="pata__web">volbats.cz</div></div>') if s_qr else ''
    return f"""<div class="pata">
  <div class="pata__cislo">
    {znak(17, id_prechodu='pataZnak', sikmo=True)}
    <div>
      <div class="pata__volte">volte číslo</div>
      <div class="pata__ctyrka">{web['cislo']}</div>
    </div>
  </div>
  <div class="pata__termin">
    <div class="pata__volte">Komunální volby</div>
    <strong>{web['termin']}</strong>
  </div>
  {kod}
</div>"""


def plakat_temata(web, kandidati, plakat) -> str:
    """Tři hesla velkým písmem, fotka jako pruh dole."""
    temata = ''
    for i, t in enumerate(plakat['temata']):
        temata += f"""<div class="tema">
  {ikona(t['ikona'], 13, f'pt{i}')}
  <div>
    <div class="tema__nadpis">{t['nadpis']}</div>
    <div class="tema__text">{t['text']}</div>
  </div>
</div>"""
    fotka = OBRAZKY / 'spolecna-2000.webp'
    return f"""<div class="strana">
  {zahlavi(web, plakat['nadpis'])}
  <div class="temata">{temata}</div>
  <div class="pruh pruh--uzky" style="margin-top:5mm">
    <img src="{dataurl(fotka, 'image/webp')}" alt="">
  </div>
  {pata(web)}
</div>"""


def plakat_lide(web, kandidati, plakat) -> str:
    """Mřížka všech kandidátů — ve městě, kde se lidé znají, je to argument."""
    dlazdice = ''
    for k in kandidati:
        foto = OBRAZKY / f"{k['foto']}-{SIRKA_PORTRETU}.webp"
        dlazdice += f"""<div>
  <div class="kandidat__foto">
    <img src="{dataurl(foto, 'image/webp')}" alt="">
    <div class="kandidat__cislo">{k['cislo']}</div>
  </div>
  <div class="kandidat__jmeno">{k['jmeno']}</div>
</div>"""
    return f"""<div class="strana">
  {zahlavi(web, 'Kandidátní listina', 34)}
  <h1 style="font-size:17pt;margin-top:3mm">{len(kandidati)} lidí, které ve městě znáte.</h1>
  <div class="mrizka">{dlazdice}</div>
  {pata(web)}
</div>"""


def plakat_fotka(web, kandidati, plakat) -> str:
    """Společná fotka přes celou plochu a claim."""
    fotka = OBRAZKY / 'spolecna-2000.webp'
    return f"""<div class="strana">
  {zahlavi(web, 'Komunální volby')}
  <h1 style="font-size:27pt;margin-top:5mm">Záleží nám<br>na našem městě.</h1>
  <div class="pruh" style="margin-top:5mm">
    <img src="{dataurl(fotka, 'image/webp')}" alt="">
  </div>
  <p style="font-size:9.5pt;line-height:1.4;margin-top:5mm;color:#40372f">
    {len(kandidati)} kandidátů z Trhových Svinů i místních částí. Co chceme
    ve městě prosadit, najdete na volbats.cz.
  </p>
  {pata(web)}
</div>"""


VARIANTY = {'temata': plakat_temata, 'lide': plakat_lide, 'fotka': plakat_fotka}


def sestav(varianta: str, web, kandidati, plakat) -> str:
    return f"""<!doctype html>
<html lang="cs"><head><meta charset="utf-8">
<title>Volba pro město Trhové Sviny — plakát</title>
<style>{fonty()}{STYL_ZNACKY}{STYL}</style></head><body>
{VARIANTY[varianta](web, kandidati, plakat)}
</body></html>"""


def main():
    web = nacti_web()
    kandidati = nacti('kandidati.json')
    plakat = nacti('plakat.json')

    if len(sys.argv) > 1 and sys.argv[1] not in VARIANTY:
        sys.exit(__doc__)
    vybrane = [sys.argv[1]] if len(sys.argv) > 1 else list(VARIANTY)

    for varianta in vybrane:
        cil = (Path(sys.argv[2]) if len(sys.argv) > 2
               else KOREN / f'plakaty/plakat-{varianta}.pdf')
        html = sestav(varianta, web, kandidati, plakat)
        print(f'{cil.stem}:')
        zmer(html)
        do_pdf(html, cil, format='A5')


if __name__ == '__main__':
    main()
