#!/usr/bin/env python3
"""Vyrobí kartičky s QR kódy na web — a QR kódy samotné.

Kartičky jsou tři vedle sebe na jednom A4 na šířku, mezi nimi řezné linky:
vytiskne se jednou, rozstřihne a je hotovo. Vedle PDF vzniknou i holé kódy
v SVG a PNG, aby šly vlepit do pozvánky, do příspěvku na sítích nebo na
nástěnku.

    python3 tools/qr-karticky.py            # do qr/ v kořeni projektu
    python3 tools/qr-karticky.py <adresář>
"""
import base64
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qr
from tiskoviny import (BROWSERLESS, INKOUST, KOREN, PLOCHA, PRECHOD, STYL_ZNACKY,
                       do_pdf, fonty, logo, nacti_web, znak, zmer)

# Úroveň korekce Q snese ušpinění i částečné zakrytí kódu, což se na
# vytištěné kartičce hodí víc než o pár modulů menší obrázek.
UROVEN = 'Q'

KODY = [
    ('uvod', 'https://volbats.cz/', 'Úvodní stránka',
     'Kdo jsme, koho volit a kdy se volí.'),
    ('program', 'https://volbats.cz/program/', 'Náš program',
     'Co chceme ve městě prosadit, po tématech.'),
    ('lide', 'https://volbats.cz/kandidati/', 'Naši lidé',
     'Všech 23 kandidátů i s medailonky.'),
]

STYL = f"""
@page {{ size: A4 landscape; margin: 0; }}

* {{ box-sizing: border-box; }}

body {{
  margin: 0;
  font-family: 'IBM Plex Sans', sans-serif;
  color: {INKOUST};
  background: #fff;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}}

.list {{
  width: 297mm;
  height: 210mm;
  display: flex;
  padding: 10mm 9mm;
  gap: 0;
}}

/* Řezná linka je společný okraj dvou sousedních kartiček, ne čára navíc —
   po rozstřižení tak nezůstane na jedné kartičce proužek z druhé. */
.karticka {{
  flex: 1;
  border: 0.3mm dashed #b9ab96;
  border-right-width: 0;
  background: {PLOCHA};
  padding: 7mm 6mm 6mm;
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}}
.karticka:last-child {{ border-right-width: 0.3mm; }}

.karticka__pruh {{
  width: 100%;
  height: 2mm;
  background: {PRECHOD};
  margin-bottom: 6mm;
}}

.karticka__nadpis {{
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 16pt; letter-spacing: -0.02em;
  margin-top: 5mm;
}}
.karticka__popis {{
  font-size: 8.5pt; line-height: 1.35; color: #5b5048; margin-top: 2mm;
}}

.karticka__qr {{ width: 56mm; margin-top: auto; }}
.karticka__qr svg {{ width: 100%; height: auto; display: block; }}
.karticka__adresa {{
  font-size: 9pt; color: #5b5048; margin-top: 3mm; letter-spacing: 0.02em;
}}

.karticka__pata {{
  margin-top: auto;
  padding-top: 5mm;
  width: 100%;
  border-top: 0.5mm solid {INKOUST};
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 3mm;
}}
.karticka__volte {{
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 12pt; letter-spacing: -0.02em;
}}
.karticka__termin {{ font-size: 8pt; color: #5b5048; margin-top: 1.5mm; }}
"""


def karticka(web, poradi, adresa, nadpis, popis) -> str:
    return f"""<div class="karticka">
  <div class="karticka__pruh"></div>
  {logo(web, 52)}
  <div class="karticka__nadpis">{nadpis}</div>
  <div class="karticka__popis">{popis}</div>
  <div class="karticka__qr">{qr.svg(adresa, UROVEN, pozadi=None)}</div>
  <div class="karticka__adresa">{adresa.replace('https://', '')}</div>
  <div class="karticka__pata">
    {znak(13, id_prechodu=f'qrz{poradi}', sikmo=True)}
    <div>
      <div class="karticka__volte">Volte číslo {web['cislo']}</div>
      <div class="karticka__termin">{web['termin']}</div>
    </div>
  </div>
</div>"""


def do_png(svg: str, cil: Path, velikost=1000) -> None:
    """Vykreslí SVG přes browserless, ať má Věrka i rastr do Wordu a na sítě."""
    html = (f'<!doctype html><body style="margin:0;background:#fff">'
            f'{svg.replace("<svg ", f"<svg width={velikost} height={velikost} ")}</body>')
    kod = ('module.exports=async({page})=>{await page.setViewport({width:VEL,height:VEL});'
           'await page.setContent(HTML,{waitUntil:"networkidle0"});'
           'const b=await page.screenshot({type:"png",clip:{x:0,y:0,width:VEL,height:VEL}});'
           'return{data:b,type:"image/png"}}')
    kod = kod.replace('HTML', json.dumps(html)).replace('VEL', str(velikost))
    odpoved = subprocess.run(
        ['curl', '-sS', '-m', '120', '-X', 'POST', BROWSERLESS + '/function',
         '-H', 'Content-Type: application/json', '--data-binary', '@-',
         '-o', str(cil), '-w', '%{http_code}'],
        input=json.dumps({'code': kod, 'context': {}}), text=True, capture_output=True)
    if odpoved.stdout.strip() != '200':
        print(f'  {cil.name}: browserless vrátil {odpoved.stdout}')


def main():
    cilovy = Path(sys.argv[1]) if len(sys.argv) > 1 else KOREN / 'qr'
    cilovy.mkdir(parents=True, exist_ok=True)
    web = nacti_web()

    karticky = ''.join(karticka(web, i, adresa, nadpis, popis)
                       for i, (_, adresa, nadpis, popis) in enumerate(KODY))
    html = f"""<!doctype html>
<html lang="cs"><head><meta charset="utf-8">
<title>Volba pro město Trhové Sviny — QR kódy</title>
<style>{fonty()}{STYL_ZNACKY}{STYL}</style></head><body>
<div class="list">{karticky}</div>
</body></html>"""

    zmer(html, '.karticka')
    do_pdf(html, cilovy / 'qr-karticky.pdf', format='A4')

    for jmeno, adresa, _, _ in KODY:
        svg = qr.svg(adresa, UROVEN)
        (cilovy / f'qr-{jmeno}.svg').write_text(svg, encoding='utf-8')
        do_png(svg, cilovy / f'qr-{jmeno}.png')
        print(f'  qr-{jmeno}.svg + .png -> {adresa}')


if __name__ == '__main__':
    main()
