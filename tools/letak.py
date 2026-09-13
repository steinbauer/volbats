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
import base64, json, re, shutil, subprocess, sys
from pathlib import Path

KOREN = Path(__file__).resolve().parent.parent
DATA = KOREN / 'src/data'
OBRAZKY = KOREN / 'src/obrazky'
FONTY = KOREN / 'src/fonts'
BROWSERLESS = 'http://localhost:3000/pdf'

# Fotky kandidátů na letáku vycházejí kolem 35 mm, u tisku 300 dpi to je
# zhruba 415 px — osmistovka má rezervu a zároveň nenafoukne PDF.
SIRKA_PORTRETU = 800


def dataurl(cesta: Path, typ: str) -> str:
    return f'data:{typ};base64,' + base64.b64encode(cesta.read_bytes()).decode()


def font_face(jmeno: str, vaha: int, soubory: list[str]) -> str:
    return '\n'.join(
        f"""@font-face {{
  font-family: '{jmeno}';
  font-weight: {vaha};
  font-style: normal;
  src: url('{dataurl(FONTY / s, "font/woff2")}') format('woff2');
}}""" for s in soubory if (FONTY / s).is_file())


def nacti_web() -> dict:
    """Vytáhne hodnoty z src/data/web.js, ať je leták bere odtamtud co web."""
    text = (DATA / 'web.js').read_text(encoding='utf-8')
    out = {}
    for klic, hodnota in re.findall(r"(\w+):\s*'([^']*)'", text):
        out[klic] = hodnota
    for klic, hodnota in re.findall(r'(\w+):\s*(\d+),', text):
        out[klic] = int(hodnota)
    return out


SRDCE = re.search(
    r"const CESTA =\s*'([^']+)'",
    (KOREN / 'src/components/Znak.jsx').read_text(encoding='utf-8')).group(1)


def znak(velikost_mm: float, cislo=None, id_prechodu='p') -> str:
    cifra = (f'<text x="105.5" y="108" text-anchor="middle" '
             f'class="znak-cislo">{cislo}</text>') if cislo is not None else ''
    return f"""<svg viewBox="0 0 202 199" style="width:{velikost_mm}mm;height:{velikost_mm * 199 / 202}mm">
  <defs><linearGradient id="{id_prechodu}" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#eed239"/><stop offset="1" stop-color="#dd4c2f"/>
  </linearGradient></defs>
  <path d="{SRDCE}" fill="url(#{id_prechodu})"/>{cifra}
</svg>"""


def bez_znacek(html: str) -> str:
    text = ' '.join(re.sub(r'<[^>]+>', ' ', html).split())
    # Po značkách zůstává mezera i tam, kde následuje interpunkce
    return re.sub(r'\s+([.,;:!?])', r'\1', text)


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
  padding: 11mm 12mm;
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

.znak-cislo {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800;
  font-size: 86px;
  fill: #191413;
}

/* pruh v barvách sdružení nahoře a dole */
.strana::before, .strana::after {
  content: '';
  position: absolute;
  left: 0; right: 0;
  height: 6mm;
  background: linear-gradient(0.25turn, #eed239, #dd4c2f);
}
.strana::before { top: 0; }
.strana::after { bottom: 0; }

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
.obalka__foto { margin: 7mm 0; }
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
.kandidat__jmeno { font-weight: 600; font-size: 8.8pt; line-height: 1.18; margin-bottom: 0.8mm; }
.kandidat__role { font-size: 6.8pt; line-height: 1.25; color: #554d46; }

/* --- program --- */
.program { columns: 2; column-gap: 9mm; margin-top: 6mm; }
.program__bod {
  break-inside: avoid;
  display: grid;
  grid-template-columns: 8mm 1fr;
  gap: 3mm;
  padding: 3mm 0;
  border-bottom: 0.25mm solid #e4e2df;
}
.program__cislo {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 600; font-size: 9pt; color: #c23a22; padding-top: 0.6mm;
}
.program__bod p { font-size: 10pt; line-height: 1.45; margin: 0; }
.program__popisek {
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 11pt; color: #c23a22; margin-bottom: 1mm;
}

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
    # Části obce bez skloňování — na obálce to funguje jako popiska
    mista = ' · '.join(sorted({k['cast'] for k in kandidati}))
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
    <div class="udaj-voleb__web">
      volbats.cz<br>{web['email']}
    </div>
  </div>
</div>"""


def strana_kandidatu(web, kandidati, poradi, celkem, id_prechodu) -> str:
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
  {hlavicka(web, id_prechodu)}
  <div class="nadtitulek" style="margin-top:4mm">Kandidátní listina</div>
  <h2 style="font-size:21pt">Naši kandidáti</h2>
  <div class="mrizka">{dlazdice}</div>
  <div class="paticka-strany">
    <span>Volba pro město Trhové Sviny</span>
    <span>{poradi} / {celkem}</span>
  </div>
</div>"""


def strana_programu(web, body, uvod) -> str:
    polozky = ''
    for i, bod in enumerate(body, 1):
        popisek = ('' if bod['nadpis'] == 'Chceme'
                   else f'<div class="program__popisek">{bod["nadpis"]}</div>')
        polozky += f"""<div class="program__bod">
  <div class="program__cislo">{i:02d}</div>
  <div>{popisek}{bod['html']}</div>
</div>"""
    return f"""<div class="strana">
  {hlavicka(web, 'program')}
  <div class="nadtitulek" style="margin-top:7mm">Co chceme prosadit</div>
  <h2 style="font-size:26pt">Náš program</h2>
  <p style="font-size:10pt;line-height:1.45;margin-top:4mm;max-width:150mm">{uvod}</p>
  <div class="program">{polozky}</div>
  <div class="paticka-strany">
    <span>Celý program na volbats.cz</span>
    <span>Volte číslo {web['cislo']}</span>
  </div>
</div>"""


def main():
    cil = Path(sys.argv[1]) if len(sys.argv) > 1 else KOREN / 'letak.pdf'
    web = nacti_web()
    kandidati = json.loads((DATA / 'kandidati.json').read_text(encoding='utf-8'))
    program = json.loads((DATA / 'program-body.json').read_text(encoding='utf-8'))
    stranky = json.loads((DATA / 'stranky.json').read_text(encoding='utf-8'))

    uvod = bez_znacek(stranky['home']['html'].split('</p>')[0])
    uvod_programu = bez_znacek(stranky['program']['html'].split('</p>')[0])

    # 23 lidí na dvě strany po dvanácti a jedenácti
    prvni, druha = kandidati[:12], kandidati[12:]

    fonty = '\n'.join([
        font_face('Bricolage Grotesque', 800,
                  ['bricolage-grotesque-800-latin.woff2',
                   'bricolage-grotesque-800-latin-ext.woff2']),
        font_face('Bricolage Grotesque', 600,
                  ['bricolage-grotesque-600-latin.woff2',
                   'bricolage-grotesque-600-latin-ext.woff2']),
        font_face('IBM Plex Sans', 400,
                  ['ibm-plex-sans-400-latin.woff2', 'ibm-plex-sans-400-latin-ext.woff2']),
        font_face('IBM Plex Sans', 600,
                  ['ibm-plex-sans-600-latin.woff2', 'ibm-plex-sans-600-latin-ext.woff2']),
    ])

    html = f"""<!doctype html>
<html lang="cs"><head><meta charset="utf-8">
<title>Volba pro město Trhové Sviny — leták</title>
<style>{fonty}{STYL}</style></head><body>
{strana_obalka(web, kandidati, uvod)}
{strana_kandidatu(web, prvni, 1, 2, 'kand1')}
{strana_kandidatu(web, druha, 2, 2, 'kand2')}
{strana_programu(web, program, uvod_programu)}
</body></html>"""

    zdroj = cil.with_suffix('.html')
    zdroj.write_text(html, encoding='utf-8')
    print(f'{zdroj.name}: {len(html) / 1024 / 1024:.1f} MB')

    # Kontrola, že se obsah na stránky vejde — přetečení by se v PDF projevilo
    # useknutým řádkem, což je na tiskovině vidět až pozdě.
    kod = ('module.exports=async({page})=>{await page.setContent(HTML,{waitUntil:"networkidle0"});'
           'const r=await page.evaluate(()=>[...document.querySelectorAll(".strana")]'
           '.map(s=>({v:Math.round(s.scrollHeight),limit:Math.round(s.clientHeight)})));'
           'return{data:r,type:"application/json"}}')
    mereni = subprocess.run(
        ['curl', '-sS', '-m', '180', '-X', 'POST', 'http://localhost:3000/function',
         '-H', 'Content-Type: application/json', '--data-binary', '@-'],
        input=json.dumps({'code': kod.replace('HTML', json.dumps(html)), 'context': {}}),
        text=True, capture_output=True)
    try:
        for i, s in enumerate(json.loads(mereni.stdout), 1):
            stav = 'PŘETÉKÁ' if s['v'] > s['limit'] + 1 else 'ok'
            print(f"  strana {i}: {s['v']} / {s['limit']} px  {stav}")
    except Exception:
        print('  měření se nepodařilo:', mereni.stdout[:200])

    odpoved = subprocess.run(
        ['curl', '-sS', '-m', '180', '-X', 'POST', BROWSERLESS,
         '-H', 'Content-Type: application/json', '--data-binary', '@-',
         '-o', str(cil), '-w', '%{http_code}'],
        input=json.dumps({'html': html,
                          'options': {'format': 'A4', 'printBackground': True,
                                      'preferCSSPageSize': True}}),
        text=True, capture_output=True)
    if odpoved.stdout.strip() != '200':
        sys.exit(f'browserless vrátil {odpoved.stdout}: {odpoved.stderr[:300]}')
    pred = cil.stat().st_size

    # Chrome vkládá obrázky v plném rozlišení, takže PDF vyjde přes 20 MB.
    # Ghostscript je převzorkuje na 300 dpi — pro tisk plně dostačující
    # a soubor se vejde do e-mailu.
    if shutil.which('gs'):
        docasny = cil.with_suffix('.gs.pdf')
        subprocess.run([
            'gs', '-q', '-dNOPAUSE', '-dBATCH', '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.5',
            '-dDownsampleColorImages=true', '-dColorImageResolution=300',
            '-dColorImageDownsampleType=/Bicubic',
            '-dAutoFilterColorImages=false', '-dColorImageFilter=/DCTEncode',
            '-dDownsampleGrayImages=true', '-dGrayImageResolution=300',
            '-dEmbedAllFonts=true', '-dSubsetFonts=true',
            f'-sOutputFile={docasny}', str(cil)], check=True)
        docasny.replace(cil)
        print(f'{cil.name}: {pred / 1024 / 1024:.1f} MB -> '
              f'{cil.stat().st_size / 1024:.0f} kB (obrázky na 300 dpi)')
    else:
        print(f'{cil.name}: {pred / 1024 / 1024:.1f} MB (bez ghostscriptu nekomprimováno)')


if __name__ == '__main__':
    main()
