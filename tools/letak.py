#!/usr/bin/env python3
"""Vyrobí volební leták jako PDF.

Předloha je leták z roku 2022: A3 přeložená napůl, tedy čtyři strany A4 —
obálka, dvakrát kandidáti a program. Obsah se bere z týchž dat jako web,
takže leták nemůže tvrdit něco jiného než volbats.cz.

    python3 tools/letak.py            # vyrobí letak.pdf vedle skriptu
    python3 tools/letak.py <cesta>    # nebo jinam

Sazba je HTML vytištěné přes Chrome (browserless na localhost:3000).
Fonty i fotky jdou do dokumentu jako data URI, aby byl soubor soběstačný.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import qr
from tiskoviny import (KOREN, OBRAZKY, STYL_ZNACKY, bez_znacek, dataurl, do_pdf,
                       fonty, ikona, logo, nacti, nacti_web, znak, zmer)

# Fotky kandidátů na letáku vycházejí kolem 35 mm, u tisku 300 dpi to je
# zhruba 415 px — osmistovka má rezervu a zároveň nenafoukne PDF.
SIRKA_PORTRETU = 800


STYL = """
@page { size: A4 portrait; margin: 0; }

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: 'IBM Plex Sans', sans-serif;
  color: #191413;
  background: #fff;
  -webkit-print-color-adjust: exact;
  print-color-adjust: exact;
}

.strana {
  width: 210mm;
  height: 297mm;
  /* Rámeček v barvách sdružení kolem celé strany; box-sizing: border-box
     ho drží uvnitř formátu A4. Pozadí je světlý odstín téhož přechodu —
     dost na to, aby strana nepůsobila prázdně, a zároveň tak světlý,
     že text zůstane čitelný a tisk nespolyká zbytečně barvu. */
  border: 8mm solid;
  border-image: linear-gradient(0.25turn, #eed239, #dd4c2f) 1;
  background: linear-gradient(0.25turn, #fdf7e4, #fdeee7);
  padding: 7mm 8mm;
  position: relative;
  overflow: hidden;
  page-break-after: always;
  display: flex;
  flex-direction: column;
}

.strana:last-child { page-break-after: auto; }

h1, h2, h3 {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800;
  letter-spacing: -0.025em;
  line-height: 1.03;
  margin: 0;
}

p { margin: 0 0 2.6mm; }

.nadtitulek {
  display: flex;
  align-items: center;
  gap: 3mm;
  font-size: 8pt;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #8f2614;
  font-weight: 600;
  margin-bottom: 4mm;
}
.nadtitulek::before {
  content: '';
  width: 9mm; height: 0.8mm;
  background: linear-gradient(0.25turn, #eed239, #dd4c2f);
}

/* --- hlavička s logem --- */
.logo { display: flex; align-items: center; gap: 3.5mm; }
.logo__nazev {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 15pt; letter-spacing: -0.02em; line-height: 1.1;
}
.logo__mesto { font-size: 11pt; color: #6b5f55; letter-spacing: 0.04em; }
.logo__claim { font-size: 9pt; font-style: italic; color: #6b5f55; margin-top: 1mm; }

/* --- obálka --- */
/* Obálka rozkládá volné místo mezi bloky, ne pod ně — jinak jí dole
   zůstane prázdný pás. */
.strana--obalka { justify-content: space-between; }
.strana--obalka .udaj-voleb { margin-top: 0; }

.obalka__nadpis { font-size: 40pt; margin: 0; }
.obalka__perex { font-size: 12pt; line-height: 1.5; color: #2c2521; }
/* Fotka jde až k rámečku — odsazení strany se ruší zápornými okraji,
   tím dostane víc místa a strana působí méně prázdně. */
.obalka__foto { margin: 0 -8mm; }
.obalka__foto img { width: 100%; display: block; }

.obalka__dole {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 10mm;
  align-items: center;
}
.obalka__pocet {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 28pt; line-height: 1;
}
.obalka__mista {
  font-size: 10pt; color: #6b5f55; margin-top: 2mm; letter-spacing: 0.04em;
}
.obalka__cislo { text-align: center; }
.obalka__volte {
  font-size: 8pt; letter-spacing: 0.2em; text-transform: uppercase;
  color: #6b5f55; font-weight: 600; margin-top: 1mm;
}

.udaj-voleb {
  border-top: 0.6mm solid #191413;
  padding-top: 4mm;
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 6mm;
  margin-top: auto;
}
.udaj-voleb__termin {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 20pt; line-height: 1.05;
}
.udaj-voleb__web { font-size: 11pt; color: #6b5f55; text-align: right; }

/* --- kandidáti --- */
.mrizka {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 4mm;
  margin-top: 4mm;
}
.kandidat__foto { position: relative; margin-bottom: 2mm; }
.kandidat__foto img {
  /* Kratší výřez než na webu, aby se dvanáct lidí vešlo na stranu.
     object-position drží hlavy — ořezává se zespodu. */
  width: 100%; display: block; aspect-ratio: 1/1.18;
  object-fit: cover; object-position: 50% 18%;
}
.kandidat__cislo {
  position: absolute; left: 0; bottom: 0;
  width: 10mm; height: 10mm;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(0.25turn, #eed239, #dd4c2f);
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 13pt;
}
.vyzva {
  border: 0.5mm solid #dd4c2f;
  border-radius: 2mm;
  padding: 4mm 3mm;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2mm;
}
.vyzva__text {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 12pt; line-height: 1.1;
}
.vyzva__qr { width: 28mm; }
.vyzva__qr svg { width: 100%; height: auto; display: block; }
.vyzva__web { font-size: 8pt; color: #6b5f55; letter-spacing: 0.04em; }

.kandidat__jmeno { font-weight: 600; font-size: 8.8pt; line-height: 1.18; margin-bottom: 0.8mm; }
.kandidat__role { font-size: 6.8pt; line-height: 1.25; color: #554d46; }

/* --- program --- */
.program { columns: 2; column-gap: 6mm; margin-top: 3mm; }
.program__sekce {
  break-inside: avoid;
  padding-bottom: 1.4mm;
  margin-bottom: 1.4mm;
  border-bottom: 0.25mm solid #e6dccb;
}
.program__nadpis {
  display: flex;
  align-items: center;
  gap: 1.6mm;
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 8.8pt; color: #c23a22;
  margin-bottom: 0.8mm; line-height: 1.12;
}
.program__nadpis svg { flex: none; }
/* „Chceme" stojí jednou nad celým programem. Nad každou sekcí zvlášť to
   bylo čtrnáctkrát totéž slovo a strana se kvůli němu musela mačkat. */
.program__chceme {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 11pt; color: #8f2614;
  letter-spacing: -0.02em;
  margin: 3mm 0 0;
}
.program__body { margin: 0; padding-left: 3.4mm; }
.program__body li { font-size: 7.5pt; line-height: 1.28; margin-bottom: 0.5mm; }
.program__body li:last-child { margin-bottom: 0; }
.program__sekce--ne .program__nadpis { text-transform: uppercase; letter-spacing: 0.04em; }

.paticka-strany {
  margin-top: auto;
  padding-top: 4mm;
  font-size: 8.5pt;
  color: #6b5f55;
  display: flex;
  justify-content: space-between;
}
"""


def hlavicka(web: dict, id_prechodu: str) -> str:
    return f"""<div class="logo">
  {znak(16, web['cislo'], id_prechodu)}
  <div>
    <div class="logo__nazev">{web['nazev']}</div>
    <div class="logo__mesto">{web['mesto']}</div>
    <div class="logo__claim">{web['claim']}</div>
  </div>
</div>"""


def strana_obalka(web, kandidati, uvod) -> str:
    spolecna = OBRAZKY / 'spolecna-2600.webp'
    # Části obce bez skloňování — na obálce to funguje jako popiska.
    # Trhové Sviny patří na začátek, zbytek abecedně.
    casti = sorted({k['cast'] for k in kandidati})
    mista = ' · '.join(['Trhové Sviny'] + [c for c in casti if c != 'Trhové Sviny'])
    return f"""<div class="strana strana--obalka">
  {hlavicka(web, 'obalka')}
  <h1 class="obalka__nadpis">Záleží nám<br>na našem městě.</h1>
  <p class="obalka__perex">{uvod}</p>
  <div class="obalka__foto"><img src="{dataurl(spolecna, 'image/webp')}" alt=""></div>

  <div class="obalka__dole">
    <div>
      <div class="obalka__pocet">{len(kandidati)} kandidátů</div>
      <div class="obalka__mista">{mista}</div>
      <p class="obalka__perex" style="margin-top:5mm">Koho na kandidátce najdete
         a co chceme ve městě prosadit, se dočtete uvnitř.</p>
    </div>
    <div class="obalka__cislo">
      {znak(58, web['cislo'], 'obalkaVelke')}
      <div class="obalka__volte">volte číslo</div>
    </div>
  </div>

  <div class="udaj-voleb">
    <div>
      <div class="nadtitulek" style="margin-bottom:2mm">Komunální volby</div>
      <div class="udaj-voleb__termin">{web['termin']}</div>
    </div>
    <div class="udaj-voleb__web">volbats.cz</div>
  </div>
</div>"""


def dlazdice_vyzvy(web) -> str:
    """Vyplní volné okénko v mřížce — kandidátů je 23, mřížka má 24 polí."""
    kod = qr.svg('https://volbats.cz/', 'Q', pozadi=None)
    return f"""<div class="vyzva">
  {znak(20, web['cislo'], 'vyzva')}
  <div class="vyzva__text">Volte číslo {web['cislo']}</div>
  <div class="vyzva__qr">{kod}</div>
  <div class="vyzva__web">volbats.cz</div>
</div>"""


def strana_kandidatu(web, kandidati, id_prechodu, vyzva=False) -> str:
    """Strana s portréty. V záhlaví je kompaktní značka — přesně jak to má
    leták z roku 2022, kde plná sazba s číslem zůstala jen na obálce."""
    dlazdice = ''
    for k in kandidati:
        foto = OBRAZKY / f"{k['foto']}-{SIRKA_PORTRETU}.webp"
        dlazdice += f"""<div class="kandidat">
  <div class="kandidat__foto">
    <img src="{dataurl(foto, 'image/webp')}" alt="">
    <div class="kandidat__cislo">{k['cislo']}</div>
  </div>
  <div class="kandidat__jmeno">{k['jmeno']}</div>
  <div class="kandidat__role">{k['info']}</div>
</div>"""
    return f"""<div class="strana">
  {logo(web, 34)}
  <div class="nadtitulek" style="margin-top:4mm">Kandidátní listina</div>
  <h2 style="font-size:21pt">Naši kandidáti</h2>
  <div class="mrizka">{dlazdice}{dlazdice_vyzvy(web) if vyzva else ''}</div>
  <div class="paticka-strany"><span>Volba pro město Trhové Sviny</span></div>
</div>"""


def strana_programu(web, program) -> str:
    """Program v tematických sekcích, ve dvou sloupcích.

    Sekcí je patnáct a odrážek přes padesát, takže je sazba hustší než
    zbytek letáku. Jestli se to na stranu vejde, hlídá měření v main() —
    při přetečení se s písmem nebo s počtem odrážek musí hnout.
    """
    polozky = ''
    for i, sekce in enumerate(program['sekce']):
        odrazky = ''.join(f'<li>{b}</li>' for b in sekce['body'])
        ne = sekce.get('nechceme')
        polozky += f"""<div class="program__sekce{' program__sekce--ne' if ne else ''}">
  <div class="program__nadpis">{ikona(sekce['slug'], 4.4, f'ik{i}')}{sekce['nadpis']}</div>
  <ul class="program__body">{odrazky}</ul>
</div>"""
    return f"""<div class="strana">
  {logo(web, 34)}
  <div class="nadtitulek" style="margin-top:4mm">Co chceme prosadit</div>
  <h2 style="font-size:22pt">Náš program</h2>
  <p style="font-size:8.2pt;line-height:1.38;margin-top:2.5mm">{program['uvod']}</p>
  <p class="program__chceme">Chceme:</p>
  <div class="program">{polozky}</div>
  <div class="paticka-strany">
    <span>Celý program na volbats.cz</span>
    <span>Volte číslo {web['cislo']}</span>
  </div>
</div>"""


def main():
    cil = Path(sys.argv[1]) if len(sys.argv) > 1 else KOREN / 'letak.pdf'
    web = nacti_web()
    kandidati = nacti('kandidati.json')
    program = nacti('program.json')
    stranky = nacti('stranky.json')

    uvod = bez_znacek(stranky['home']['html'].split('</p>')[0])

    # 23 lidí na dvě strany po dvanácti a jedenácti
    prvni, druha = kandidati[:12], kandidati[12:]

    html = f"""<!doctype html>
<html lang="cs"><head><meta charset="utf-8">
<title>Volba pro město Trhové Sviny — leták</title>
<style>{fonty()}{STYL_ZNACKY}{STYL}</style></head><body>
{strana_obalka(web, kandidati, uvod)}
{strana_kandidatu(web, prvni, 'kand1')}
{strana_kandidatu(web, druha, 'kand2', vyzva=True)}
{strana_programu(web, program)}
</body></html>"""

    print(f'{cil.stem}.html: {len(html) / 1024 / 1024:.1f} MB')
    zmer(html)
    do_pdf(html, cil)


if __name__ == '__main__':
    main()
