#!/usr/bin/env python3
"""Přegeneruje src/data/kandidati.json podle kandidátní listiny pro volby 2026.

Jednorázový skript k výměně lidí. Kdo na listině zůstal, podrží si fotku,
medailonek i popisek pod fotkou (jen se srovná věk); kdo přibyl, dostane
siluetu a medailonek s poznámkou, že se připravuje.
"""
import json, re, unicodedata
from pathlib import Path

KOREN = Path(__file__).resolve().parent.parent
LISTINA = json.loads(Path('/tmp/claude-1000/-home-kamil-Sites-volbats/'
                          '35c9e59b-62b4-4894-ab47-0832cdddac03/scratchpad/listina.json')
                     .read_text(encoding='utf-8'))
STARI = json.loads((KOREN / 'src/data/kandidati.json').read_text(encoding='utf-8'))

TITULY = {'mgr','ing','bc','mudr','judr','phdr','arch','dis','ph','d','mba','csc','dr','rndr'}

def bez_titulu(jmeno):
    casti = [c.strip('.,') for c in jmeno.replace(',', ' ').split()]
    return [c for c in casti if c and c.lower() not in TITULY]

def klic(jmeno):
    return ' '.join(sorted(c.lower() for c in bez_titulu(jmeno)))

def slug(jmeno):
    text = ' '.join(bez_titulu(jmeno))
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()
    return re.sub(r'[^a-z0-9]+', '-', text.lower()).strip('-')

def popis_z_listiny(k):
    """Řádek pod fotkou poskládaný z údajů na kandidátní listině."""
    casti = [k['povolani'][0].lower() + k['povolani'][1:]]
    if k['cast'] != 'Trhové Sviny':
        casti.append(k['cast'])
    if k['strana'] != 'bez politické příslušnosti':
        casti.append(k['strana'])
    casti.append(f"{k['vek']} let")
    return ', '.join(casti)

stara_mapa = {klic(s['jmeno']): s for s in STARI}
novi = []
for k in LISTINA:
    stary = stara_mapa.get(klic(k['jmeno']))
    if stary:
        # Popisek pod fotkou zůstává, jen se srovná věk ke druhému dni voleb.
        info = re.sub(r'\b\d+ let\b', f"{k['vek']} let", stary['info'])
        novi.append({
            'cislo': k['cislo'],
            'jmeno': k['jmeno'],
            'slug': stary['slug'] or slug(k['jmeno']),
            'foto': stary['foto'],
            'povolani': k['povolani'],
            'cast': k['cast'],
            'strana': k['strana'],
            'vek': k['vek'],
            'info': info,
            'zivotopis': stary['zivotopis'],
        })
    else:
        novi.append({
            'cislo': k['cislo'],
            'jmeno': k['jmeno'],
            'slug': slug(k['jmeno']),
            'foto': 'obrazky/silueta.svg',
            'povolani': k['povolani'],
            'cast': k['cast'],
            'strana': k['strana'],
            'vek': k['vek'],
            'info': popis_z_listiny(k),
            'zivotopis': '',
        })

(KOREN / 'src/data/kandidati.json').write_text(
    json.dumps(novi, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

zustava = sum(1 for n in novi if n['foto'] != 'obrazky/silueta.svg')
print(f'{len(novi)} kandidátů — {zustava} s fotkou, {len(novi)-zustava} se siluetou')
print(f"s medailonkem: {sum(1 for n in novi if n['zivotopis'])}")
