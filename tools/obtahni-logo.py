#!/usr/bin/env python3
"""Obtáhne srdce z loga do SVG křivek.

Předlohou je fotka letáku z roku 2022 — vektorový originál se nedochoval.
Kresba na letáku je jiná než srdce, které mělo logo na webu 2022: širší,
s plnějšími oblouky. Lídryně sdružení si vyžádala právě tuhle podobu.

Nepracuje s binární maskou, ale se spojitým polem „tmavosti": rozostření
tisku ve fotce nese subpixelovou informaci o hraně, takže špičky tahů
zůstanou špičaté. Špičky přecházejí do tmavě hnědé, odlesk blesku naopak
kus levého oblouku přesvětlí — proto se jas kombinuje s červeností.

    python3 tools/obtahni-logo.py

Vypíše dvě cesty `d`; ty patří do CESTA v src/components/Znak.jsx. Spouští
se ručně a jen když přibude lepší podklad — fotka leží mimo repozitář,
v .lab-uploads.
"""
import numpy as np
from PIL import Image
from pathlib import Path

KOREN = Path(__file__).resolve().parent.parent
FOTKA = (KOREN / '.lab-uploads'
         / '2026-09-13T10-28-52-244Z-photo_2026-09-13_12-24-29.jpg')
VYREZ = (1328, 432, 1512, 686)
UROVEN = 57.0        # půl cesty mezi papírem a plnou barvou
PERSPEKTIVA = 1.054  # fotka protahuje svislou osu, změřeno na srdci se čtyřkou
SKLON = -1.0         # zbytkové natočení stránky
NASOBEK = 6

HRANY = {1: [(3, 2)], 2: [(2, 1)], 3: [(3, 1)], 4: [(0, 1)], 6: [(0, 2)],
         7: [(3, 0)], 8: [(3, 0)], 9: [(0, 2)], 11: [(0, 1)], 12: [(3, 1)],
         13: [(2, 1)], 14: [(3, 2)], 5: [(3, 0), (2, 1)], 10: [(3, 2), (0, 1)]}


PAPIR = 178.0   # jas papíru ve fotce


def pole():
    """Pole „tmavosti" — tisk je tmavší než papír. Špičky tahů přecházejí
    do tmavě hnědé, takže na červenost se spolehnout nejde."""
    a = np.asarray(Image.open(FOTKA).convert('RGB').crop(VYREZ)).astype(np.float32)
    luma = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    cervenost = a[..., 0] - (a[..., 1] + a[..., 2]) / 2
    # Odlesk blesku přesvětlí kus levého oblouku, tam je vodítkem červenost;
    # špičky tahů naopak přecházejí do tmavě hnědé, tam rozhoduje jas.
    tmavost = np.maximum(PAPIR - luma, (cervenost - 18) * 1.9)
    im = Image.fromarray(tmavost, mode='F')
    im = im.resize((im.width * NASOBEK, im.height * NASOBEK), Image.BICUBIC)
    # Lem papíru kolem dokola: obrys, který by dosáhl na okraj pole, by se
    # nedal uzavřít a marching squares by ho useknul tětivou.
    return np.pad(np.asarray(im).astype(float), 3 * NASOBEK)


def vzorek(f, x, y):
    h, w = f.shape
    x = min(max(x, 0), w - 1.001)
    y = min(max(y, 0), h - 1.001)
    x0, y0 = int(x), int(y)
    tx, ty = x - x0, y - y0
    return ((f[y0, x0] * (1 - tx) + f[y0, x0 + 1] * tx) * (1 - ty)
            + (f[y0 + 1, x0] * (1 - tx) + f[y0 + 1, x0 + 1] * tx) * ty)


def izolinie(f, uroven):
    h, w = f.shape
    segmenty = []
    for y in range(h - 1):
        for x in range(w - 1):
            a, b = f[y, x], f[y, x + 1]
            c, d = f[y + 1, x + 1], f[y + 1, x]
            idx = (a > uroven) * 8 + (b > uroven) * 4 + (c > uroven) * 2 + (d > uroven)
            if idx in (0, 15):
                continue

            def bod(hrana):
                if hrana == 0:
                    return (x + (uroven - a) / (b - a), float(y))
                if hrana == 1:
                    return (float(x + 1), y + (uroven - b) / (c - b))
                if hrana == 2:
                    return (x + (uroven - d) / (c - d), float(y + 1))
                return (float(x), y + (uroven - a) / (d - a))

            for h1, h2 in HRANY[idx]:
                p, q = bod(h1), bod(h2)
                dx, dy = q[0] - p[0], q[1] - p[1]
                sx, sy = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
                if vzorek(f, sx - dy * 0.3, sy + dx * 0.3) <= uroven:
                    p, q = q, p
                segmenty.append([p, q])

    def klic(p):
        return (round(p[0], 5), round(p[1], 5))

    zacatky = {}
    for i, s in enumerate(segmenty):
        zacatky.setdefault(klic(s[0]), []).append(i)

    smycky, hotovo = [], set()
    for i in range(len(segmenty)):
        if i in hotovo:
            continue
        smycka = [segmenty[i][0]]
        j = i
        while j is not None and j not in hotovo:
            hotovo.add(j)
            smycka.append(segmenty[j][1])
            dalsi = [k for k in zacatky.get(klic(segmenty[j][1]), []) if k not in hotovo]
            j = dalsi[0] if dalsi else None
        if len(smycka) > 200:
            smycky.append(np.array(smycka))
    smycky.sort(key=lambda s: -len(s))
    return smycky


def delka(b):
    d = np.diff(np.vstack([b, b[:1]]), axis=0)
    return float(np.hypot(d[:, 0], d[:, 1]).sum())


def vyhlad(b, okno):
    n, j = len(b), np.ones(okno) / okno
    out = np.empty_like(b)
    for k in range(2):
        r = np.concatenate([b[-okno:, k], b[:, k], b[:okno, k]])
        out[:, k] = np.convolve(r, j, 'same')[okno:okno + n]
    return out


def uzly(b, pocet, duraz=4.0):
    """Body rozmístí podle délky i zakřivení — do špiček jich padne víc."""
    p = np.vstack([b, b[:1]])
    d = np.hypot(*np.diff(p, axis=0).T)
    s = np.concatenate([[0], np.cumsum(d)])

    # zakřivení z úhlu mezi sousedními úseky
    v = np.diff(p, axis=0)
    uhly = np.arctan2(v[:, 1], v[:, 0])
    zmena = np.abs(np.diff(np.concatenate([uhly, uhly[:1]])))
    zmena = np.minimum(zmena, 2 * np.pi - zmena)
    zmena = np.convolve(np.concatenate([zmena[-20:], zmena, zmena[:20]]),
                        np.ones(21) / 21, 'same')[20:20 + len(zmena)]

    vaha = d * (1 + duraz * zmena / max(zmena.max(), 1e-9))
    t = np.concatenate([[0], np.cumsum(vaha)])
    cil = np.linspace(0, t[-1], pocet, endpoint=False)
    kde = np.interp(cil, t, s)
    return np.column_stack([np.interp(kde, s, p[:, 0]), np.interp(kde, s, p[:, 1])])


def na_bezier(p):
    """Celá čísla stačí: viewBox je 1000 jednotek na šířku, tedy desetina
    procenta na jednotku — pod rozlišovací schopnost tisku i obrazovky."""
    n = len(p)
    d = [f'M{p[0,0]:.0f} {p[0,1]:.0f}']
    for i in range(n):
        p0, p1, p2, p3 = p[(i - 1) % n], p[i], p[(i + 1) % n], p[(i + 2) % n]
        c1 = p1 + (p2 - p0) / 6
        c2 = p2 - (p3 - p1) / 6
        d.append(f'C{c1[0]:.0f} {c1[1]:.0f} {c2[0]:.0f} {c2[1]:.0f} {p2[0]:.0f} {p2[1]:.0f}')
    return ''.join(d) + 'Z'


def srovnej(cesty, sirka_vyrezu):
    """Otočí stránku do svislé polohy, srovná perspektivu i sklon."""
    out = []
    a = np.radians(SKLON)
    rot = np.array([[np.cos(a), -np.sin(a)], [np.sin(a), np.cos(a)]])
    for c in cesty:
        q = np.column_stack([c[:, 1], sirka_vyrezu - c[:, 0]])   # otočení o 90°
        q[:, 0] /= PERSPEKTIVA
        out.append(q @ rot.T)
    return out


def main():
    if not FOTKA.is_file():
        raise SystemExit(f'předloha {FOTKA} tu není')
    f = pole()
    smycky = [s / NASOBEK - 3 for s in izolinie(f, UROVEN)]
    print('nalezené smyčky:', [len(s) for s in smycky[:5]])
    cesty = srovnej(smycky[:2], (VYREZ[2] - VYREZ[0]))

    vse = np.vstack(cesty)
    x0, y0 = vse[:, 0].min(), vse[:, 1].min()
    sirka, vyska = vse[:, 0].max() - x0, vse[:, 1].max() - y0
    mer = 1000 / sirka
    print(f'viewBox 0 0 1000 {vyska * mer:.0f}  (poměr {sirka / vyska:.3f})')

    d = []
    for c in cesty:
        q = np.column_stack([(c[:, 0] - x0) * mer, (c[:, 1] - y0) * mer])
        q = vyhlad(q, 7)
        pocet = max(30, int(delka(q) / 30))
        print('  uzlů', pocet)
        d.append(na_bezier(uzly(q, pocet)))
    print()
    for cesta in d:
        print(f"  '{cesta}',")


if __name__ == '__main__':
    main()
