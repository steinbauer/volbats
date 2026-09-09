#!/usr/bin/env python3
"""Připraví fotky kandidátů pro web.

Fotograf dodává svislé portréty kolem 3300×5000 px a několika megabajtů —
takové se na web dát nedají. Skript z každé udělá tři velikosti pro srcset,
aby si prohlížeč stáhl tu, kterou opravdu zobrazí.

    python3 tools/fotky.py <adresář se zdroji>

Zdroje se čekají pojmenované číslem kandidáta (1.jpg, 2.jpg, …), výstup
jde do src/obrazky/ jako kandidat-<číslo>-<šířka>.webp.
"""
import sys
from pathlib import Path
from PIL import Image, ImageOps

KOREN = Path(__file__).resolve().parent.parent
CIL = KOREN / 'src/obrazky'
SIRKY = (400, 800, 1200)
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

def main():
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
