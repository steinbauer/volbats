#!/usr/bin/env python3
"""Společné kusy generátorů tiskovin — letáku, plakátů a kartiček s QR.

Sazba všech tiskovin je HTML vytištěné přes Chrome (browserless na
localhost:3000). Obsah i značka se berou z týchž zdrojů jako web, takže
tiskovina nemůže tvrdit něco jiného než volbats.cz a logo na ní nemůže být
jiné než v hlavičce webu.
"""
import base64
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

KOREN = Path(__file__).resolve().parent.parent
DATA = KOREN / 'src/data'
OBRAZKY = KOREN / 'src/obrazky'
FONTY = KOREN / 'src/fonts'
BROWSERLESS = 'http://localhost:3000'

ZLUTA = '#eed239'
ORANZOVA = '#dd4c2f'
CERVENA = '#c23a22'
INKOUST = '#191413'
PLOCHA = 'linear-gradient(0.25turn, #fdf7e4, #fdeee7)'
PRECHOD = f'linear-gradient(0.25turn, {ZLUTA}, {ORANZOVA})'


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


def fonty() -> str:
    """Všechna čtyři písma jako data URI, ať je dokument soběstačný."""
    return '\n'.join([
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


def nacti_web() -> dict:
    """Hodnoty z src/data/web.js, ať je tiskovina bere odtamtud co web."""
    text = (DATA / 'web.js').read_text(encoding='utf-8')
    out = {}
    for klic, hodnota in re.findall(r"(\w+):\s*'([^']*)'", text):
        out[klic] = hodnota
    for klic, hodnota in re.findall(r'(\w+):\s*(\d+),', text):
        out[klic] = int(hodnota)
    return out


def nacti(jmeno: str):
    return json.loads((DATA / jmeno).read_text(encoding='utf-8'))


# Křivky srdce i rozměry viewBoxu se berou ze stejné komponenty jako web.
_ZNAK = (KOREN / 'src/components/Znak.jsx').read_text(encoding='utf-8')
SRDCE = re.findall(r"^  '(M[^']+)',$", _ZNAK, re.M)
VIEWBOX = re.search(r"VIEWBOX = '([^']+)'", _ZNAK).group(1)
VB_SIRKA, VB_VYSKA = (float(x) for x in VIEWBOX.split()[2:])
assert SRDCE, 'v Znak.jsx se nenašly křivky srdce'

IKONY = nacti('ikony.json')

# Styl značky. Velikosti jsou v jednotkách viewBoxu 1000 × 867, takže se
# škálují spolu se srdcem — stejně jako na webu.
STYL_ZNACKY = f"""
.znak-cislo {{
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 430px; fill: {INKOUST};
}}
.logo-nazev, .logo-mesto {{
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 92px; letter-spacing: -0.02em;
}}
.logo-nazev {{ fill: {INKOUST}; }}
.logo-mesto {{ fill: #9a7411; }}
.logo-claim {{
  font-family: 'IBM Plex Sans', sans-serif;
  font-style: italic; font-size: 48px; fill: #6b5f55;
}}
"""


def _svg(velikost_mm: float, vnitrek: str) -> str:
    vyska = velikost_mm * VB_VYSKA / VB_SIRKA
    return (f'<svg viewBox="{VIEWBOX}" style="width:{velikost_mm}mm;height:{vyska}mm">'
            f'{vnitrek}</svg>')


def znak(velikost_mm: float, cislo=None, id_prechodu='p', sikmo=False) -> str:
    """Srdce s přechodem, volitelně s volebním číslem uvnitř."""
    cifra = (f'<text x="520" y="492" text-anchor="middle" '
             f'class="znak-cislo">{cislo}</text>') if cislo is not None else ''
    tahy = ''.join(f'<path d="{d}" fill="url(#{id_prechodu})"/>' for d in SRDCE)
    return _svg(velikost_mm, f'''<defs>
    <linearGradient id="{id_prechodu}" x1="0" y1="0" x2="1" y2="{1 if sikmo else 0}">
    <stop offset="0" stop-color="{ZLUTA}"/><stop offset="1" stop-color="{ORANZOVA}"/>
  </linearGradient></defs>{tahy}{cifra}''')


def logo(web: dict, velikost_mm: float) -> str:
    """Značka s nápisem uvnitř srdce, jak ji má leták z roku 2022."""
    tahy = ''.join(f'<path d="{d}" fill="{CERVENA}"/>' for d in SRDCE)
    return _svg(velikost_mm, f'''{tahy}
  <text class="logo-nazev" x="522" y="258" text-anchor="middle">{web['nazev']}</text>
  <text class="logo-mesto" x="522" y="362" text-anchor="middle">{web['mesto']}</text>
  <text class="logo-claim" x="522" y="440" text-anchor="middle">{web['claim'].lower()}</text>''')


def ikona(slug: str, velikost_mm: float, id_prechodu: str) -> str:
    """Kresba tématu programu, stejná jako na webu."""
    tahy = IKONY.get(slug)
    if not tahy:
        return ''
    cesty = ''.join(f'<path d="{d}" fill="url(#{id_prechodu})" fill-rule="evenodd"/>'
                    for d in tahy)
    return f'''<svg viewBox="0 0 100 100" style="width:{velikost_mm}mm;height:{velikost_mm}mm">
  <defs><linearGradient id="{id_prechodu}" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{ZLUTA}"/><stop offset="1" stop-color="{ORANZOVA}"/>
  </linearGradient></defs>{cesty}</svg>'''


def spolecna() -> Path:
    """Největší dostupná společná fotka.

    Na jméno se nespoléhá: podle toho, jak velkou předlohu fotograf dodal,
    nemusí ta největší varianta vůbec vzniknout (viz tools/fotky.py).
    """
    varianty = sorted(OBRAZKY.glob('spolecna-*.webp'),
                      key=lambda c: int(c.stem.rsplit('-', 1)[1]))
    if not varianty:
        raise SystemExit('v src/obrazky/ není žádná spolecna-*.webp')
    return varianty[-1]


def bez_znacek(html: str) -> str:
    text = ' '.join(re.sub(r'<[^>]+>', ' ', html).split())
    # Po značkách zůstává mezera i tam, kde následuje interpunkce
    return re.sub(r'\s+([.,;:!?])', r'\1', text)


def _curl(cesta: str, telo: dict, vystup: str | None = None) -> subprocess.CompletedProcess:
    prikaz = ['curl', '-sS', '-m', '240', '-X', 'POST', BROWSERLESS + cesta,
              '-H', 'Content-Type: application/json', '--data-binary', '@-']
    if vystup:
        prikaz += ['-o', vystup, '-w', '%{http_code}']
    return subprocess.run(prikaz, input=json.dumps(telo), text=True, capture_output=True)


def zmer(html: str, vyber: str = '.strana') -> None:
    """Ohlásí, jestli se obsah na strany vejde.

    Přetečení by se v PDF projevilo useknutým řádkem, což je na hotové
    tiskovině vidět až pozdě.
    """
    kod = ('module.exports=async({page})=>{await page.setContent(HTML,{waitUntil:"networkidle0"});'
           'const r=await page.evaluate(()=>[...document.querySelectorAll(VYBER)]'
           '.map(s=>({v:Math.round(s.scrollHeight),limit:Math.round(s.clientHeight)})));'
           'return{data:r,type:"application/json"}}')
    kod = kod.replace('HTML', json.dumps(html)).replace('VYBER', json.dumps(vyber))
    odpoved = _curl('/function', {'code': kod, 'context': {}})
    try:
        for i, s in enumerate(json.loads(odpoved.stdout), 1):
            stav = 'PŘETÉKÁ' if s['v'] > s['limit'] + 1 else 'ok'
            print(f"  strana {i}: {s['v']} / {s['limit']} px  {stav}")
    except Exception:
        print('  měření se nepodařilo:', odpoved.stdout[:200])


def do_pdf(html: str, cil: Path, format='A4') -> None:
    """Vytiskne HTML do PDF a zmenší v něm obrázky na tiskových 300 dpi."""
    cil.parent.mkdir(parents=True, exist_ok=True)
    zdroj = cil.with_suffix('.html')
    zdroj.write_text(html, encoding='utf-8')

    odpoved = _curl('/pdf', {'html': html,
                             'options': {'format': format, 'printBackground': True,
                                         'preferCSSPageSize': True}}, str(cil))
    if odpoved.stdout.strip() != '200':
        sys.exit(f'browserless vrátil {odpoved.stdout}: {odpoved.stderr[:300]}')
    pred = cil.stat().st_size

    # Chrome vkládá obrázky v plném rozlišení, takže PDF vyjde v desítkách
    # megabajtů. Ghostscript je převzorkuje na 300 dpi — pro tisk plně
    # dostačující a soubor se vejde do e-mailu.
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
