#!/usr/bin/env python3
"""Výzvy na sociální sítě: „Hoď tam 4!“ a poděkování po volbách.

    python3 tools/vyzvy.py                 # obě, obrázek i video
    python3 tools/vyzvy.py hod-tam-4       # jen jedna
    python3 tools/vyzvy.py --bez-videa     # jen obrázky

Každá výzva je jedna HTML stránka s funkcí `nastav(t)`, která ji postaví do
stavu v čase t. Obrázek je poslední stav animace, video vznikne nafocením
stránky po třicetinách vteřiny — obojí tak vypadá stejně a písmo i srdce jsou
tytéž jako na kartách a letáku. Texty jsou v src/data/socialni.json, klíč
„vyzvy“.
"""
import argparse
import base64
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from socialni import PLOCHA, PRECHOD, TLUMENY, znak
from tiskoviny import (BROWSERLESS, CERVENA, INKOUST, KOREN, ORANZOVA, ZLUTA,
                       dataurl, fonty, nacti, nacti_web)

SIRKA, VYSKA = 1080, 1350          # 4:5 jako karty
FPS = 30
OBRAZKY_VEN = KOREN / 'socialni/vyzvy'
VIDEA_VEN = KOREN / 'video'
PRACOVNI = KOREN / 'video/dily/vyzvy'

# Animace v obou výzvách stojí na stejných pomůckách: lineární úsek 0–1
# mezi dvěma časy a měkký náběh i dojezd, ať nic necuká.
JS_POMUCKY = """
const usek = (t, a, b) => Math.min(1, Math.max(0, (t - a) / (b - a)));
const hladce = x => x * x * (3 - 2 * x);
const pruzne = x => x === 0 ? 0 : x === 1 ? 1 :
  Math.pow(2, -9 * x) * Math.sin((x * 10 - 0.75) * (2 * Math.PI) / 3) + 1;
const $ = s => document.querySelector(s);
"""


def stranka(telo: str, styl: str, skript: str) -> str:
    return f"""<!doctype html><html lang="cs"><head><meta charset="utf-8"><style>
{fonty()}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
body {{
  width: {SIRKA}px; height: {VYSKA}px; overflow: hidden; position: relative;
  background: {PLOCHA};
  font-family: 'IBM Plex Sans', sans-serif; color: {INKOUST};
  -webkit-font-smoothing: antialiased;
}}
.hlavicka {{ position: absolute; left: 44px; right: 44px; top: 40px;
  display: flex; align-items: center; gap: 20px; }}
.hlavicka__nazev {{ font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800;
  font-size: 38px; line-height: 1.05; letter-spacing: -0.02em; }}
.hlavicka__mesto {{ color: #9a7411; }}
.hlavicka__web {{ margin-left: auto; font-size: 30px; font-weight: 600; color: {CERVENA}; }}
.znak-cislo {{ font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800;
  font-size: 430px; fill: {INKOUST}; }}
.bricolage {{ font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800;
  letter-spacing: -0.025em; line-height: 1.02; }}
{styl}
</style></head><body>{telo}
<script>{JS_POMUCKY}{skript}</script></body></html>"""


def hlavicka(web: dict) -> str:
    return f"""<div class="hlavicka">{znak(96, web['cislo'], 'hl')}
  <div class="hlavicka__nazev">{web['nazev']}<br><span class="hlavicka__mesto">{web['mesto']}</span></div>
  <div class="hlavicka__web">volbats.cz</div></div>"""


# --- Hoď tam 4 ---------------------------------------------------------------
# Řadicí schéma jako na hlavici páky: nahoře 1 3 5, dole 2 4 R. Cesta z
# jedničky na čtyřku je tatáž, kterou ruka opravdu jede — dolů do neutrálu,
# doprava a dolů. Ve videu po ní jede hlavice páky, na obrázku šipka: hlavici
# lídryně na statickém obrázku nepoznala, ve videu ano. Tachometr vedle ukazuje, co to udělá.

SCHEMA_X = (90, 270, 450)
SCHEMA_Y = (95, 255, 415)   # horní řada, neutrál, dolní řada
HROT_NAD = 26               # hrot šipky končí nad tečkou čtyřky, ne na ní


def hod_tam_4(web: dict, texty: dict, kandidati: list) -> str:
    x1, x2, x3 = SCHEMA_X
    yh, yn, yd = SCHEMA_Y
    cara = f'stroke="{INKOUST}" stroke-width="16" stroke-linecap="round" fill="none"'
    teckly = ''.join(f'<circle cx="{x}" cy="{y}" r="17" fill="{INKOUST}"/>'
                     for x in SCHEMA_X for y in (yh, yd))
    cisla = ''.join(
        f'<text x="{x}" y="{y}" text-anchor="middle" class="bricolage cislo-rychlosti'
        f'{" cislo-ctyri" if c == "4" else ""}">{c}</text>'
        for x, y, c in [(x1, 48, '1'), (x2, 48, '3'), (x3, 48, '5'),
                        (x1, 534, '2'), (x2, 534, '4'), (x3, 534, 'R')])
    cesta = f'M{x1},{yh} L{x1},{yn} L{x2},{yn} L{x2},{yd - HROT_NAD}'
    schema = f"""<svg class="schema" viewBox="0 0 540 550" width="480" height="489">
  <defs><linearGradient id="pruh" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{ZLUTA}"/><stop offset="1" stop-color="{ORANZOVA}"/></linearGradient>
  <radialGradient id="hlavice-barva" cx="0.38" cy="0.32" r="0.75">
    <stop offset="0" stop-color="#ffd76a"/><stop offset="0.55" stop-color="{ORANZOVA}"/>
    <stop offset="1" stop-color="{CERVENA}"/></radialGradient></defs>
  <path d="M{x1},{yh} V{yd} M{x2},{yh} V{yd} M{x3},{yh} V{yd} M{x1},{yn} H{x3}" {cara}/>
  {teckly}{cisla}
  <path id="jizda" d="{cesta}" stroke="url(#pruh)" stroke-width="34" stroke-linecap="round"
        stroke-linejoin="round" fill="none" pathLength="1000"
        stroke-dasharray="1000" stroke-dashoffset="1000"/>
  <polygon id="sipka" points="0,0 -66,-48 -66,48" fill="{ORANZOVA}" stroke="{ORANZOVA}"
           stroke-width="8" stroke-linejoin="round"/>
  <g id="hlavice" transform="translate({x1},{yh})">
    <circle r="46" fill="url(#hlavice-barva)" stroke="#fff" stroke-width="8"/>
    <path d="M-17,-18 V18 M0,-18 V18 M17,-18 V18 M-17,0 H17" stroke="#fff" stroke-width="5"
          stroke-linecap="round" fill="none" opacity="0.9"/>
  </g>
</svg>"""

    # Tachometr: oblouk od −120° do +120°, ručička v něm doletí až nahoru.
    def bod(uhel, r):
        import math
        a = math.radians(uhel - 90)
        return 180 + r * math.cos(a), 180 + r * math.sin(a)
    za, zb = bod(-120, 140), bod(120, 140)
    rysky = ''
    for i in range(9):
        u = -120 + i * 30
        (ax, ay), (bx, by) = bod(u, 112), bod(u, 128)
        rysky += f'<line x1="{ax:.1f}" y1="{ay:.1f}" x2="{bx:.1f}" y2="{by:.1f}" stroke="{INKOUST}" stroke-width="5" stroke-linecap="round"/>'
    tachometr = f"""<svg class="tachometr" viewBox="0 0 360 330" width="360" height="330">
  <defs><linearGradient id="oblouk" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="{ZLUTA}"/><stop offset="1" stop-color="{ORANZOVA}"/></linearGradient></defs>
  <path d="M{za[0]:.1f},{za[1]:.1f} A140,140 0 1 1 {zb[0]:.1f},{zb[1]:.1f}" stroke="#f3e2cf"
        stroke-width="26" fill="none" stroke-linecap="round"/>
  <path id="oblouk-plny" d="M{za[0]:.1f},{za[1]:.1f} A140,140 0 1 1 {zb[0]:.1f},{zb[1]:.1f}"
        stroke="url(#oblouk)" stroke-width="26" fill="none" stroke-linecap="round"
        pathLength="1000" stroke-dasharray="1000" stroke-dashoffset="1000"/>
  {rysky}
  <g id="rucicka" transform="rotate(-120 180 180)">
    <path d="M174,190 L180,62 L186,190 Z" fill="{CERVENA}"/>
  </g>
  <circle cx="180" cy="180" r="20" fill="{INKOUST}"/>
  <text x="180" y="300" text-anchor="middle" class="bricolage tacho-popis">km/h</text>
</svg>"""

    cary = ''.join(f'<div class="rychlost" style="top:{y}px;width:{w}px;--zpozdeni:{d}"></div>'
                   for y, w, d in [(0, 230, 0), (34, 300, 0.12), (68, 190, 0.06),
                                   (102, 260, 0.18)])

    radky = ''
    for k in kandidati[:3]:
        povolani = k['povolani'][0].lower() + k['povolani'][1:]
        radky += f"""<div class="radek">
      <div class="ctverecek"></div>
      <div><span class="poradi">{k['cislo']}.</span> <b>{k['jmeno']},</b> {k['vek']} let, {povolani}</div></div>"""

    telo = f"""{hlavicka(web)}
<h1 class="bricolage titulek">{texty['titulek']}</h1>
<div class="radek-schema">{schema}
  <div class="vpravo">
    <div class="cary">{cary}</div>
    {tachometr}
  </div>
</div>
<div class="listek">
  <div class="strana">
    <svg class="krizek" viewBox="0 0 110 110" width="110" height="110">
      <rect x="5" y="5" width="100" height="100" fill="#fff" stroke="{INKOUST}" stroke-width="6"/>
      <path id="tah1" d="M24,24 L86,86" stroke="{INKOUST}" stroke-width="13" stroke-linecap="round"
            pathLength="100" stroke-dasharray="100" stroke-dashoffset="100"/>
      <path id="tah2" d="M86,24 L24,86" stroke="{INKOUST}" stroke-width="13" stroke-linecap="round"
            pathLength="100" stroke-dasharray="100" stroke-dashoffset="100"/>
    </svg>
    <div><div class="strana__nazev">{web['nazev']}</div>
      <div class="strana__cislo">vylosované číslo: {web['cislo']}</div></div>
  </div>
  <div class="kandidati">{radky}<div class="radek radek--dal">…</div></div>
</div>
<p class="popisek" id="popisek">{texty['popisek']}</p>
<p class="termin">volby {web['termin']}</p>"""

    styl = f"""
.titulek {{ position: absolute; left: 44px; right: 44px; top: 168px; margin: 0;
  font-size: 118px; text-align: center; }}
.titulek em {{ font-style: normal; color: {CERVENA}; }}
.radek-schema {{ position: absolute; left: 30px; right: 30px; top: 318px;
  display: flex; align-items: center; justify-content: space-between; }}
/* Ostatní rychlosti jen naznačené, ať oko jde rovnou na čtyřku. */
.cislo-rychlosti {{ font-size: 58px; fill: {INKOUST}; opacity: 0.3; }}
.cislo-ctyri {{ fill: {CERVENA}; font-size: 74px; opacity: 1; }}
.vpravo {{ position: relative; width: 400px; height: 489px; }}
.tachometr {{ position: absolute; left: 20px; bottom: 0; }}
.tacho-popis {{ font-size: 34px; fill: {TLUMENY}; font-weight: 600; }}
.cary {{ position: absolute; left: 0; top: 112px; width: 400px; height: 140px; }}
.rychlost {{ position: absolute; right: 30px; height: 12px; border-radius: 12px;
  background: {PRECHOD}; opacity: 0; transform-origin: right center; }}
.listek {{ position: absolute; left: 70px; right: 70px; top: 826px;
  background: #fff; border-radius: 22px; padding: 30px 38px 22px;
  box-shadow: 0 10px 34px rgba(150, 90, 40, 0.13); transform: rotate(-1.2deg); }}
.strana {{ display: flex; align-items: center; gap: 28px; }}
.strana__nazev {{ font-size: 46px; font-weight: 600; line-height: 1.1; }}
.strana__cislo {{ font-size: 32px; font-weight: 600; margin-top: 6px; }}
.kandidati {{ margin-top: 20px; padding-left: 26px; color: #6f645b; font-size: 23px; }}
.radek {{ display: flex; align-items: center; gap: 22px; margin-top: 10px; }}
.radek b {{ font-weight: 600; color: #4a413a; }}
.radek--dal {{ padding-left: 82px; margin-top: 2px; }}
.ctverecek {{ flex: none; width: 58px; height: 42px; border: 4px solid #8a7f76; }}
.popisek {{ position: absolute; left: 60px; right: 60px; top: 1204px; margin: 0;
  text-align: center; font-family: 'Bricolage Grotesque', sans-serif; font-weight: 800;
  font-size: 44px; letter-spacing: -0.02em; color: {CERVENA}; }}
/* Obrázek je jednodušší než video: na statické ploše by tachometr a řádky
   kandidátů jen přidávaly, co číst. Zůstane řazení na čtyřku
   a křížek u strany. */
.staticky .vpravo, .staticky .kandidati {{ display: none; }}
.staticky .radek-schema {{ justify-content: center; top: 300px; }}
.staticky .schema {{ width: 580px; height: 591px; }}
.staticky .listek {{ top: 924px; left: 150px; right: 150px; padding-bottom: 30px; }}
.staticky .popisek {{ top: 1130px; font-size: 50px; }}
.termin {{ position: absolute; left: 0; right: 0; bottom: 34px; margin: 0; text-align: center;
  font-size: 27px; font-weight: 600; letter-spacing: 0.08em; color: {TLUMENY}; }}
"""

    skript = f"""
const X = {list(SCHEMA_X)}, Y = {list(SCHEMA_Y)};
// cesta 1 → neutrál → doprava → 4; délky úseků v px schématu
const useky = [[X[0],Y[0],X[0],Y[1]],[X[0],Y[1],X[1],Y[1]],[X[1],Y[1],X[1],Y[2]-{HROT_NAD}]];
const DELKA_SIPKY = 66;
const delky = useky.map(u => Math.hypot(u[2]-u[0], u[3]-u[1]));
const celkem = delky.reduce((a, b) => a + b);
function poloha(s) {{
  let zbyva = Math.max(0, Math.min(celkem, s));
  for (let i = 0; i < useky.length; i++) {{
    if (zbyva <= delky[i] || i === useky.length - 1) {{
      const f = Math.min(1, zbyva / delky[i]), u = useky[i];
      return [u[0] + (u[2]-u[0]) * f, u[1] + (u[3]-u[1]) * f];
    }}
    zbyva -= delky[i];
  }}
}}
function nastav(t, staticky) {{
  document.body.classList.toggle('staticky', !!staticky);
  // řazení: krátký nádech na jedničce, pak jednou plynulou jízdou na čtyřku
  const p = hladce(usek(t, 0.7, 2.0));
  // hrot jede po cestě, čára za ním končí pod šipkou; natočení se bere
  // z úseku za hrotem, takže se šipka v zatáčkách otáčí plynule
  const s = DELKA_SIPKY + p * (celkem - DELKA_SIPKY);
  const [hx, hy] = poloha(s), [zx, zy] = poloha(s - 40);
  const uhel = Math.atan2(hy - zy, hx - zx) * 180 / Math.PI;
  const dosed = 1 + 0.12 * Math.sin(Math.PI * usek(t, 2.0, 2.3));
  $('#sipka').style.display = staticky ? '' : 'none';
  $('#hlavice').style.display = staticky ? 'none' : '';
  if (staticky) {{
    $('#sipka').setAttribute('transform', `translate(${{hx}},${{hy}}) rotate(${{uhel}}) scale(${{dosed}})`);
    $('#jizda').setAttribute('stroke-dashoffset', 1000 * (1 - Math.max(0, s - 50) / celkem));
  }} else {{
    // hlavice dojede až na tečku čtyřky, čára pod ní celou cestou
    const [kx, ky] = poloha(p * celkem);
    const dojezd = {HROT_NAD} * usek(p * celkem, celkem - delky[2], celkem);
    $('#hlavice').setAttribute('transform', `translate(${{kx}},${{ky + dojezd}}) scale(${{dosed}})`);
    $('#jizda').setAttribute('stroke-dashoffset', 1000 * (1 - p));
  }}
  // zrychlení: ručička doletí s malým překmitem, oblouk se naplní
  const r = pruzne(usek(t, 2.05, 3.4));
  $('#rucicka').setAttribute('transform', `rotate(${{-120 + 228 * r}} 180 180)`);
  $('#oblouk-plny').setAttribute('stroke-dashoffset', 1000 * (1 - Math.min(1, r) * 0.95));
  document.querySelectorAll('.rychlost').forEach(c => {{
    const z = parseFloat(c.style.getPropertyValue('--zpozdeni'));
    const k = usek(t, 2.1 + z, 2.6 + z);
    // ve videu čáry prolétnou a zůstanou slabší, na obrázku drží naplno
    const zbytek = staticky ? 1 : 1 - 0.45 * usek(t, 3.2 + z, 3.8 + z);
    c.style.opacity = k * zbytek;
    c.style.transform = `translateX(${{-80 * (1 - k)}}px) scaleX(${{0.3 + 0.7 * k}})`;
  }});
  // křížek do rámečku strany
  $('#tah1').setAttribute('stroke-dashoffset', 100 * (1 - hladce(usek(t, 3.6, 3.95))));
  $('#tah2').setAttribute('stroke-dashoffset', 100 * (1 - hladce(usek(t, 4.05, 4.4))));
  const pop = hladce(usek(t, 4.6, 5.2));
  $('#popisek').style.opacity = pop;
  $('#popisek').style.transform = `translateY(${{18 * (1 - pop)}}px)`;
}}
"""
    return stranka(telo, styl, skript)


# --- Děkujeme ----------------------------------------------------------------
# Musí sedět na jakýkoli výsledek: nikde „vyhráli“, „zvolení“ ani „mandát“.
# Děkuje se za hlasy a rozhovory a slibuje se jen to, co platí vždycky —
# že pro město budeme pracovat dál.

def dekujeme(web: dict, texty: dict) -> str:
    foto = dataurl(KOREN / 'src/obrazky/spolecna-2000.webp', 'image/webp')
    odstavce = ''.join(f'<p class="veta" data-od="{1.9 + i * 0.7}">{v}</p>'
                       for i, v in enumerate(texty['vety']))
    telo = f"""{hlavicka(web)}
<div class="foto"><img src="{foto}" alt=""></div>
<div class="text">
  <h1 class="bricolage dekujeme">{texty['titulek']}</h1>
  <div class="podtrzeni"></div>
  {odstavce}
  <p class="podpis veta" data-od="{1.9 + len(texty['vety']) * 0.7 + 0.3}">{texty['podpis']}</p>
</div>
<div class="srdce">{znak(170, web['cislo'], 'velke')}</div>"""
    styl = f"""
.foto {{ position: absolute; left: 44px; right: 44px; top: 164px; height: 470px;
  border-radius: 28px; overflow: hidden; background: #fff; }}
.foto img {{ width: 100%; height: 100%; object-fit: cover; object-position: 50% 62%;
  transform-origin: 50% 60%; }}
.text {{ position: absolute; left: 64px; right: 64px; top: 676px; }}
.dekujeme {{ margin: 0; font-size: 150px; }}
.podtrzeni {{ height: 10px; width: 420px; border-radius: 10px; background: {PRECHOD};
  margin: 18px 0 30px; transform-origin: left center; }}
.veta {{ margin: 0 0 18px; font-size: 35px; line-height: 1.4; color: #40372f; max-width: 23em; }}
.podpis {{ margin-top: 30px; font-size: 30px; font-weight: 600; color: {CERVENA}; }}
.srdce {{ position: absolute; right: 58px; bottom: 46px; transform-origin: 50% 60%; }}
"""
    skript = """
function nastav(t, staticky) {
  $('.foto img').style.transform = `scale(${1.08 - 0.08 * hladce(usek(t, 0, 8))})`;
  const d = hladce(usek(t, 0.5, 1.2));
  $('.dekujeme').style.opacity = d;
  $('.dekujeme').style.transform = `translateY(${30 * (1 - d)}px)`;
  $('.podtrzeni').style.transform = `scaleX(${hladce(usek(t, 1.1, 1.8))})`;
  document.querySelectorAll('.veta').forEach(v => {
    const k = hladce(usek(t, +v.dataset.od, +v.dataset.od + 0.6));
    v.style.opacity = k; v.style.transform = `translateY(${16 * (1 - k)}px)`;
  });
  // srdce na konci jednou tepne
  const s = usek(t, 4.6, 5.4), tep = 1 + 0.14 * Math.sin(Math.PI * s);
  $('.srdce').style.opacity = hladce(usek(t, 4.3, 4.8));
  $('.srdce').style.transform = `scale(${tep})`;
}
"""
    return stranka(telo, styl, skript)


# --- focení ------------------------------------------------------------------

def _browserless(kod: str, kontext: dict) -> dict:
    vysledek = subprocess.run(
        ['curl', '-sS', '-m', '600', '-X', 'POST', BROWSERLESS + '/function',
         '-H', 'Content-Type: application/json', '--data-binary', '@-'],
        input=json.dumps({'code': kod, 'context': kontext}), text=True, capture_output=True)
    try:
        return json.loads(vysledek.stdout)
    except json.JSONDecodeError:
        sys.exit(f'browserless: {vysledek.stdout[:300]} {vysledek.stderr[:300]}')


def nafot(html: str, casy: list[float], staticky: bool, typ='jpeg') -> list[bytes]:
    """Stránku jednou načte a pro každý čas z `casy` vrátí snímek."""
    kod = f"""module.exports = async ({{ page, context }}) => {{
  await page.setViewport({{ width: {SIRKA}, height: {VYSKA}, deviceScaleFactor: 1 }});
  await page.setContent(context.html, {{ waitUntil: 'networkidle0' }});
  await page.evaluate(() => document.fonts.ready);
  const snimky = [];
  for (const t of context.casy) {{
    await page.evaluate((t, s) => nastav(t, s), t, context.staticky);
    snimky.push(await page.screenshot({{ type: '{typ}', {'quality: 92, ' if typ == 'jpeg' else ''}encoding: 'base64' }}));
  }}
  return {{ data: snimky, type: 'application/json' }};
}};"""
    return [base64.b64decode(s) for s in _browserless(kod, {'html': html, 'casy': casy,
                                                             'staticky': staticky})]


def zvuk_hod_tam_4(cil: Path, delka: float) -> None:
    """Cvaknutí páky, dosednutí do čtyřky, vzrůstající „fíí“ a škrábnutí tužky.

    Všechno se syntetizuje ffmpegem — žádné cizí zvuky, které by se musely
    licencovat. Na Facebooku se stejně většinou přehrává bez zvuku, takže je
    zvuk tichý doprovod, ne nosná vrstva.
    """
    def obalka(od, trvani):
        return f"afade=t=in:st={od}:d=0.005,afade=t=out:st={od}:d={trvani},adelay={int(od*1000)}:all=1"
    vstupy = [
        # cvaknutí, když páka vyjede z jedničky
        "anoisesrc=d=0.05:c=white:a=0.6,highpass=f=2500,afade=t=out:st=0:d=0.05,adelay=700:all=1",
        # dosednutí do čtyřky: krátké nízké ťuknutí
        "sine=f=110:d=0.14,volume=0.9,afade=t=out:st=0:d=0.14,adelay=2000:all=1",
        "anoisesrc=d=0.06:c=pink:a=0.5,lowpass=f=900,afade=t=out:st=0:d=0.06,adelay=2000:all=1",
        # fíí: šum se zvedajícím se tónem, rozjezd a doznění
        "anoisesrc=d=1.5:c=pink:a=0.35,bandpass=f=1800:w=1600,afade=t=in:d=0.25,"
        "afade=t=out:st=0.6:d=0.9,adelay=2100:all=1",
        "aevalsrc='0.16*sin(2*PI*(260*t+520*t*t))*min(1\\,t*6)*max(0\\,1-t/1.4)':d=1.4,"
        "adelay=2100:all=1",
        # dva tahy tužkou při křížku
        "anoisesrc=d=0.3:c=brown:a=0.25,highpass=f=1200,afade=t=out:st=0.1:d=0.2,adelay=3600:all=1",
        "anoisesrc=d=0.3:c=brown:a=0.25,highpass=f=1200,afade=t=out:st=0.1:d=0.2,adelay=4050:all=1",
    ]
    filtr = ';'.join(f'{v}[a{i}]' for i, v in enumerate(vstupy))
    filtr += ';' + ''.join(f'[a{i}]' for i in range(len(vstupy)))
    filtr += f'amix=inputs={len(vstupy)}:normalize=0,apad=whole_dur={delka},alimiter=limit=0.8[out]'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-filter_complex', filtr, '-map', '[out]',
                    '-t', str(delka), '-ar', '48000', '-ac', '2', str(cil)], check=True)


def video(jmeno: str, html: str, delka: float, zvuk=None) -> Path:
    prac = PRACOVNI / jmeno
    shutil.rmtree(prac, ignore_errors=True)
    prac.mkdir(parents=True)
    casy = [i / FPS for i in range(int(delka * FPS))]
    # po dávkách, ať odpověď browserless nenaroste do desítek megabajtů
    for od in range(0, len(casy), 45):
        for i, snimek in enumerate(nafot(html, casy[od:od + 45], False), start=od):
            (prac / f'{i:04d}.jpg').write_bytes(snimek)
    stopa = prac / 'zvuk.wav'
    if zvuk:
        zvuk(stopa, delka)
    else:
        # tichá stopa: některé přehrávače bez zvuku video nepustí jako video
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i',
                        'anullsrc=r=48000:cl=stereo', '-t', str(delka), str(stopa)], check=True)
    cil = VIDEA_VEN / f'{jmeno}.mp4'
    cil.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', str(FPS),
                    '-i', str(prac / '%04d.jpg'), '-i', str(stopa),
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p',
                    '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart',
                    str(cil)], check=True)
    shutil.rmtree(prac, ignore_errors=True)
    return cil


VYZVY = {
    'hod-tam-4': {'delka': 8.0, 'konec': 8.0, 'zvuk': zvuk_hod_tam_4},
    'dekujeme': {'delka': 8.0, 'konec': 8.0, 'zvuk': None},
}


def main() -> None:
    p = argparse.ArgumentParser(description='Výzvy na sociální sítě')
    p.add_argument('co', nargs='*', default=list(VYZVY), choices=list(VYZVY))
    p.add_argument('--bez-videa', action='store_true')
    args = p.parse_args()

    web = nacti_web()
    texty = nacti('socialni.json')['vyzvy']
    kandidati = nacti('kandidati.json')

    for jmeno in args.co:
        html = (hod_tam_4(web, texty[jmeno], kandidati) if jmeno == 'hod-tam-4'
                else dekujeme(web, texty[jmeno]))
        nastaveni = VYZVY[jmeno]
        OBRAZKY_VEN.mkdir(parents=True, exist_ok=True)
        obr = OBRAZKY_VEN / f'{jmeno}.png'
        obr.write_bytes(nafot(html, [nastaveni['konec']], True, 'png')[0])
        print(f'  {obr.relative_to(KOREN)}  {SIRKA} × {VYSKA}')
        if not args.bez_videa:
            cil = video(jmeno, html, nastaveni['delka'], nastaveni['zvuk'])
            print(f'  {cil.relative_to(KOREN)}  {nastaveni["delka"]:.0f} s')


if __name__ == '__main__':
    main()
