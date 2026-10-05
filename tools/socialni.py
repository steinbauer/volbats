#!/usr/bin/env python3
"""Karty na Instagram a Facebook — jedna grafika, obsah se točí.

    python3 tools/socialni.py                    # všechno do socialni/
    python3 tools/socialni.py kandidati          # jen lidi
    python3 tools/socialni.py temata             # jen témata
    python3 tools/socialni.py --format ctverec   # 1:1 místo 4:5
    python3 tools/socialni.py --vse-formaty      # všechny tři rozměry naráz

Prvních deset kandidátů dostane kartu s heslem a větou, zbytek listiny kartu
prostou — jméno, povolání a pořadí. Kdo skončí na sedmnáctém místě, nepotřebuje
slogan; potřebuje být vidět.

Sází se stejně jako tiskoviny — HTML vyfocené Chromem přes browserless na
:3000 — jen výstup není PDF v milimetrech, ale PNG v pixelech. Obsah i značka
se berou z týchž dat jako web a leták, takže na kartě nemůže být jiné srdce,
jiné volební číslo ani jiný text programu.

Hesla a věty ke kartám žijí v src/data/socialni.json, ať je jde přepsat bez
sahání do sazby.
"""
import argparse
import base64
import io
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tiskoviny import (BROWSERLESS, CERVENA, IKONY, INKOUST, KOREN, OBRAZKY, ORANZOVA,
                       SRDCE, VIEWBOX, ZLUTA, dataurl, fonty, nacti, nacti_web)

VYSTUP = KOREN / 'socialni'

# 4:5 je největší plocha, kterou Instagram i Facebook pustí do nástěnky, a platí
# pro oba kanály stejně — zvlášť pro Facebook se nic generovat nemusí. Čtverec
# je tu proto, že v něm přišly předlohy a někomu se líp skládá do galerie.
FORMATY = {
    'feed': (1080, 1350),     # 4:5 — hlavní formát, Instagram i Facebook
    'ctverec': (1080, 1080),  # 1:1 — galerie, sdílení do skupin
    'story': (1080, 1920),    # 9:16 — stories na obou sítích
}

# Stories překrývá aplikace nahoře i dole; obsah musí zůstat mezi tím.
BEZPECNA_ZONA = {'feed': (0, 0), 'ctverec': (0, 0), 'story': (230, 300)}

# Do téhle hranice na kandidátce se reálně hraje o zastupitelstvo (21 křesel),
# takže těmhle lidem stojí za to dát na kartu i heslo a větu.
S_TEXTEM_DO = 10

# Svislý rozsah hlavy v každém portrétu, aby ořez neuťal temeno ani bradu.
# Odečteno ručně, viz hlavička src/data/fotky-hlavy.json.
HLAVY = nacti('fotky-hlavy.json')['hlavy']
# Komu má být na kartě vidět i krk: spodní okraj rámu v procentech snímku.
# Přednost má před celým temenem, které pak rám může uříznout.
SPODEK = nacti('fotky-hlavy.json').get('spodek', {})

PORTRET = (1200, 1600)   # všechny portréty kandidátů mají tenhle rozměr

# Značka vyplní v obrázku placeholder, který se po změření rámu nahradí
# spočítanou svislou pozicí ořezu.
POS = '__POS__'

PLOCHA = 'linear-gradient(0.25turn, #fdf7e4, #fdeee7)'
PRECHOD = f'linear-gradient(0.25turn, {ZLUTA}, {ORANZOVA})'
TLUMENY = '#6b5f55'


# --- značka v pixelech -------------------------------------------------------
# tiskoviny.py sází srdce i ikony v milimetrech, protože míří na papír. Tady je
# cílem rastr, tak si totéž vykreslíme v px — křivky jsou ale tytéž.

VB_SIRKA, VB_VYSKA = (float(x) for x in VIEWBOX.split()[2:])


def znak(sirka_px: float, cislo=None, id_prechodu='p') -> str:
    vyska = sirka_px * VB_VYSKA / VB_SIRKA
    cifra = (f'<text x="520" y="492" text-anchor="middle" class="znak-cislo">{cislo}</text>'
             if cislo is not None else '')
    tahy = ''.join(f'<path d="{d}" fill="url(#{id_prechodu})"/>' for d in SRDCE)
    return (f'<svg viewBox="{VIEWBOX}" style="width:{sirka_px}px;height:{vyska:.0f}px">'
            f'<defs><linearGradient id="{id_prechodu}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{ZLUTA}"/><stop offset="1" stop-color="{ORANZOVA}"/>'
            f'</linearGradient></defs>{tahy}{cifra}</svg>')


def ikona(slug: str, velikost_px: float, id_prechodu: str, barva=None) -> str:
    tahy = IKONY.get(slug)
    if not tahy:
        return ''
    vypln = barva or f'url(#{id_prechodu})'
    defs = '' if barva else (
        f'<defs><linearGradient id="{id_prechodu}" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{ZLUTA}"/><stop offset="1" stop-color="{ORANZOVA}"/>'
        f'</linearGradient></defs>')
    cesty = ''.join(f'<path d="{d}" fill="{vypln}" fill-rule="evenodd"/>' for d in tahy)
    return (f'<svg viewBox="0 0 100 100" style="width:{velikost_px}px;height:{velikost_px}px">'
            f'{defs}{cesty}</svg>')


def orez(klic: str, ram_sirka: float, ram_vyska: float) -> float:
    """Svislá pozice ořezu v procentech, aby se do rámu vešla celá hlava.

    Rám je vždycky širší poměr než portrét 3:4, takže se z fotky ukáže jen
    vodorovný pruh. Bez počítání by `object-position` musela být pro všechny
    stejná — a protože lidé mají na snímcích hlavu jednou výš, jednou níž,
    někomu by uřízla temeno a jinému bradu.
    """
    od, do = HLAVY.get(klic, (20, 63))
    img_s, img_v = PORTRET
    if not ram_vyska or not ram_sirka:
        return 50.0

    # Kolik procent výšky snímku se do rámu vejde, když ho `cover` roztáhne
    # na šířku rámu.
    vidno = ram_vyska * img_s / (ram_sirka * img_v) * 100
    if vidno >= 100:
        return 50.0

    # Střed hlavy posunutý o kousek dolů: nad temenem stačí míň místa než
    # pod bradou, kde má být vidět krk a kus ramen.
    horni = (od + do) / 2 + 2 - vidno / 2
    # Uříznuté temeno je vidět víc než uříznutá ramena, tak má přednost.
    horni = min(horni, od - 2)
    if klic in SPODEK:
        horni = SPODEK[klic] - vidno
    return round(max(0.0, min(100.0, horni / (100 - vidno) * 100)), 1)


def fotka(cislo_foto: str) -> str:
    """Portrét kandidáta jako data URI — dokument musí být soběstačný."""
    cesta = OBRAZKY / f'{cislo_foto}-1200.webp'
    if not cesta.is_file():
        raise SystemExit(f'chybí {cesta}')
    return dataurl(cesta, 'image/webp')


# --- styl --------------------------------------------------------------------
# Celá karta stojí na krémovém podkladu z letáku. Žádná tmavá plocha ani šedý
# pruh pod fotkou: na kartě, kterou si má člověk spojit se svým městem, působí
# ztmavená zóna pohřebně. Text proto nikdy neleží na fotce — fotka se oreže
# a text dostane vlastní místo pod ní.

def styl(format: str) -> str:
    sirka, vyska = FORMATY[format]
    shora, zdola = BEZPECNA_ZONA[format]
    return f"""
{fonty()}

* {{ box-sizing: border-box; }}

html, body {{ margin: 0; padding: 0; background: #fff; }}

body {{
  font-family: 'IBM Plex Sans', sans-serif;
  color: {INKOUST};
  -webkit-font-smoothing: antialiased;
}}

.karta {{
  width: {sirka}px;
  height: {vyska}px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  background: {PLOCHA};
  padding: {40 + shora}px 44px {30 + zdola}px;
}}

.znak-cislo {{
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 430px; fill: {INKOUST};
}}

h1, h2, .heslo, .jmeno {{
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800;
  letter-spacing: -0.025em;
  line-height: 1.03;
  margin: 0;
}}

p {{ margin: 0; }}

/* --- hlavička: srdce s volebním číslem a název sdružení --- */
.hlavicka {{
  display: flex;
  align-items: center;
  gap: 20px;
  flex: none;
  margin-bottom: 26px;
}}
.hlavicka svg {{ flex: none; }}
.hlavicka__nazev {{
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800;
  font-size: 38px;
  line-height: 1.05;
  letter-spacing: -0.02em;
}}
.hlavicka__mesto {{ color: #9a7411; }}
.hlavicka__web {{
  margin-left: auto;
  font-size: 30px;
  font-weight: 600;
  letter-spacing: 0.02em;
  color: {CERVENA};
}}

/* Fotka a text pod sebou; na čtverci u karet s delším textem vedle sebe,
   protože z portrétu 3:4 by ve zbylém pruhu zůstalo čelo a nic víc. */
.telo {{
  flex: 1;
  min-height: 0;
  display: flex;
  flex-direction: column;
}}
.karta--ctverec.karta--plna .telo,
.karta--ctverec.karta--tema-tvar .telo {{
  flex-direction: row;
  gap: 32px;
}}
.karta--ctverec.karta--plna .snimek,
.karta--ctverec.karta--tema-tvar .snimek {{ flex: none; width: 45%; }}
.karta--ctverec.karta--plna .popis,
.karta--ctverec.karta--tema-tvar .popis {{
  flex: 1; min-width: 0; padding-top: 0;
  display: flex; flex-direction: column; justify-content: center;
}}
.karta--ctverec.karta--plna .jmeno {{ font-size: 56px; }}
.karta--ctverec.karta--plna .jmeno--dlouhe {{ font-size: 46px; }}
.karta--ctverec.karta--plna .povolani {{ font-size: 24px; }}
.karta--ctverec.karta--plna .heslo {{ font-size: 44px; margin-top: 22px; }}
.karta--ctverec.karta--plna .heslo--dlouhe {{ font-size: 38px; }}
.karta--ctverec.karta--plna .text {{ font-size: 25px; }}
.karta--ctverec.karta--tema-tvar .heslo {{ font-size: 46px; }}
.karta--ctverec.karta--tema-tvar .heslo--dlouhe {{ font-size: 40px; }}
.karta--ctverec.karta--tema-tvar .text {{ font-size: 25px; }}
.karta--ctverec.karta--tema-tvar .podpis {{ font-size: 21px; }}
.karta--ctverec.karta--tema-tvar .podpis b {{ font-size: 24px; }}

/* --- fotka: zabere, co zbude, a má vlastní papír --- */
.snimek {{
  flex: 1;
  min-height: 0;
  border-radius: 26px;
  overflow: hidden;
  position: relative;
  background: #fff;
}}
.snimek img {{
  width: 100%; height: 100%;
  object-fit: cover;
  object-position: 50% var(--orez, 20%);
  display: block;
}}

/* --- text pod fotkou --- */
.popis {{ flex: none; padding-top: 30px; }}

.poradi {{
  display: inline-flex; align-items: center; gap: 14px;
  font-size: 24px; font-weight: 600;
  letter-spacing: 0.15em; text-transform: uppercase;
  color: #8f2614;
  margin-bottom: 14px;
}}
.poradi::before {{
  content: ''; width: 46px; height: 5px; border-radius: 5px;
  background: {PRECHOD}; flex: none;
}}

.jmeno {{ font-size: 84px; }}
.jmeno--dlouhe {{ font-size: 68px; }}

.povolani {{
  font-size: 31px; line-height: 1.28; margin-top: 12px; color: {TLUMENY};
}}

.heslo {{ font-size: 66px; color: {CERVENA}; margin-top: 24px; }}
.heslo--dlouhe {{ font-size: 54px; }}

.text {{ font-size: 32px; line-height: 1.38; margin-top: 16px; color: #40372f; }}

/* --- karta bez textu: fotka dostane víc místa a jméno smí být velké --- */
.karta--prosta .snimek {{ border-radius: 30px; }}
.karta--prosta .jmeno {{ font-size: 100px; }}
.karta--prosta .jmeno--dlouhe {{ font-size: 80px; }}
.karta--prosta .povolani {{ font-size: 36px; }}

/* --- téma --- */
.stitek {{
  display: inline-flex; align-items: center; gap: 14px;
  font-size: 25px; font-weight: 600; letter-spacing: 0.16em;
  text-transform: uppercase; color: #8f2614; margin-bottom: 16px;
}}
.stitek svg {{ flex: none; }}
.karta--tema .heslo {{ color: {INKOUST}; margin-top: 0; }}

/* S tváří: kompozice je stejná jako u karty člověka, jen text mluví o tématu. */
.karta--tema-tvar .heslo {{ font-size: 70px; }}
.karta--tema-tvar .heslo--dlouhe {{ font-size: 58px; }}
.karta--tema-tvar .text {{ font-size: 32px; margin-top: 14px; }}
.podpis {{
  font-size: 27px; margin-top: 18px; color: {TLUMENY};
}}
.podpis b {{
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; color: {INKOUST}; font-size: 31px; letter-spacing: -0.02em;
}}

/* Bez tváře: plochu drží velká kresba tématu, ne prázdno. */
.karta--tema-holy {{ justify-content: center; }}
.karta--tema-holy .kresba {{ margin-bottom: 46px; }}
.karta--tema-holy .heslo {{ font-size: 96px; }}
.karta--tema-holy .heslo--dlouhe {{ font-size: 78px; }}
.karta--tema-holy .text {{ font-size: 36px; line-height: 1.36; margin-top: 28px; max-width: 15em; }}
.karta--tema-holy .stred {{ flex: none; }}
.vypln {{ flex: 1; min-height: 0; }}
"""


# --- sazba jednotlivých karet ------------------------------------------------

def _delka(text: str, mez: int) -> str:
    return ' heslo--dlouhe' if len(text) > mez else ''


def _hlavicka(web: dict, id_p: str) -> str:
    """Srdce s volebním číslem, název sdružení a adresa webu.

    Volební číslo nese srdce, tak se vedle nevypisuje ještě slovy — místo něj
    je vpravo adresa, kde si člověk může zbytek dohledat.
    """
    return f"""<div class="hlavicka">
    {znak(96, web['cislo'], id_p)}
    <div class="hlavicka__nazev">{web['nazev']}<br>
      <span class="hlavicka__mesto">{web['mesto']}</span></div>
    <div class="hlavicka__web">volbats.cz</div>
  </div>"""


def _snimek(k: dict) -> str:
    """Fotka i s klíčem, podle kterého se po změření rámu dopočítá ořez."""
    return (f'<div class="snimek" data-foto="{k["foto"]}" style="--orez: {POS}%">'
            f'<img src="{fotka(k["foto"])}" alt=""></div>')


def karta_kandidat(k: dict, texty: dict, web: dict, varianta: str, format: str) -> str:
    """Kdo to je a v čem je silný.

    Prvních deset nese i heslo a větu — jsou to lidé, kteří po volbách reálně
    sednou do zastupitelstva. Zbytek kandidátky má kartu prostou: jméno,
    povolání a pořadí. Zadní část listiny nepotřebuje slogan, potřebuje být
    vidět.
    """
    t = texty.get(str(k['cislo']), {})
    povolani = t.get('povolani', k['povolani'])
    if k.get('cast') and k['cast'] != web['mesto']:
        povolani += f' · {k["cast"]}'

    jmeno = _zkrat_jmeno(k)
    dlouhe = ' jmeno--dlouhe' if len(jmeno) > 16 else ''

    obsah = f"""<div class="poradi">{k['cislo']}. na kandidátce</div>
    <h1 class="jmeno{dlouhe}">{jmeno}</h1>
    <p class="povolani">{povolani}</p>"""

    if varianta == 'plna':
        heslo = t.get('heslo', '')
        obsah += f"""
    <p class="heslo{_delka(heslo, 21)}">{heslo}</p>
    <p class="text">{t.get('text', '')}</p>"""

    return f"""<div class="karta karta--{varianta} karta--{format}">
  {_hlavicka(web, f'p{k["cislo"]}')}
  <div class="telo">
    {_snimek(k)}
    <div class="popis">{obsah}</div>
  </div>
</div>"""


def karta_tema(t: dict, sekce: dict, kandidati: list, texty: dict,
               web: dict, varianta: str, format: str) -> str:
    """Jeden bod programu jako heslo, ne jako výpis odrážek.

    S tváří má karta stejnou stavbu jako karta člověka — fotka nahoře, text
    pod ní. Kdo listuje nástěnkou, vidí pořád tentýž útvar a nemusí luštit,
    co se na něj dívá. Bez tváře drží plochu velká kresba tématu.
    """
    stitek = (f'<div class="stitek">{ikona(t["slug"], 44, "s-" + t["slug"])}'
              f'{sekce.get("stitek", "")}</div>')
    stitek_holy = f'<div class="stitek">{sekce.get("stitek", "")}</div>'
    heslo = f'<p class="heslo{_delka(t["heslo"], 22)}">{t["heslo"]}</p>'

    k = next((x for x in kandidati if x['cislo'] == t['kdo']), None) if t.get('kdo') else None

    if varianta == 'tema-tvar' and k:
        return f"""<div class="karta karta--tema karta--tema-tvar karta--{format}">
  {_hlavicka(web, 'z-' + t['slug'])}
  <div class="telo">
    {_snimek(k)}
    <div class="popis">
      {stitek}
      {heslo}
      <p class="text">{t['text']}</p>
      <p class="podpis">ručí za to <b>{_zkrat_jmeno(k)}</b>,
        {_kdo(k)}{k['cislo']}. na kandidátce</p>
    </div>
  </div>
</div>"""

    return f"""<div class="karta karta--tema karta--tema-holy karta--{format}">
  {_hlavicka(web, 'z-' + t['slug'])}
  <div class="vypln"></div>
  <div class="stred">
    <div class="kresba">{ikona(t['slug'], 260, 'i-' + t['slug'])}</div>
    {stitek_holy}
    {heslo}
    <p class="text">{t['text']}</p>
  </div>
  <div class="vypln"></div>
</div>"""


def _kdo(k: dict) -> str:
    """Povolání do podpisu — celé, nebo vůbec.

    Uříznout ho na první čárce nejde: z „ředitelka mateřské, základní
    a praktické školy“ by zbyla „ředitelka mateřské“. Delší funkce se tedy
    na kartu tématu nedostane a podpis zůstane u jména.
    """
    povolani = k['povolani'].strip()
    if len(povolani) > 40:
        return ''
    return povolani[0].lower() + povolani[1:] + ', '


def _zkrat_jmeno(k: dict) -> str:
    """Jméno na kartu i s tituly, přesně jak stojí na kandidátní listině.

    Původně se tituly škrtaly a nechávaly jen tam, kde nesou informaci
    (MUDr., Ing. arch.). Od 27. 9. 2026 je kampaň chce u všech.
    """
    return k['jmeno'].strip()


def dokument(karta_html: str, format: str) -> str:
    return (f'<!doctype html><html lang="cs"><head><meta charset="utf-8">'
            f'<style>{styl(format)}</style></head><body>{karta_html}</body></html>')


# --- focení ------------------------------------------------------------------

def vyfot(html: str, cil: Path, format: str) -> None:
    sirka, vyska = FORMATY[format]
    cil.parent.mkdir(parents=True, exist_ok=True)
    telo = {'html': html,
            'options': {'type': 'png', 'fullPage': False},
            'viewport': {'width': sirka, 'height': vyska, 'deviceScaleFactor': 1}}
    odpoved = subprocess.run(
        ['curl', '-sS', '-m', '120', '-X', 'POST', BROWSERLESS + '/screenshot',
         '-H', 'Content-Type: application/json', '--data-binary', '@-',
         '-o', str(cil), '-w', '%{http_code}'],
        input=json.dumps(telo), text=True, capture_output=True)
    if odpoved.stdout.strip() != '200':
        sys.exit(f'browserless vrátil {odpoved.stdout} u {cil.name}: {odpoved.stderr[:300]}')


def zmer(html: str) -> dict:
    """Změří přetečení obsahu a skutečný rám fotky.

    Rám fotky vychází z toho, co na kartě zbude po textu, takže ho dopředu
    neznáme — a bez něj nejde spočítat, kde fotku oříznout, aby v ní zůstala
    celá hlava. Proto se karta vyrendruje dvakrát: jednou na míru, podruhé
    nastop.
    """
    kod = ('module.exports=async({page})=>{await page.setContent(HTML,{waitUntil:"networkidle0"});'
           'const r=await page.evaluate(()=>{const k=document.querySelector(".karta");'
           'const s=k.querySelector(".snimek");const b=s&&s.getBoundingClientRect();'
           'return{v:Math.round(k.scrollHeight),limit:Math.round(k.clientHeight),'
           'foto:s?s.dataset.foto:null,'
           'ram:b?[Math.round(b.width),Math.round(b.height)]:null}});'
           'return{data:r,type:"application/json"}}').replace('HTML', json.dumps(html))
    odpoved = subprocess.run(
        ['curl', '-sS', '-m', '120', '-X', 'POST', BROWSERLESS + '/function',
         '-H', 'Content-Type: application/json', '--data-binary', '@-'],
        input=json.dumps({'code': kod, 'context': {}}), text=True, capture_output=True)
    try:
        return json.loads(odpoved.stdout)
    except Exception:
        return {}


def uloz(ukoly: list, format: str) -> None:
    """Karty se fotí souběžně — jinak by celá sada trvala minuty."""
    def jeden(u):
        mira = zmer(dokument(u['html'].replace(POS, '20'), format))
        pozice = orez(mira.get('foto'), *(mira.get('ram') or (0, 0))) if mira.get('foto') else 20
        vyfot(dokument(u['html'].replace(POS, str(pozice)), format), u['cil'], format)
        return u['cil'], mira, pozice

    with ThreadPoolExecutor(max_workers=4) as bazen:
        for cil, mira, pozice in bazen.map(jeden, ukoly):
            preteklo = mira.get('v', 0) - mira.get('limit', 0)
            stav = f'  PŘETÉKÁ o {preteklo} px' if preteklo > 1 else ''
            print(f'  {cil.relative_to(KOREN)}  ořez {pozice} %{stav}')


# --- přehled na výběr ---------------------------------------------------------

def nahled(cesta: Path, sirka=380) -> str:
    """Náhled jako data URI, ať je přehled jeden soubor k poslání mailem."""
    from PIL import Image
    obr = Image.open(cesta).convert('RGB')
    obr.thumbnail((sirka, sirka * 3), Image.LANCZOS)
    buf = io.BytesIO()
    obr.save(buf, 'JPEG', quality=72, optimize=True)
    return 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()


def prehled(web: dict, kandidati: list, soc: dict) -> Path:
    """Stránka se všemi hotovými kartami — na výběr témat a na kontrolu textů."""
    def dlazdice(cesta: Path, popis: str) -> str:
        if not cesta.is_file():
            return ''
        return (f'<figure><img src="{nahled(cesta)}" alt="">'
                f'<figcaption>{popis}</figcaption></figure>')

    feed = VYSTUP / 'feed'
    jmena = {k['cislo']: _zkrat_jmeno(k) for k in kandidati}

    def karty_lidi(od: int, do: int) -> str:
        return '<div class="mrizka">' + ''.join(
            dlazdice(feed / 'lide' / f'{k["cislo"]:02d}-{k["slug"]}.png',
                     f'{k["cislo"]}. {jmena[k["cislo"]]}'
                     + (' <b>· text k doladění</b>'
                        if soc['kandidati'].get(str(k['cislo']), {}).get('overit') else ''))
            for k in kandidati if od <= k['cislo'] <= do) + '</div>'

    temata = '<div class="mrizka">' + ''.join(
        dlazdice(feed / 'temata' / f'{t["slug"]}.png', t['heslo']) for t in soc['temata']) + '</div>'

    rozmery = ''
    for f in FORMATY:
        for cislo in (4, 17):
            k = next(x for x in kandidati if x['cislo'] == cislo)
            rozmery += dlazdice(VYSTUP / f / 'lide' / f'{k["cislo"]:02d}-{k["slug"]}.png',
                                f'{FORMATY[f][0]} × {FORMATY[f][1]} px')

    doladit = ''.join(
        f'<li><b>{k["cislo"]}. {jmena[k["cislo"]]}</b> ({k["povolani"].lower()})</li>'
        for k in kandidati
        if soc['kandidati'].get(str(k['cislo']), {}).get('overit'))

    html = f"""<!doctype html><html lang="cs"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Karty na Instagram a Facebook — {web['nazev']} {web['mesto']}</title>
<style>
  body {{ margin:0; background:linear-gradient(0.25turn,#fdf7e4,#fdeee7); color:#2c2521;
         font:16px/1.6 'IBM Plex Sans','Segoe UI',system-ui,sans-serif; }}
  .obal {{ max-width:1180px; margin:0 auto; padding:40px 20px 80px; }}
  h1,h2,h3 {{ font-family:'Bricolage Grotesque','Trebuchet MS',system-ui,sans-serif;
              font-weight:800; line-height:1.15; letter-spacing:-.02em; }}
  h1 {{ font-size:clamp(1.8rem,4.5vw,2.6rem); margin:0 0 .3em; }}
  h2 {{ font-size:1.5rem; margin:56px 0 .2em; }}
  h3 {{ font-size:1.05rem; margin:30px 0 .4em; color:#8f2614; }}
  p {{ max-width:66ch; }}
  .lead {{ font-size:1.08rem; }}
  .mrizka {{ display:grid; gap:16px; margin:16px 0 28px;
             grid-template-columns:repeat(auto-fill,minmax(210px,1fr)); }}
  .rozmery {{ display:grid; gap:16px; margin:16px 0 28px;
              grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); align-items:start; }}
  figure {{ margin:0; background:#fff; border:1px solid #e6dfcd; border-radius:12px; padding:10px; }}
  figure img {{ width:100%; display:block; border-radius:6px; }}
  figcaption {{ font-size:.82rem; color:#6b5f55; padding:9px 2px 2px; }}
  figcaption b {{ color:#c23a22; }}
  .papir {{ background:#fff; border:1px solid #e6dfcd; border-radius:14px;
            padding:22px 26px; margin:18px 0; }}
  code {{ background:#f4efe2; padding:1px 5px; border-radius:4px; font-size:.88em; }}
  ul {{ max-width:66ch; }}
</style></head><body><div class="obal">
<h1>Karty na Instagram a Facebook</h1>
<p class="lead">Jedna grafika, obsah se točí. Všechno stojí na krémovém podkladu z letáku,
nikde není tmavá plocha ani šedý pruh — text má vždycky vlastní místo pod fotkou
a fotka se pro něj oreže. Nahoře je srdce s volebním číslem, název sdružení a adresa webu;
dole už nic, aby zbylo místo na velké písmo.</p>

<h2>1. Rozměr a ořez</h2>
<p>Hotové je 4:5, tedy 1080 × 1350. Facebook i Instagram berou tentýž poměr, takže
zvlášť pro jednu a druhou síť se nic negeneruje — je to jeden a týž soubor. Čtverec
a stories skript umí taky, stačí říct.</p>
<p>Ořez se u každé fotky počítá zvlášť, aby v rámu zůstala celá hlava a pod bradou
kousek krku a ramen. Lidé mají na snímcích hlavu jednou výš, jednou níž; kdyby byl ořez
pro všechny stejný, někomu by uťal temeno a jinému bradu.</p>
<div class="rozmery">{rozmery}</div>

<h2>2. Prvních deset — karta s textem</h2>
<p>Tihle lidé po volbách reálně sednou do zastupitelstva, tak mají na kartě i heslo
a větu, v čem jsou silní.</p>
{karty_lidi(1, 10)}

<h2>3. Zbytek kandidátky — karta prostá</h2>
<p>Jméno, povolání a pořadí. Kdo je sedmnáctý, nepotřebuje slogan — potřebuje být vidět,
protože i jeho hlasy se počítají celé kandidátce.</p>
{karty_lidi(11, 23)}

<h2>4. Témata — vyberte, která se budou zveřejňovat</h2>
<p>Patnáct sekcí programu přeložených do hesla a jedné věty. Karta má stejnou stavbu
jako karta člověka: nahoře fotka toho, kdo za téma ručí, pod ní heslo. Kdo listuje
nástěnkou, vidí pořád tentýž útvar.</p>
{temata}

<h2>5. Co je potřeba doladit</h2>
<div class="papir">
<p>U těchhle lidí nemáme životopis, takže věta na kartě je jen návrh podle povolání.
Karta jim zatím vychází prostá, takže na nic nečeká — ale kdyby se některý z nich měl
objevit s textem, měl by si ho potvrdit vlastními slovy:</p>
<ul>{doladit}</ul>
</div>

<h2>6. Jak se to vyrábí</h2>
<div class="papir">
<p>Texty žijí v <code>src/data/socialni.json</code>, sazba v <code>tools/socialni.py</code>.
Změna hesla je změna jednoho řádku v datech, pak:</p>
<p><code>make socialni</code> — karty 4:5 do <code>socialni/feed/</code><br>
<code>python3 tools/socialni.py --vse-formaty</code> — všechny tři rozměry<br>
<code>python3 tools/socialni.py --format ctverec</code> — jen čtverec<br>
<code>python3 tools/socialni.py --prehled</code> — tahle stránka</p>
<p>Skript hlídá, jestli se text na kartu vejde — useknutý řádek je na kartě vidět
stejně jako na tiskovině, jen ho vidí víc lidí.</p>
</div>
</div></body></html>"""

    cil = VYSTUP / 'prehled.html'
    cil.write_text(html, encoding='utf-8')
    return cil


# --- sestavení ---------------------------------------------------------------

def _varianta(k: dict) -> str:
    return 'plna' if k['cislo'] <= S_TEXTEM_DO else 'prosta'


def main() -> None:
    p = argparse.ArgumentParser(description='Karty na Instagram a Facebook')
    p.add_argument('co', nargs='?', default='vse', choices=['vse', 'kandidati', 'temata'])
    p.add_argument('--format', default='feed', choices=list(FORMATY))
    p.add_argument('--vse-formaty', action='store_true',
                   help='všechny tři rozměry naráz')
    p.add_argument('--varianta', default=None, choices=['plna', 'prosta'],
                   help='vynutí jedno rozvržení pro všechny; jinak podle pořadí')
    p.add_argument('--tema-varianta', default='tema-tvar', choices=['tema', 'tema-tvar'])
    p.add_argument('--ukazky', action='store_true',
                   help='od každé varianty pár kusů na výběr, nic víc')
    p.add_argument('--prehled', action='store_true',
                   help='stránka s náhledy hotových karet, na výběr')
    args = p.parse_args()

    web = nacti_web()
    kandidati = nacti('kandidati.json')
    program = {s['slug']: s for s in nacti('program.json')['sekce']}
    soc = nacti('socialni.json')
    texty = soc['kandidati']

    if args.prehled:
        print(prehled(web, kandidati, soc).relative_to(KOREN))
        return

    formaty = list(FORMATY) if args.vse_formaty else [args.format]

    for f in formaty:
        ukoly = []

        if args.ukazky:
            for k in kandidati:
                if k['cislo'] not in (1, 4, 15, 17):
                    continue
                v = args.varianta or _varianta(k)
                ukoly.append({'html': karta_kandidat(k, texty, web, v, f),
                              'cil': VYSTUP / 'ukazky' / f'{f}-kandidat-{v}-{k["cislo"]:02d}.png'})
            for varianta in ('tema-tvar', 'tema'):
                for t in soc['temata'][:2]:
                    ukoly.append({'html': karta_tema(t, program.get(t['slug'], {}), kandidati,
                                                     texty, web, varianta, f),
                                  'cil': VYSTUP / 'ukazky' / f'{f}-{varianta}-{t["slug"]}.png'})
            print(f'ukázky ({f}):')
            uloz(ukoly, f)
            continue

        if args.co in ('vse', 'kandidati'):
            for k in kandidati:
                v = args.varianta or _varianta(k)
                ukoly.append({'html': karta_kandidat(k, texty, web, v, f),
                              'cil': VYSTUP / f / 'lide' / f'{k["cislo"]:02d}-{k["slug"]}.png'})

        if args.co in ('vse', 'temata'):
            for t in soc['temata']:
                ukoly.append({'html': karta_tema(t, program.get(t['slug'], {}), kandidati,
                                                 texty, web, args.tema_varianta, f),
                              'cil': VYSTUP / f / 'temata' / f'{t["slug"]}.png'})

        print(f'{len(ukoly)} karet ({f}, {FORMATY[f][0]} × {FORMATY[f][1]}):')
        uloz(ukoly, f)


if __name__ == '__main__':
    main()
