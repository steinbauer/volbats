#!/usr/bin/env python3
"""Namluví scénáře videí a uloží k nim přesné časování titulků.

    export POLY_ELEVENLABS_API_KEY=...        # nebo POLY_OPENAI_API_KEY
    python3 tools/hlas.py                     # co ještě nemá hlas
    python3 tools/hlas.py doprava --znovu     # jedno téma znovu
    python3 tools/hlas.py --sluzba openai     # druhá služba

Každá věta se namluví zvlášť a teprve pak se nahrávky slepí s krátkou pauzou.
Zní to o něco kouskovaněji než jeden dlouhý blok, ale u výčtu programových bodů
to sedí — a hlavně je pak přesně známo, kdy která věta začíná, takže titulky
nemůžou utéct řeči. Odhadovat časování z počtu písmen se rozejde už po pár
větách.

Klíč se bere z prostředí, ne ze souboru v repu: tenhle repozitář je veřejný.

Výstup jde do src/video/hlasy/ — mp3 a vedle něj JSON s časy. Nahrávky se
verzují, aby šlo video složit znovu bez dalšího placeného volání.
"""
import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from tiskoviny import KOREN, nacti

HLASY = KOREN / 'src/video/hlasy'

# Pauza mezi větami. Kratší zní uspěchaně, delší jako by hlas ztratil nit.
PAUZA = 0.38

# Nad tuhle délku se věta na kartu nevejde a láme se na dva titulky.
DELKA_TITULKU = 76

SLUZBY = {
    # Český hlas, přednes bez cizího přízvuku. Vyžaduje uhrazené předplatné.
    'elevenlabs': {
        'url': 'https://api.elevenlabs.io/v1/text-to-speech/{hlas}?output_format=mp3_44100_128',
        'model': 'eleven_multilingual_v2',
    },
    # Záloha: hlasy jsou anglické a české koncovky občas ulítnou, ale
    # `coral` s výslovnostní instrukcí je z nabídky nejsrozumitelnější.
    'openai': {
        'url': 'https://api.openai.com/v1/audio/speech',
        'model': 'gpt-4o-mini-tts',
        'instrukce': ('Mluv plynulou spisovnou češtinou rodilé mluvčí. Klidné, '
                      'vlídné a důvěryhodné tempo jako zkušená učitelka. Vyslovuj '
                      'pečlivě české koncovky a diakritiku: ě, š, č, ř, ž, ů. '
                      'Žádný cizí přízvuk.'),
    },
}


def klic(sluzba: str) -> str:
    jmeno = ('POLY_ELEVENLABS_API_KEY' if sluzba == 'elevenlabs'
             else 'POLY_OPENAI_API_KEY')
    k = os.environ.get(jmeno, '').strip()
    if not k:
        sys.exit(f'chybí {jmeno} v prostředí')
    return k


def namluv_vetu(text: str, hlas: str, sluzba: str, cil: Path) -> None:
    nastaveni = SLUZBY[sluzba]
    if sluzba == 'elevenlabs':
        telo = {'text': text, 'model_id': nastaveni['model'],
                'voice_settings': {'stability': 0.55, 'similarity_boost': 0.8,
                                   'style': 0.0, 'use_speaker_boost': True}}
        hlavicky = ['-H', f'xi-api-key: {klic(sluzba)}']
        url = nastaveni['url'].format(hlas=hlas)
    else:
        telo = {'model': nastaveni['model'], 'input': text, 'voice': hlas,
                'response_format': 'mp3', 'instructions': nastaveni['instrukce']}
        hlavicky = ['-H', f'Authorization: Bearer {klic(sluzba)}']
        url = nastaveni['url']

    odpoved = subprocess.run(
        ['curl', '-sS', '-m', '300', '-X', 'POST', url, *hlavicky,
         '-H', 'Content-Type: application/json', '--data-binary', '@-',
         '-o', str(cil), '-w', '%{http_code}'],
        input=json.dumps(telo, ensure_ascii=False), text=True, capture_output=True)
    if odpoved.stdout.strip() != '200':
        chyba = cil.read_text(encoding='utf-8', errors='replace')[:300] if cil.is_file() else ''
        sys.exit(f'hlasová služba vrátila {odpoved.stdout}: {chyba}')


def delka(cesta: Path) -> float:
    return float(subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'csv=p=0', str(cesta)], check=True, capture_output=True,
        text=True).stdout.strip())


def slep(kusy: list[Path], cil: Path) -> None:
    """Slepí věty s pauzou mezi nimi. Překóduje se, ať sedí délky na snímek."""
    vstupy, filtr = [], []
    for i, k in enumerate(kusy):
        vstupy += ['-i', str(k)]
        filtr.append(f'[{i}:a]apad=pad_dur={PAUZA}[a{i}]' if i < len(kusy) - 1
                     else f'[{i}:a]anull[a{i}]')
    retez = ''.join(f'[a{i}]' for i in range(len(kusy)))
    filtr.append(f'{retez}concat=n={len(kusy)}:v=0:a=1[out]')
    subprocess.run(
        ['ffmpeg', '-v', 'error', '-y', *vstupy,
         '-filter_complex', ';'.join(filtr), '-map', '[out]',
         '-c:a', 'libmp3lame', '-b:a', '160k', '-ar', '44100', str(cil)],
        check=True, capture_output=True)


def _rozdel(veta: str) -> list[str]:
    """Dlouhou větu rozlomí na dva titulky, nejlíp v přirozené pauze."""
    if len(veta) <= DELKA_TITULKU:
        return [veta]
    stred = len(veta) // 2
    nejlepsi, nejblize = None, len(veta)
    for znak in (' — ', ', ', ' a ', ' i '):
        misto = veta.find(znak)
        while misto != -1:
            # Čárka zůstane na konci prvního dílu, spojka na začátku druhého.
            rez = misto + len(znak) if znak in (' — ', ', ') else misto + 1
            if abs(rez - stred) < nejblize and 12 < rez < len(veta) - 12:
                nejlepsi, nejblize = rez, abs(rez - stred)
            misto = veta.find(znak, misto + 1)
    if nejlepsi is None:
        nejlepsi = (veta.rfind(' ', 0, stred + 14) + 1) or stred
    return [veta[:nejlepsi].strip(), veta[nejlepsi:].strip()]


def zpracuj(tema: str, scenar: dict, hlas: str, sluzba: str, znovu: bool) -> None:
    zvuk = HLASY / f'{tema}.mp3'
    casovani = HLASY / f'{tema}.json'
    if zvuk.is_file() and casovani.is_file() and not znovu:
        print(f'  {tema}: hotovo, přeskakuji')
        return

    HLASY.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        kusy, delky = [], []
        for i, v in enumerate(scenar['vety']):
            kus = Path(tmp) / f'{i:02d}.mp3'
            namluv_vetu(v['text'], hlas, sluzba, kus)
            kusy.append(kus)
            delky.append(delka(kus))
        slep(kusy, zvuk)

    # Časy vět plynou z délek jednotlivých nahrávek a pauz mezi nimi.
    titulky, zabery, cas = [], [], 0.0
    for v, d in zip(scenar['vety'], delky):
        od_v, do_v = cas, cas + d
        dily = _rozdel(v['text'])
        znaku = sum(len(x) for x in dily)
        zacatek = od_v
        for dil in dily:
            podil = d * len(dil) / znaku
            titulky.append({'od': round(zacatek, 3),
                            'do': round(zacatek + podil, 3), 'text': dil})
            zacatek += podil
        if zabery and zabery[-1]['obraz'] == v['obraz']:
            zabery[-1]['do'] = round(do_v, 3)
        else:
            zabery.append({'obraz': v['obraz'], 'do': round(do_v, 3)})
        cas = do_v + PAUZA

    cela = delka(zvuk)
    titulky[-1]['do'] = round(max(titulky[-1]['do'], cela - 0.15), 3)
    zabery[-1]['do'] = round(cela, 3)

    casovani.write_text(json.dumps(
        {'nazev': scenar['nazev'], 'zvuk': f'hlasy/{tema}.mp3', 'sluzba': sluzba,
         'hlas': hlas, 'delka': round(cela, 3),
         'zabery': zabery, 'titulky': titulky},
        ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'  {tema}: {cela:5.1f} s · {len(titulky)} titulků · {len(zabery)} záběrů')


def main() -> None:
    p = argparse.ArgumentParser(description='Namluví scénáře videí')
    p.add_argument('tema', nargs='*', help='která témata; bez uvedení všechna')
    p.add_argument('--sluzba', default='elevenlabs', choices=list(SLUZBY))
    p.add_argument('--hlas', help='jiný hlas než ze scénáře')
    p.add_argument('--znovu', action='store_true', help='přemluvit i hotová')
    args = p.parse_args()

    scenare = nacti('video-temata.json')
    hlas = args.hlas or scenare['hlas' if args.sluzba == 'elevenlabs' else 'hlas_openai']
    temata = args.tema or list(scenare['temata'])

    for tema in temata:
        if tema not in scenare['temata']:
            sys.exit(f'{tema} není ve scénářích')
        zpracuj(tema, scenare['temata'][tema], hlas, args.sluzba, args.znovu)


if __name__ == '__main__':
    main()
