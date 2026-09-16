#!/usr/bin/env python3
"""Vyrobí ikony sekcí programu do src/data/ikony.json.

Ikony jsou kreslené stejnou logikou jako srdce z loga: tah proměnlivé
šířky, který doběhne do špičky. Nekreslí se proto jako obrysy, ale jako
osa tahu (`body`) a profil šířky (`sila`); zbytek dopočítá `tah()`.

Výstup je jeden `d` na tah, v soustavě 100 × 100. Čte ho web
(src/components/IkonaSekce.jsx) i generátory tiskovin, takže kresba je
na webu, na letáku i na plakátu stejná.

    python3 tools/ikony.py
"""
import json
import math
from pathlib import Path

KOREN = Path(__file__).resolve().parent.parent
CIL = KOREN / 'src/data/ikony.json'


def catmull(body, uzavreno, kroku=8):
    """Proloží zadanými body hladkou křivku a vzorkuje ji."""
    n = len(body)
    if uzavreno:
        idx = lambda i: body[i % n]
        useky = range(n)
    else:
        idx = lambda i: body[min(max(i, 0), n - 1)]
        useky = range(n - 1)

    ven = []
    for i in useky:
        p0, p1, p2, p3 = idx(i - 1), idx(i), idx(i + 1), idx(i + 2)
        for k in range(kroku):
            t = k / kroku
            t2, t3 = t * t, t * t * t
            ven.append((
                0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t
                       + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2
                       + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3),
                0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t
                       + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2
                       + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3),
                i + t,
            ))
    if not uzavreno:
        ven.append((body[-1][0], body[-1][1], n - 1.0))
    return ven


def sirka_v(sila, u, useku):
    """Šířka tahu v parametru `u` (0 … počet úseků) lineární interpolací."""
    mist = len(sila) - 1
    x = u / useku * mist
    i = min(int(x), mist - 1)
    t = x - i
    return sila[i] * (1 - t) + sila[i + 1] * t


def tah(body, sila, uzavreno=False):
    """Z osy tahu a profilu šířky udělá obrys."""
    vzorky = catmull(body, uzavreno)
    useku = len(body) if uzavreno else len(body) - 1

    levy, pravy = [], []
    for i, (x, y, u) in enumerate(vzorky):
        dalsi = vzorky[(i + 1) % len(vzorky)] if uzavreno else vzorky[min(i + 1, len(vzorky) - 1)]
        pred = vzorky[(i - 1) % len(vzorky)] if uzavreno else vzorky[max(i - 1, 0)]
        dx, dy = dalsi[0] - pred[0], dalsi[1] - pred[1]
        d = math.hypot(dx, dy) or 1
        nx, ny = -dy / d, dx / d
        w = sirka_v(sila, u, useku) / 2
        levy.append((x + nx * w, y + ny * w))
        pravy.append((x - nx * w, y - ny * w))

    def cislo(v):
        return f'{v:.1f}'.replace('.0', '')

    def usek(pole):
        return ' '.join(f'{cislo(x)} {cislo(y)}' for x, y in pole)

    if uzavreno:
        # dva prstence; díru mezi nimi vyřízne fill-rule evenodd
        return f'M{usek(levy)}Z M{usek(list(reversed(pravy)))}Z'
    return f'M{usek(levy)} L{usek(list(reversed(pravy)))}Z'


def kruh(sx, sy, r, sila, od=-90, kusu=5):
    """Kruhový tah — pro kola, mince a sluníčko."""
    body = [(sx + r * math.cos(math.radians(od + i * 360 / kusu)),
             sy + r * math.sin(math.radians(od + i * 360 / kusu))) for i in range(kusu)]
    return tah(body, sila, uzavreno=True)


def oblouk(sx, sy, r, od, do, sila, kusu=5):
    body = [(sx + r * math.cos(math.radians(od + (do - od) * i / (kusu - 1))),
             sy + r * math.sin(math.radians(od + (do - od) * i / (kusu - 1)))) for i in range(kusu)]
    return tah(body, sila)


# --- kresby ----------------------------------------------------------------
# Každá ikona je seznam tahů. Souřadnice v soustavě 100 × 100, počátek vlevo
# nahoře. Profil šířky začíná a končí nulou všude, kde má tah doběhnout
# do špičky — stejně jako oblouky srdce.
IKONY = {
    # Rozvoj města — dům s podloubím, jaké je na náměstí
    'rozvoj-mesta': [
        tah([(6, 46), (50, 14), (94, 46)], [0, 13, 0]),
        oblouk(50, 66, 26, 180, 360, [10, 13, 13, 13, 10]),
        tah([(24, 66), (24, 94)], [10, 10]),
        tah([(76, 66), (76, 94)], [10, 10]),
    ],
    # Děti — drak s ocasem
    'deti': [
        tah([(50, 8), (74, 34), (50, 62), (26, 34)], [6, 9, 6, 9], uzavreno=True),
        tah([(50, 62), (38, 74), (58, 82), (42, 96)], [7, 5, 4, 0]),
    ],
    # Senioři — slunce s paprsky
    'seniori': [
        kruh(50, 54, 21, [9, 12, 12, 11, 9]),
        tah([(50, 22), (50, 6)], [7, 0]),
        tah([(50, 86), (50, 98)], [6, 0]),
        tah([(19, 54), (4, 54)], [7, 0]),
        tah([(81, 54), (96, 54)], [7, 0]),
        tah([(28, 32), (16, 20)], [6, 0]),
        tah([(72, 32), (84, 20)], [6, 0]),
    ],
    # Doprava — silnice ubíhající do dálky
    'doprava': [
        tah([(10, 92), (34, 52), (44, 14)], [14, 7, 0]),
        tah([(92, 92), (68, 52), (57, 14)], [14, 7, 0]),
        tah([(51, 88), (51, 68)], [0, 8]),
        tah([(51, 56), (51, 40)], [6, 0]),
    ],
    # Bezpečnost — štít
    'bezpecnost': [
        tah([(20, 17), (35, 11), (50, 9), (65, 11), (80, 17), (87, 28),
             (80, 58), (67, 77), (50, 92), (33, 77), (20, 58), (13, 28)],
            [11, 11, 11, 11, 11, 11, 12, 10, 7, 10, 12, 11], uzavreno=True),
    ],
    # Zdravotnictví — kříž
    'zdravotnictvi': [
        tah([(50, 12), (50, 52), (50, 90)], [13, 18, 13]),
        tah([(12, 50), (50, 50), (88, 50)], [13, 18, 13]),
    ],
    # Kultura — nota
    'kultura': [
        kruh(34, 76, 17, [10, 13, 13, 12, 10]),
        tah([(50, 74), (52, 18)], [9, 5]),
        tah([(52, 18), (76, 28), (80, 46)], [6, 8, 0]),
    ],
    # Sport — míč v letu
    'sport': [
        kruh(62, 58, 27, [8, 11, 11, 10, 8]),
        tah([(44, 38), (62, 58), (46, 80)], [0, 6, 0]),
        tah([(4, 26), (24, 30), (38, 38)], [0, 8, 9]),
        tah([(8, 50), (24, 50)], [0, 6]),
    ],
    # Cestovní ruch — značka místa
    'cestovni-ruch': [
        tah([(50, 10), (82, 36), (50, 92), (18, 36)], [6, 13, 6, 13], uzavreno=True),
        kruh(50, 38, 9, [7, 7, 7, 7, 7]),
    ],
    # Životní prostředí — jehličnan
    'zivotni-prostredi': [
        tah([(50, 96), (50, 12)], [13, 3]),
        tah([(50, 28), (30, 44)], [8, 0]),
        tah([(50, 28), (70, 44)], [8, 0]),
        tah([(50, 50), (24, 68)], [9, 0]),
        tah([(50, 50), (76, 68)], [9, 0]),
        tah([(50, 72), (18, 90)], [9, 0]),
        tah([(50, 72), (82, 90)], [9, 0]),
    ],
    # Zeleň ve městě — list
    'zelen-ve-meste': [
        tah([(20, 84), (26, 34), (72, 14), (84, 54), (46, 84)], [0, 10, 12, 10, 0], uzavreno=True),
        tah([(22, 86), (50, 56), (78, 34)], [8, 6, 0]),
    ],
    # Místní části — rozcestník
    'mistni-casti': [
        tah([(50, 96), (50, 14)], [11, 6]),
        tah([(50, 32), (88, 32)], [10, 0]),
        tah([(50, 54), (12, 54)], [10, 0]),
        tah([(50, 74), (84, 74)], [9, 0]),
    ],
    # Účelné hospodaření — mince do dlaně
    'ucelne-hospodareni': [
        kruh(50, 32, 18, [8, 11, 11, 10, 8]),
        oblouk(50, 54, 32, 0, 180, [0, 12, 14, 12, 0]),
    ],
    # Nechceme — šipka dolů: ceny držíme při zemi
    'nechceme': [
        tah([(50, 8), (50, 74)], [7, 15]),
        tah([(20, 52), (50, 92), (80, 52)], [0, 14, 0]),
    ],
    # Fungování úřadu — bublina, tedy řeč s občany
    'fungovani-uradu': [
        tah([(50, 12), (88, 34), (74, 66), (34, 70), (12, 44)],
            [7, 12, 12, 10, 12], uzavreno=True),
        tah([(34, 70), (26, 92), (46, 72)], [8, 0, 6]),
    ],
}


def main():
    data = {slug: tahy for slug, tahy in IKONY.items()}
    CIL.write_text(json.dumps(data, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
    znaku = sum(len(t) for tahy in data.values() for t in tahy)
    print(f'{CIL.relative_to(KOREN)}: {len(data)} ikon, {znaku / 1024:.0f} kB cest')


if __name__ == '__main__':
    main()
