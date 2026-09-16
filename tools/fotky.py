#!/usr/bin/env python3
"""Připraví fotky pro web.

Fotograf dodává snímky v tisícových rozměrech a několika megabajtech — takové
se na web dát nedají. Skript z každé udělá několik velikostí pro srcset, aby
si prohlížeč stáhl tu, kterou opravdu zobrazí.

    python3 tools/fotky.py <adresář s portréty>
    python3 tools/fotky.py --spolecna <soubor> [horní hrana] [spodní hrana]

Portréty se čekají pojmenované číslem kandidáta (1.jpg, 2.jpg, …) a výstup
jde do src/obrazky/ jako kandidat-<číslo>-<šířka>.webp. Společná fotka se
ukládá jako spolecna-<šířka>.webp; hrany ořezu se zadávají v pixelech
originálu, protože na úvodní stránce sedí v horní části fotky logo a dole
nemá zbýt zbytečný pás dlažby.
"""
import sys
from pathlib import Path
from PIL import Image, ImageOps

KOREN = Path(__file__).resolve().parent.parent
CIL = KOREN / 'src/obrazky'
SIRKY = (400, 800, 1200)
SIRKY_SPOLECNA = (800, 1400, 2000, 2600)
POMER = 3 / 4          # výška dlaždice na webu
KVALITA = 82

def uprav(zdroj: Path) -> list[str]:
    im = ImageOps.exif_transpose(Image.open(zdroj))   # srovná otočení z fotáku
    if im.mode != 'RGB':
        im = im.convert('RGB')

    # Ořez na poměr dlaždice se dělá tady, ne v prohlížeči: ubíráme zespodu,
    # aby portrétu zůstal prostor nad hlavou tak, jak ho fotograf naaranžoval.
    cilova_vyska = round(im.width / POMER)
    if cilova_vyska < im.height:
        im = im.crop((0, 0, im.width, cilova_vyska))

    vytvorene = []
    cislo = zdroj.stem
    for sirka in SIRKY:
        varianta = im.resize((sirka, round(sirka / POMER)), Image.LANCZOS)
        jmeno = f'kandidat-{cislo}-{sirka}.webp'
        # WebP kvůli poměru kvalita/velikost; EXIF se nepřenáší, takže
        # s fotkami neputují údaje o fotoaparátu ani poloze.
        varianta.save(CIL / jmeno, 'WEBP', quality=KVALITA, method=6)
        vytvorene.append(jmeno)
    return vytvorene

def uprav_spolecnou(zdroj: Path, nahore: int = 0, dole: int | None = None) -> list[str]:
    """Společná fotka se ořízne na zadané hrany a zmenší do srcsetu."""
    im = ImageOps.exif_transpose(Image.open(zdroj))
    if im.mode != 'RGB':
        im = im.convert('RGB')
    if nahore or dole:
        im = im.crop((0, nahore, im.width, min(dole or im.height, im.height)))

    vytvorene = []
    for sirka in SIRKY_SPOLECNA:
        jmeno = f'spolecna-{sirka}.webp'
        if sirka > im.width:
            # Na tuhle šířku předloha nestačí. Zvětšovat nemá smysl, ale
            # nechat tu ležet variantu z minulé předlohy taky ne — srcset by
            # míchal dvě různé fotky podle toho, jak široké má kdo okno.
            (CIL / jmeno).unlink(missing_ok=True)
            continue
        vyska = round(im.height * sirka / im.width)
        im.resize((sirka, vyska), Image.LANCZOS).save(
            CIL / jmeno, 'WEBP', quality=KVALITA, method=6)
        vytvorene.append(jmeno)
    return vytvorene


def main():
    if len(sys.argv) in (3, 4, 5) and sys.argv[1] == '--spolecna':
        zdroj = Path(sys.argv[2])
        nahore = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        dole = int(sys.argv[4]) if len(sys.argv) > 4 else None
        celkem = 0
        for jmeno in uprav_spolecnou(zdroj, nahore, dole):
            velikost = (CIL / jmeno).stat().st_size
            celkem += velikost
            print(f'{jmeno:24} {velikost // 1024:4} kB')
        print(f'\ncelkem {celkem / 1024:.0f} kB')
        return

    if len(sys.argv) != 2:
        sys.exit(__doc__)
    zdroje = sorted(Path(sys.argv[1]).glob('*.jpg'), key=lambda p: int(p.stem))
    celkem = 0
    for zdroj in zdroje:
        for jmeno in uprav(zdroj):
            celkem += (CIL / jmeno).stat().st_size
        print(f'{zdroj.name:8} -> kandidat-{zdroj.stem}-{{{",".join(map(str, SIRKY))}}}.webp')
    print(f'\n{len(zdroje)} kandidátů, {celkem / 1024 / 1024:.1f} MB celkem')

if __name__ == '__main__':
    main()
