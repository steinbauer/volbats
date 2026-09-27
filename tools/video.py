#!/usr/bin/env python3
"""Složí video pro Facebook a Instagram z hlasu, obrázků a titulků.

    python3 tools/video.py              # video/seniori.mp4
    python3 tools/video.py --dily       # nechá i mezisoubory, když je co ladit

Hlas se bere z nahrávky tak, jak je; obraz vzniká celý tady — obrázky se
prolínají, přes ně jdou titulky a na konci je značka s volebním číslem
a termínem voleb.

Titulky odpovídají tomu, co je slyšet, a vypalují se přímo do obrazu: na
Facebooku se videa přehrávají bez zvuku a titulky, které si divák musí zapnout,
si nezapne skoro nikdo.

Textové vrstvy se sázejí v HTML a fotí přes browserless — stejnou cestou jako
karty a tiskoviny, takže písmo ani srdce nemůžou být na videu jiné než na
letáku. Nikde není tmavá plocha, viz pravidlo o barvách značky.

Scénář (co se kdy ukazuje a co se kdy říká) žije v src/data/video.json.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from socialni import PLOCHA, PRECHOD, TLUMENY, znak
from tiskoviny import BROWSERLESS, CERVENA, INKOUST, KOREN, fonty, nacti, nacti_web

VIDEO = KOREN / 'src/video'
# Verze pro web jde rovnou do public/, odkud ji Vite vezme do buildu.
WEB = KOREN / 'public/videa'
KRESBY = VIDEO / 'kresby'
HLASY = VIDEO / 'hlasy'
VYSTUP = KOREN / 'video'

# Koncová značka doběhne po hlase; tolik vteřin má na obrazovce vydržet.
KONCOVKA = 4.4

# De-esser pro nahrávky s ostrými sykavkami. Signál se rozdělí na nízké
# a vysoké pásmo, komprimuje se jen to vysoké a pak se obě zase sečtou —
# sykavka se tím stáhne jen ve chvíli, kdy zazní, a hlas nezmatní tak,
# jako když se výšky stáhnou natrvalo. Zesílení na konci dorovnává hlasitost,
# kterou komprese ubrala.
DEESSER = ('asplit=2[nizke][vysoke];'
           '[nizke]lowpass=f=6000[n];'
           '[vysoke]highpass=f=6000,'
           'acompressor=threshold=0.02:ratio=8:attack=1:release=40[v];'
           '[n][v]amix=inputs=2:normalize=0,volume=4.5dB')

# 4:5 je tentýž poměr jako karty — největší plocha, kterou Instagram i Facebook
# pustí do nástěnky. Výš než 1080 px se nešplhá: předlohy mají necelý tisíc
# pixelů na šířku a větší formát by z nich udělal jen měkčí obraz.
SIRKA, VYSKA = 1080, 1350
FPS = 30

# Obrázky jsou na šířku, plátno na výšku, takže se nic neořezává — obraz dostane
# pruh uprostřed. Ořez by u těch kreseb znamenal uříznout dům nebo půlku stolu.
# Nad obrazem drží značka, pod ním je místo na titulek; prázdná krémová plocha
# je tím rozdělená symetricky a vypadá jako záměr, ne jako zbytek.
POLE_Y, POLE_V = 215, 800
TITULEK_Y = 1075

PLOCHA_BARVA = '#fdf2e6'   # střed krémového přechodu, na plochu kolem obrazu

# Titulky se v datech dotýkají koncem a začátkem, protože tak plyne řeč. Na
# plátně by ale v tom okamžiku byly obě vrstvy naráz a text by se na snímku
# přetiskl — každý se proto o tohle zkrátí z obou stran a mezi nápisy vznikne
# dvoudesetinová pauza.
MEZERA = 0.1


# --- textové vrstvy ----------------------------------------------------------

def _stranka(vnitrek: str, styl: str) -> str:
    return f"""<!doctype html><html lang="cs"><head><meta charset="utf-8"><style>
{fonty()}
* {{ box-sizing: border-box; }}
html, body {{ margin: 0; padding: 0; }}
body {{
  width: {SIRKA}px; height: {VYSKA}px;
  font-family: 'IBM Plex Sans', sans-serif;
  color: {INKOUST};
  -webkit-font-smoothing: antialiased;
}}
{styl}
</style></head><body>{vnitrek}</body></html>"""


def hlavicka_html(web: dict) -> str:
    """Značka nad obrazem, stejná po celé video.

    Kdo video nedokouká — a to je na nástěnce většina — musí i tak vidět, kdo
    mluví a s jakým číslem.
    """
    styl = f"""
body {{ background: transparent; }}
.hlavicka {{
  display: flex; align-items: center; gap: 18px;
  padding: 52px 56px 0;
}}
.nazev {{
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 36px; line-height: 1.05; letter-spacing: -0.02em;
}}
.mesto {{ color: #9a7411; }}
.web {{
  margin-left: auto; font-size: 29px; font-weight: 600; color: {CERVENA};
}}
.znak-cislo {{
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 430px; fill: {INKOUST};
}}"""
    vnitrek = f"""<div class="hlavicka">
  {znak(92, web['cislo'], 'hlava')}
  <div class="nazev">{web['nazev']}<br><span class="mesto">{web['mesto']}</span></div>
  <div class="web">volbats.cz</div>
</div>"""
    return _stranka(vnitrek, styl)


def titulek_html(text: str) -> str:
    """Titulek pod obrazem. Na krémové ploše, ne na tmavém pásu."""
    styl = f"""
body {{ background: transparent; position: relative; }}
.pas {{
  position: absolute;
  left: 0; right: 0;
  top: {TITULEK_Y}px;
  padding: 0 72px;
  display: flex; align-items: flex-start; justify-content: center;
}}
.text {{
  font-size: 44px;
  font-weight: 600;
  line-height: 1.34;
  text-align: center;
  max-width: 19em;
  margin: 0;
}}"""
    return _stranka(f'<div class="pas"><p class="text">{text}</p></div>', styl)


def uvod_html(web: dict, podtitul: str) -> str:
    """První záběr: značka a téma, ještě než začne mluvit hlas."""
    styl = f"""
body {{
  background: {PLOCHA};
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  /* Pod kartou běží titulky, tak se obsah drží nad jejich pásem. */
  padding-bottom: {VYSKA - TITULEK_Y + 40}px;
}}
.nazev {{
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; letter-spacing: -0.025em; line-height: 1.04;
  font-size: 76px; text-align: center;
  margin-top: 40px;
}}
.mesto {{ color: #9a7411; }}
.tema {{
  margin-top: 40px;
  padding-top: 32px;
  border-top: 5px solid transparent;
  border-image: {PRECHOD} 1;
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; letter-spacing: -0.02em;
  font-size: 54px; color: {CERVENA}; text-align: center;
  max-width: 15em;
}}
.znak-cislo {{
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 430px; fill: {INKOUST};
}}"""
    vnitrek = f"""
  {znak(280, web['cislo'], 'uvod')}
  <div class="nazev">{web['nazev']}<br><span class="mesto">{web['mesto']}</span></div>
  <div class="tema">{podtitul}</div>"""
    return _stranka(vnitrek, styl)


def koncovka_html(web: dict) -> str:
    """Poslední záběr: značka, volební číslo a pod tím drobně termín voleb."""
    styl = f"""
body {{
  background: {PLOCHA};
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
}}
.nazev {{
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; letter-spacing: -0.025em; line-height: 1.04;
  font-size: 86px; text-align: center;
  margin-top: 46px;
}}
.mesto {{ color: #9a7411; }}
.termin {{
  margin-top: 38px;
  padding-top: 30px;
  border-top: 5px solid transparent;
  border-image: {PRECHOD} 1;
  font-size: 34px;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: {CERVENA};
}}
.web {{
  margin-top: 16px;
  font-size: 28px;
  color: {TLUMENY};
  letter-spacing: 0.04em;
}}
.znak-cislo {{
  font-family: 'Bricolage Grotesque', sans-serif;
  font-weight: 800; font-size: 430px; fill: {INKOUST};
}}"""
    vnitrek = f"""
  {znak(300, web['cislo'], 'konec')}
  <div class="nazev">{web['nazev']}<br><span class="mesto">{web['mesto']}</span></div>
  <div class="termin">volby {web['termin']}</div>
  <div class="web">volbats.cz</div>"""
    return _stranka(vnitrek, styl)


def vyfot(html: str, cil: Path, pruhledne: bool) -> None:
    cil.parent.mkdir(parents=True, exist_ok=True)
    telo = {'html': html,
            'options': {'type': 'png', 'fullPage': False, 'omitBackground': pruhledne},
            'viewport': {'width': SIRKA, 'height': VYSKA, 'deviceScaleFactor': 1}}
    odpoved = subprocess.run(
        ['curl', '-sS', '-m', '120', '-X', 'POST', BROWSERLESS + '/screenshot',
         '-H', 'Content-Type: application/json', '--data-binary', '@-',
         '-o', str(cil), '-w', '%{http_code}'],
        input=json.dumps(telo), text=True, capture_output=True)
    if odpoved.stdout.strip() != '200':
        sys.exit(f'browserless vrátil {odpoved.stdout} u {cil.name}: {odpoved.stderr[:300]}')


# --- obraz -------------------------------------------------------------------

def najdi_obraz(jmeno: str) -> Path:
    if (VIDEO / jmeno).is_file():
        return VIDEO / jmeno
    for nalez in sorted(VIDEO.glob(f'*/{jmeno}')):
        return nalez
    sys.exit(f'chybí obrázek {jmeno}')


def nacti_scenar(tema: str) -> dict:
    """Scénář k tématu — buď hotové časování od hlasu, nebo ruční z video.json.

    tools/hlas.py při mluvení rovnou spočítá, kdy která věta začíná, takže
    scénář videa z toho vypadne sám. Ruční varianta zůstává pro první video,
    kde hlas přišel hotový zvenčí.
    """
    casovani = HLASY / f'{tema}.json'
    if casovani.is_file():
        scenar = json.loads(casovani.read_text(encoding='utf-8'))
        scenar.setdefault('prechod', 0.6)
        for z in scenar['zabery']:
            z.setdefault('pohyb', 'zoom')
            z.setdefault('vypln', 'cover')
        scenar['zabery'].append({'koncovka': True,
                                 'do': round(scenar['delka'] + KONCOVKA, 3)})
        return scenar
    return nacti('video.json')[tema]


def rozmer(cesta: Path) -> tuple[int, int]:
    out = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
         '-show_entries', 'stream=width,height', '-of', 'csv=p=0:s=x', str(cesta)],
        check=True, capture_output=True, text=True).stdout.strip()
    s, v = out.split('x')[:2]
    return int(s), int(v)


def splynout(zdroj: Path, cil: Path) -> Path:
    """Smíchá bílé pozadí předlohy s krémovou plochou videa.

    Logo přišlo jako JPEG na bílé, takže by na krémové ploše leželo na bílém
    čtverci. Prahovat bílou na průhlednou nejde — JPEG má kolem hran artefakty
    a po prahu by kresba dostala špinavý lem. Násobení podkladem bílou srovná
    s plochou a barev se skoro nedotkne.
    """
    from PIL import Image, ImageChops
    obraz = Image.open(zdroj).convert('RGB')
    podklad = Image.new('RGB', obraz.size, PLOCHA_BARVA)
    ImageChops.multiply(obraz, podklad).save(cil)
    return cil


def _usazeni_pole(vypln: str | None) -> str:
    """Jak se obraz posadí do pruhu uprostřed plátna.

    `pole` ho roztáhne přes celý pruh a přebytek ořízne — všechny záběry pak
    mají tentýž tvar a obraz mezi nimi neskáče. Jinak se vejde celý a kolem
    zůstane krémová plocha.
    """
    if vypln == 'pole':
        return (f'scale={SIRKA}:{POLE_V}:force_original_aspect_ratio=increase:flags=lanczos,'
                f'crop={SIRKA}:{POLE_V},'
                f'pad={SIRKA}:{VYSKA}:0:{POLE_Y}:color={PLOCHA_BARVA}')
    return (f'scale={SIRKA}:{POLE_V}:force_original_aspect_ratio=decrease:flags=lanczos,'
            f'pad={SIRKA}:{VYSKA}:(ow-iw)/2:{POLE_Y}+({POLE_V}-ih)/2:color={PLOCHA_BARVA}')


def klip(zaber: dict, delka: float, cil: Path, karta: Path, prechod: float = 0) -> None:
    """Jeden záběr jako kousek videa.

    Pohyb je pomalý zoom, nic víc: obrázků je pár na půl minuty, takže každý
    střih je vidět sám o sobě a nemusí se podtrhávat efektem. Záběrem může být
    i kus hotového videa — pak se jen usadí do plátna a nechá běžet.
    """
    if zaber.get('video'):
        zdroj = najdi_obraz(zaber['video'])
        # Předloha mívá kolem obrazu černé pruhy, protože se do ní vkládaly
        # fotky různých tvarů. Na krémové ploše by z nich byla ta tmavá zóna,
        # kterou značka nemá mít, tak se ořežou pryč — každý záběr zvlášť,
        # protože každý je má jinde.
        orez = f"crop={zaber['orez']}," if zaber.get('orez') else ''
        # Klip končí přesně tam, kde v předloze končí jeho střih, a poslední
        # snímek se pak podrží po dobu prolnutí. Kdyby si bral rovnou i ten
        # překryv, sáhl by do dalšího záběru předlohy — a ten má jiný ořez,
        # takže by obraz na dvě desetiny vteřiny poskočil do jiného výřezu.
        vlastni = max(delka - prechod, 0.1)
        drzet = (f',tpad=stop_mode=clone:stop_duration={prechod:.3f}'
                 if prechod else '')
        usazeni = orez + _usazeni_pole(zaber.get('vypln'))
        subprocess.run(
            ['ffmpeg', '-v', 'error', '-y', '-ss', str(zaber.get('od_videa', 0)),
             '-t', f'{vlastni:.3f}', '-i', str(zdroj),
             '-an', '-vf', usazeni + f',fps={FPS}{drzet},setsar=1,format=yuv420p',
             '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', str(cil)],
            check=True, capture_output=True)
        return

    if zaber.get('koncovka') or zaber.get('uvod'):
        # Úvodní i koncová karta jsou hotová plátna v plné velikosti.
        filtr = f'scale={SIRKA}:{VYSKA}'
        zdroj = karta
    else:
        zdroj = najdi_obraz(zaber['obraz'])
        if zaber.get('podklad') == 'splynout':
            zdroj = splynout(zdroj, cil.with_name(cil.stem + '-podklad.png'))
        s, v = rozmer(zdroj)
        if zaber.get('vypln') == 'pole':
            # Všechny záběry vyplní tentýž obdélník, i za cenu ořezu — jinak
            # obraz mezi záběry skáče podle toho, jestli je předloha na šířku,
            # na výšku nebo čtvercová.
            os, ov = SIRKA, POLE_V
        else:
            # Obraz se vejde do pruhu celý, ať má jakýkoli tvar.
            mer = min(SIRKA / s, POLE_V / v)
            os, ov = int(s * mer) // 2 * 2, int(v * mer) // 2 * 2

        vyrez = zaber.get('vyrez', 'střed')
        if zaber.get('vypln') == 'pole':
            posun = {'nahoru': '0', 'dolů': '(ih-oh)'}.get(vyrez, '(ih-oh)/2')
            do_pole = (f'scale={os}:{ov}:force_original_aspect_ratio=increase:flags=lanczos,'
                       f'crop={os}:{ov}:(iw-ow)/2:{posun},')
        else:
            do_pole = ''

        if zaber.get('pohyb') == 'klid':
            filtr = do_pole + f'scale={os}:{ov}:flags=lanczos'
        elif do_pole:
            krok = 0.12 / (delka * FPS)
            filtr = (do_pole + f'scale={os * 2}:{ov * 2}:flags=lanczos,'
                     f"zoompan=z='min(1+{krok:.6f}*on,1.12)':d=1"
                     f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                     f':s={os}x{ov}:fps={FPS}')
        else:
            # 12 % za celý záběr: pohyb se pozná, ale nestrhává pozornost.
            krok = 0.12 / (delka * FPS)
            filtr = (f'scale={os * 2}:{ov * 2}:flags=lanczos,'
                     f"zoompan=z='min(1+{krok:.6f}*on,1.12)':d=1"
                     f":x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
                     f':s={os}x{ov}:fps={FPS}')

        filtr += (f',pad={SIRKA}:{VYSKA}:(ow-iw)/2:'
                  f'{POLE_Y}+({POLE_V}-ih)/2:color={PLOCHA_BARVA}')

    subprocess.run(
        ['ffmpeg', '-v', 'error', '-y', '-loop', '1', '-framerate', str(FPS),
         '-t', f'{delka:.3f}', '-i', str(zdroj),
         '-vf', filtr + ',setsar=1,format=yuv420p',
         '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', str(cil)],
        check=True, capture_output=True)


def sestav(scenar: dict, web: dict, prac: Path, jmeno: str) -> Path:
    prechod = scenar.get('prechod', 0.6)
    prac.mkdir(parents=True, exist_ok=True)

    konec_png = prac / 'koncovka.png'
    vyfot(koncovka_html(web), konec_png, False)

    uvod_png = None
    for z in scenar['zabery']:
        if z.get('uvod'):
            uvod_png = prac / 'uvod.png'
            vyfot(uvod_html(web, z.get('podtitul', scenar['nazev'])), uvod_png, False)

    hlavicka_png = prac / 'hlavicka.png'
    vyfot(hlavicka_html(web), hlavicka_png, True)

    titulky = []
    for i, t in enumerate(scenar['titulky']):
        cil = prac / f'titulek-{i:02d}.png'
        vyfot(titulek_html(t['text']), cil, True)
        titulky.append(cil)

    # Každý záběr je delší o překryv, aby bylo co prolnout.
    klipy, zacatek = [], 0.0
    for i, z in enumerate(scenar['zabery']):
        posledni = i == len(scenar['zabery']) - 1
        delka = z['do'] - zacatek + (0 if posledni else prechod)
        cil = prac / f'zaber-{i:02d}.mp4'
        klip(z, delka, cil, uvod_png if z.get('uvod') else konec_png,
             0 if posledni else prechod)
        klipy.append(cil)
        zacatek = z['do']

    vstupy = []
    for cesta in klipy + titulky + [hlavicka_png]:
        vstupy += ['-i', str(cesta)]
    vstupy += ['-i', str(VIDEO / scenar['zvuk'])]

    filtr, predchozi = [], '[0:v]'
    for i in range(1, len(klipy)):
        offset = scenar['zabery'][i - 1]['do'] - prechod
        filtr.append(f'{predchozi}[{i}:v]xfade=transition=fade:'
                     f'duration={prechod}:offset={offset:.3f}[x{i}]')
        predchozi = f'[x{i}]'

    od_listy = scenar['zabery'][0]['do'] if scenar['zabery'][0].get('uvod') else 0
    do_listy = scenar['zabery'][-2]['do']
    filtr.append(f"{predchozi}[{len(klipy) + len(titulky)}:v]overlay=0:0:"
                 f"enable='between(t,{od_listy},{do_listy})'[h]")
    predchozi = '[h]'

    for i, t in enumerate(scenar['titulky']):
        od, do = t['od'] + MEZERA, t['do'] - MEZERA
        filtr.append(f"{predchozi}[{len(klipy) + i}:v]overlay=0:0:"
                     f"enable='between(t,{od:.2f},{do:.2f})'[t{i}]")
        predchozi = f'[t{i}]'

    # Nahrávka začíná až za úvodní kartou a na konci se nechá doznít.
    stopa = len(klipy) + len(titulky) + 1
    zvuk = []
    if scenar.get('deesser'):
        zvuk.append(DEESSER)
    posun = scenar.get('zvuk_posun', 0)
    if posun:
        zvuk.append(f'adelay={int(posun * 1000)}:all=1')
    if scenar.get('zvuk_utlum'):
        od, trvani = scenar['zvuk_utlum']
        zvuk.append(f'afade=t=out:st={od + posun}:d={trvani}')
    if zvuk:
        retez = zvuk[0]
        for dalsi in zvuk[1:]:
            retez += (';' if '[' in dalsi else ',') + dalsi
        filtr.append(f'[{stopa}:a]' + retez + '[zvuk]')
        mapa_zvuku = '[zvuk]'
    else:
        mapa_zvuku = f'{stopa}:a'

    cil = VYSTUP / f'{jmeno}.mp4'
    cil.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ['ffmpeg', '-v', 'error', '-y', *vstupy,
         '-filter_complex', ';'.join(filtr),
         '-map', predchozi, '-map', mapa_zvuku,
         '-t', f"{scenar['zabery'][-1]['do']:.3f}",
         '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p',
         '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart',
         str(cil)], check=True, capture_output=True)
    return cil


def pro_web(scenar: dict, web_data: dict, hotove: Path, jmeno: str, prac: Path) -> None:
    """Zmenšená kopie do public/ a k ní náhledový obrázek.

    Na webu se video přehrává na pár set pixelech, takže plné rozlišení by
    jen natahovalo stahování. Náhled je první kreslený záběr bez titulku —
    tentýž obraz, jaký uvidí návštěvník po spuštění, takže při kliknutí nic
    nepřeskočí.
    """
    WEB.mkdir(parents=True, exist_ok=True)
    cil = WEB / f'{jmeno}.mp4'
    subprocess.run(
        ['ffmpeg', '-v', 'error', '-y', '-i', str(hotove),
         '-vf', f'scale={SIRKA // 2}:-2:flags=lanczos',
         '-c:v', 'libx264', '-preset', 'slow', '-crf', '28', '-pix_fmt', 'yuv420p',
         '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', str(cil)],
        check=True, capture_output=True)

    # Náhled: buď obrázek určený scénářem, nebo první kreslený záběr.
    jmeno_obrazu = scenar.get('poster') or next(
        (z['obraz'] for z in scenar['zabery'] if z.get('obraz')), None)
    if not jmeno_obrazu:
        return
    nahled = prac / 'poster.mp4'
    klip({'obraz': jmeno_obrazu, 'pohyb': 'klid', 'vypln': 'pole'}, 0.2, nahled,
         prac / 'koncovka.png')
    hlavicka_png = prac / 'hlavicka.png'
    subprocess.run(
        ['ffmpeg', '-v', 'error', '-y', '-i', str(nahled), '-i', str(hlavicka_png),
         '-filter_complex', f'[0:v][1:v]overlay=0:0,scale={SIRKA // 2}:-2',
         '-frames:v', '1', '-q:v', '4', str(WEB / f'{jmeno}.jpg')],
        check=True, capture_output=True)


def main() -> None:
    p = argparse.ArgumentParser(description='Video pro Facebook a Instagram')
    p.add_argument('scenar', nargs='*', default=['seniori'],
                   help='která témata; bez uvedení jen seniori')
    p.add_argument('--dily', action='store_true', help='nechat mezisoubory')
    p.add_argument('--web', action='store_true',
                   help='navíc zmenšenou kopii a náhled do public/videa/')
    args = p.parse_args()

    web = nacti_web()

    for tema in args.scenar:
        scenar = nacti_scenar(tema)
        prac = VYSTUP / 'dily' / tema
        cil = sestav(scenar, web, prac, tema)
        if args.web:
            pro_web(scenar, web, cil, tema, prac)
        if not args.dily:
            shutil.rmtree(prac, ignore_errors=True)

        delka = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'csv=p=0', str(cil)], check=True, capture_output=True,
            text=True).stdout.strip()
        print(f'  {cil.relative_to(KOREN)}  {SIRKA} × {VYSKA}  '
              f'{float(delka):.1f} s  {cil.stat().st_size / 1024 / 1024:.1f} MB')


if __name__ == '__main__':
    main()
