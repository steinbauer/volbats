#!/usr/bin/env python3
"""Připraví fotky pro web.

Fotograf dodává snímky v tisícových rozměrech a několika megabajtech — takové
se na web dát nedají. Skript z každé udělá několik velikostí pro srcset, aby
si prohlížeč stáhl tu, kterou opravdu zobrazí.

    python3 tools/fotky.py <adresář s portréty>
    python3 tools/fotky.py --spolecna <soubor>

Portréty se čekají pojmenované číslem kandidáta (1.jpg, 2.jpg, …) a výstup
jde do src/obrazky/ jako kandidat-<číslo>-<šířka>.webp. Společná fotka se
neořezává — ukazuje se celá — a ukládá se jako spolecna-<šířka>.webp.
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

def uprav_spolecnou(zdroj: Path) -> list[str]:
    """Společná fotka se neořezává, jen zmenšuje — má být vidět celá."""
    im = ImageOps.exif_transpose(Image.open(zdroj))
    if im.mode != 'RGB':
        im = im.convert('RGB')

    vytvorene = []
    for sirka in SIRKY_SPOLECNA:
        if sirka > im.width:
            continue
        vyska = round(im.height * sirka / im.width)
        jmeno = f'spolecna-{sirka}.webp'
        im.resize((sirka, vyska), Image.LANCZOS).save(
            CIL / jmeno, 'WEBP', quality=KVALITA, method=6)
        vytvorene.append(jmeno)
    return vytvorene


def main():
    if len(sys.argv) == 3 and sys.argv[1] == '--spolecna':
        zdroj = Path(sys.argv[2])
        celkem = 0
        for jmeno in uprav_spolecnou(zdroj):
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
