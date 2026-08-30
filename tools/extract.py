#!/usr/bin/env python3
"""Vytáhne obsah ze staré statické kopie (site/) do JSON pro React aplikaci.

Stará kopie je výstup z PolyWeb CMS, takže je obalená vrstvami divů
(blok_o, jeden_i, odstavec_NNNNN...), které nenesou žádný význam. Bereme
z ní jen to, co je obsah: nadpis, HTML textu a obrázky.

Spouští se jednorázově při migraci; až se obsah začne psát v repu, tenhle
skript je k ničemu a půjde smazat.
"""
import json, re, shutil
from pathlib import Path
from bs4 import BeautifulSoup

SRC = Path('site')
OUT = Path('src/data')
IMG_OUT = Path('src/obrazky')

OUT.mkdir(parents=True, exist_ok=True)
IMG_OUT.mkdir(parents=True, exist_ok=True)

obrazky = {}          # původní cesta -> nové jméno souboru


def soup_of(rel: str) -> BeautifulSoup:
    return BeautifulSoup((SRC / rel).read_text(encoding='utf-8'), 'lxml')


def zkopiruj_obrazek(page_rel: str, src_attr: str) -> str:
    """Zkopíruje obrázek do public/obrazky/ a vrátí novou absolutní cestu."""
    if src_attr.startswith(('http://', 'https://', 'data:')):
        return src_attr
    cesta = (SRC / page_rel).parent.joinpath(src_attr).resolve()
    try:
        cesta.relative_to(SRC.resolve())
    except ValueError:
        return src_attr
    if not cesta.is_file():
        return src_attr
    klic = str(cesta)
    if klic not in obrazky:
        jmeno = cesta.name
        # CMS jména jsou unikátní (g_4957_38979.jpg, 28035_skolstv.jpg),
        # ale kdyby přece jen kolidovala, přidáme pořadí.
        if any(v == jmeno for v in obrazky.values()):
            jmeno = f'{len(obrazky)}-{jmeno}'
        shutil.copy2(cesta, IMG_OUT / jmeno)
        obrazky[klic] = jmeno
    # Bez lomítka na začátku: cesty pak projdou mapou v src/obrazky.js,
    # která je nahradí hashovanou URL od Vite.
    return f'obrazky/{obrazky[klic]}'


def uklid_html(node, page_rel: str) -> str:
    """Z CMS bloku udělá čisté HTML: obsah bez obalů, s opravenými cestami."""
    for tag in node.select('.clear, .clear-galerie, script, .formular_obal'):
        tag.decompose()
    # Galerie měla v CMS třídu podle svého ID (galerie_obal_4957); šablona na ni
    # cílila natvrdo. Sjednocujeme na .galerie, aby styl nezávisel na čísle.
    for galerie in node.select('[class*="galerie_obal_"]'):
        galerie['class'] = ['galerie']
    for a_kotva in node.select('a[id^="od_"], a[name]'):
        if not a_kotva.get('href'):
            a_kotva.decompose()
    for img in node.select('img'):
        if img.get('src'):
            img['src'] = zkopiruj_obrazek(page_rel, img['src'])
        img.attrs.pop('loading', None)
        cls = img.get('class') or []
        img['class'] = [c for c in cls if c != 'img-fluid'] + ['img-fluid']
    for a in node.select('a[href]'):
        a['href'] = preloz_odkaz(page_rel, a['href'])
    html = node.decode_contents()
    html = re.sub(r'\n\s*\n+', '\n', html)
    return html.strip()


def preloz_odkaz(page_rel: str, href: str) -> str:
    """Relativní odkaz na starou strukturu přeloží na cestu v nové aplikaci."""
    if href.startswith(('http://', 'https://', 'mailto:', 'tel:', '#')):
        return href
    cil = (Path(page_rel).parent / href).as_posix()
    cil = str(Path(cil).resolve().relative_to(Path(page_rel).parent.resolve())) if False else cil
    cil = re.sub(r'(^|/)\./', r'\1', cil)
    while '../' in cil:
        cil = re.sub(r'[^/]+/\.\./', '', cil, count=1)
    # Lomítko na konci necháváme: adresa pak míří rovnou na předgenerovaný
    # soubor a při obnovení stránky nedojde k přesměrování.
    cil = cil.removesuffix('index.html')
    if cil and not cil.endswith('/'):
        cil += '/'
    return '/' + cil if cil else '/'


def obsah(rel: str):
    """Vrátí (nadpis, html) hlavního bloku stránky."""
    soup = soup_of(rel)
    content = soup.select_one('[class*="content"]')
    h1 = content.select_one('.kotva h1')
    nadpis = h1.get_text(strip=True) if h1 else ''
    if h1:
        h1.find_parent(class_='kotva').decompose()
    telo = content.select_one('.blok_o')
    return nadpis, uklid_html(telo or content, rel)


# --- kandidáti ------------------------------------------------------------
kandidati = []
soup = soup_of('kandidati/index.html')
for thumb in soup.select('.thumbnail'):
    nadpis_el = thumb.select_one('.caption h4')
    odkaz = thumb.select_one('.caption h4 a')
    foto = thumb.select_one('.embed-responsive-item img')
    info = thumb.select_one('.peopleInfo')
    cislo = thumb.select_one('.cislo')
    # Jen část kandidátů má vlastní medailonek; zbytek je pouze na kandidátce.
    slug = (odkaz['href'].split('/lide/')[-1].removesuffix('index.html').strip('/')
            if odkaz else None)
    kandidat = {
        'cislo': int(cislo.get_text(strip=True)) if cislo else None,
        'jmeno': (odkaz or nadpis_el).get_text(strip=True),
        'slug': slug,
        'foto': zkopiruj_obrazek('kandidati/index.html', foto['src']) if foto else None,
        'info': ' '.join(info.get_text(strip=True).split()) if info else '',
        'zivotopis': '',
    }
    detail = SRC / 'lide' / slug / 'index.html' if slug else None
    if detail and detail.is_file():
        _, html = obsah(f'lide/{slug}/index.html')
        kandidat['zivotopis'] = html
    kandidati.append(kandidat)
(OUT / 'kandidati.json').write_text(
    json.dumps(kandidati, ensure_ascii=False, indent=2), encoding='utf-8')

# --- priority -------------------------------------------------------------
priority = []
# Pořadí bereme z menu na homepage, kde jsou odkazy tvaru priority/<slug>/index.html
for li in soup_of('index.html').select('#top_menu .dropdown-menu a[href]'):
    href = li['href']
    if not href.startswith('priority/'):
        continue
    slug = href.removeprefix('priority/').removesuffix('index.html').strip('/')
    if not slug or not (SRC / 'priority' / slug / 'index.html').is_file():
        continue
    if any(p['slug'] == slug for p in priority):
        continue
    nadpis, html = obsah(f'priority/{slug}/index.html')
    priority.append({'slug': slug, 'nadpis': nadpis, 'html': html})
(OUT / 'priority.json').write_text(
    json.dumps(priority, ensure_ascii=False, indent=2), encoding='utf-8')

# --- jednoduché stránky ---------------------------------------------------
stranky = {}
for klic, rel in [('home', 'index.html'), ('program', 'program/index.html'),
                  ('priority', 'priority/index.html'), ('kontakt', 'kontakt/index.html')]:
    nadpis, html = obsah(rel)
    stranky[klic] = {'nadpis': nadpis, 'html': html}

# Program má pod úvodním textem dvousloupcovou tabulku „Podařilo se / Chceme".
# V HTML to jsou samostatné .row.border mimo hlavní CMS blok, takže je bereme
# zvlášť a v Reactu je vykreslíme jako data, ne jako slepené HTML.
soup_p = soup_of('program/index.html')
radky = []
for radek in soup_p.select('.col-12.content .row.border'):
    sloupce = []
    for sloupec in radek.select('[class*="col-"]'):
        nadpis_el = sloupec.find(['h2', 'h3'])
        nadpis_text = nadpis_el.get_text(strip=True) if nadpis_el else ''
        if nadpis_el:
            nadpis_el.decompose()
        sloupce.append({
            'nadpis': nadpis_text,
            'html': uklid_html(sloupec, 'program/index.html'),
        })
    if sloupce:
        radky.append(sloupce)
(OUT / 'program-tabulka.json').write_text(
    json.dumps(radky, ensure_ascii=False, indent=2), encoding='utf-8')
print(f'program:   {len(radky)} řádků tabulky')

# Kandidátka má vlastní stránku s úvodním textem; dlaždice se skládají
# z kandidati.json, takže z HTML bereme jen ten úvod.
soup_k = soup_of('kandidati/index.html')
uvod = soup_k.select_one('.col-12.content .odstavec')
stranky['kandidati'] = {
    'nadpis': soup_k.select_one('.col-12.content .kotva h1').get_text(strip=True),
    'html': uklid_html(uvod, 'kandidati/index.html') if uvod else '',
}
(OUT / 'stranky.json').write_text(
    json.dumps(stranky, ensure_ascii=False, indent=2), encoding='utf-8')

print(f'kandidáti: {len(kandidati)}')
print(f'priority:  {len(priority)}')
print(f'stránky:   {len(stranky)}')
print(f'obrázky:   {len(obrazky)}')
