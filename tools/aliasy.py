#!/usr/bin/env python3
"""Krátké adresy kandidat1.volbats.cz … kandidat10.volbats.cz.

Každá přesměruje na medailonek kandidáta s tím číslem na listině. Původní
adresy /kandidati/<slug>/ zůstávají, tohle je jen zkratka na tiskoviny.

GitHub Pages unese na jeden repozitář jen jednu vlastní doménu, takže každý
alias je samostatný malý repozitář steinbauer/kandidatN s CNAME a stránkou,
která hned přesměruje. HTTPS certifikát k doméně vystaví GitHub sám, jakmile
na něj míří DNS:

    kandidatN.volbats.cz.  CNAME  steinbauer.github.io.

    python3 tools/aliasy.py             # jen vygeneruje obsah do aliasy/
    GITHUB_TOKEN=… python3 tools/aliasy.py --nasadit

Nasazení je idempotentní: založí, co chybí, nahraje obsah a zapne Pages.
Vynucení HTTPS jde nastavit až po vydání certifikátu (pár minut po tom, co
začne platit DNS) — do té doby skript hlásí stav a stačí ho pustit znovu.

Token potřebuje u účtu steinbauer právo zakládat repozitáře a spravovat
Pages (classic `repo`, nebo fine-grained s Administration, Contents a Pages
na zápis).
"""
import base64
import html
import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

KOREN = Path(__file__).resolve().parent.parent
VYSTUP = KOREN / 'aliasy'
VLASTNIK = 'steinbauer'
WEB = 'https://volbats.cz'
POCET = 10

STRANKA = """<!doctype html>
<html lang="cs">
<head>
<meta charset="utf-8">
<title>{jmeno} — Volba pro město</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{cil}">
<meta http-equiv="refresh" content="0; url={cil}">
<script>location.replace({cil_js})</script>
</head>
<body>
<p><a href="{cil}">{jmeno}</a></p>
</body>
</html>
"""


def aliasy():
    kandidati = json.loads((KOREN / 'src/data/kandidati.json').read_text())
    for k in sorted(kandidati, key=lambda k: k['cislo'])[:POCET]:
        # Přesměrovat na stránku, která neexistuje, by bylo horší než nic.
        if not k.get('zivotopis'):
            sys.exit(f"{k['jmeno']} nemá medailonek, alias by vedl na 404")
        yield {
            'repo': f"kandidat{k['cislo']}",
            'domena': f"kandidat{k['cislo']}.volbats.cz",
            'jmeno': k['jmeno'],
            'cil': f"{WEB}/kandidati/{k['slug']}/",
        }


def vygeneruj(a):
    adresar = VYSTUP / a['repo']
    adresar.mkdir(parents=True, exist_ok=True)
    stranka = STRANKA.format(
        jmeno=html.escape(a['jmeno']),
        cil=html.escape(a['cil']),
        cil_js=json.dumps(a['cil']),
    )
    (adresar / 'index.html').write_text(stranka)
    # Cokoli jiného na subdoméně (překlep, stará cesta) skončí taky na kartě.
    (adresar / '404.html').write_text(stranka)
    (adresar / 'CNAME').write_text(a['domena'] + '\n')
    (adresar / '.nojekyll').write_text('')
    return adresar


def api(token, metoda, cesta, data=None):
    pozadavek = urllib.request.Request(
        'https://api.github.com' + cesta,
        method=metoda,
        data=json.dumps(data).encode() if data is not None else None,
        headers={
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json',
            'X-GitHub-Api-Version': '2022-11-28',
        },
    )
    try:
        with urllib.request.urlopen(pozadavek) as odpoved:
            telo = odpoved.read()
            return odpoved.status, json.loads(telo) if telo else None
    except urllib.error.HTTPError as chyba:
        telo = chyba.read()
        return chyba.code, json.loads(telo) if telo else None


def nahraj(token, a, adresar):
    """Obsah jako jediný commit, ať historie aliasu nebobtná."""
    hlavicka = base64.b64encode(f'x-access-token:{token}'.encode()).decode()
    # Token přes proměnné prostředí, ne v argumentech — ty vidí `ps`.
    prostredi = dict(
        os.environ,
        GIT_CONFIG_COUNT='1',
        GIT_CONFIG_KEY_0='http.extraHeader',
        GIT_CONFIG_VALUE_0=f'Authorization: Basic {hlavicka}',
        GIT_AUTHOR_NAME='volbats', GIT_AUTHOR_EMAIL='noreply@volbats.cz',
        GIT_COMMITTER_NAME='volbats', GIT_COMMITTER_EMAIL='noreply@volbats.cz',
    )
    with tempfile.TemporaryDirectory() as tmp:
        git = lambda *args: subprocess.run(
            ['git', '-C', tmp, *args], env=prostredi, check=True,
            stdout=subprocess.DEVNULL)
        git('init', '-q', '-b', 'main')
        git('--work-tree', str(adresar), 'add', '-A')
        git('commit', '-q', '-m', f"Přesměrování {a['domena']} na {a['cil']}")
        git('push', '-q', '--force',
            f"https://github.com/{VLASTNIK}/{a['repo']}.git", 'main')


def nasad(token, a, adresar):
    repo = f"/repos/{VLASTNIK}/{a['repo']}"

    stav, _ = api(token, 'GET', repo)
    if stav == 404:
        stav, odpoved = api(token, 'POST', '/user/repos', {
            'name': a['repo'],
            'description': f"Přesměrování {a['domena']} → {a['cil']}",
            'homepage': f"https://{a['domena']}/",
            'has_issues': False, 'has_projects': False, 'has_wiki': False,
        })
        if stav != 201:
            sys.exit(f"{a['repo']}: repozitář nejde založit ({stav}): {odpoved}")

    nahraj(token, a, adresar)

    stav, pages = api(token, 'GET', repo + '/pages')
    if stav == 404:
        stav, pages = api(token, 'POST', repo + '/pages',
                          {'source': {'branch': 'main', 'path': '/'}})
        if stav != 201:
            sys.exit(f"{a['repo']}: Pages nejdou zapnout ({stav}): {pages}")

    if pages.get('cname') != a['domena']:
        api(token, 'PUT', repo + '/pages', {'cname': a['domena']})

    _, pages = api(token, 'GET', repo + '/pages')
    certifikat = (pages.get('https_certificate') or {}).get('state')
    if pages.get('https_enforced'):
        return 'HTTPS vynucené'
    if certifikat == 'approved':
        stav, _ = api(token, 'PUT', repo + '/pages', {'https_enforced': True})
        return 'HTTPS vynucené' if stav == 204 else f'vynucení HTTPS selhalo ({stav})'
    return f'čeká na certifikát ({certifikat or "zatím nežádán — platí DNS?"})'


def main():
    nasadit = '--nasadit' in sys.argv[1:]
    token = os.environ.get('GITHUB_TOKEN')
    if nasadit and not token:
        sys.exit('Nasazení potřebuje GITHUB_TOKEN')

    for a in aliasy():
        adresar = vygeneruj(a)
        stav = nasad(token, a, adresar) if nasadit else 'vygenerováno'
        print(f"https://{a['domena']}/  →  {a['cil']}  [{stav}]")


if __name__ == '__main__':
    main()
