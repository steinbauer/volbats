#!/usr/bin/env python3
"""Generátor QR kódů.

Web nemá žádné závislosti a kvůli třem QR kódům nemá smysl je zavádět, takže
je tu vlastní kodér — bajtový režim, verze 1 až 10, všechny úrovně korekce.
Na adresu typu https://volbats.cz/program/ to bohatě stačí.

    python3 tools/qr.py "https://volbats.cz/" > qr.svg

Používají ho tools/qr-karticky.py, tools/letak.py i tools/plakat.py, aby
kódy na všech tiskovinách vypadaly stejně.
"""
import sys

# Kolik opravných kódových slov na blok a jak jsou bloky velké.
# Klíč je (verze, úroveň), hodnota (opravných na blok, [(bloků, dat v bloku)]).
BLOKY = {
    (1, 'L'): (7, [(1, 19)]), (1, 'M'): (10, [(1, 16)]),
    (1, 'Q'): (13, [(1, 13)]), (1, 'H'): (17, [(1, 9)]),
    (2, 'L'): (10, [(1, 34)]), (2, 'M'): (16, [(1, 28)]),
    (2, 'Q'): (22, [(1, 22)]), (2, 'H'): (28, [(1, 16)]),
    (3, 'L'): (15, [(1, 55)]), (3, 'M'): (26, [(1, 44)]),
    (3, 'Q'): (18, [(2, 17)]), (3, 'H'): (22, [(2, 13)]),
    (4, 'L'): (20, [(1, 80)]), (4, 'M'): (18, [(2, 32)]),
    (4, 'Q'): (26, [(2, 24)]), (4, 'H'): (16, [(4, 9)]),
    (5, 'L'): (26, [(1, 108)]), (5, 'M'): (24, [(2, 43)]),
    (5, 'Q'): (18, [(2, 15), (2, 16)]), (5, 'H'): (22, [(2, 11), (2, 12)]),
    (6, 'L'): (18, [(2, 68)]), (6, 'M'): (16, [(4, 27)]),
    (6, 'Q'): (24, [(4, 19)]), (6, 'H'): (28, [(4, 15)]),
    (7, 'L'): (20, [(2, 78)]), (7, 'M'): (18, [(4, 31)]),
    (7, 'Q'): (18, [(2, 14), (4, 15)]), (7, 'H'): (26, [(4, 13), (1, 14)]),
    (8, 'L'): (24, [(2, 97)]), (8, 'M'): (22, [(2, 38), (2, 39)]),
    (8, 'Q'): (22, [(4, 18), (2, 19)]), (8, 'H'): (26, [(4, 14), (2, 15)]),
    (9, 'L'): (30, [(2, 116)]), (9, 'M'): (22, [(3, 36), (2, 37)]),
    (9, 'Q'): (20, [(4, 16), (4, 17)]), (9, 'H'): (24, [(4, 12), (4, 13)]),
    (10, 'L'): (18, [(2, 68), (2, 69)]), (10, 'M'): (26, [(4, 43), (1, 44)]),
    (10, 'Q'): (24, [(6, 19), (2, 20)]), (10, 'H'): (28, [(6, 15), (2, 16)]),
}

# Středy zarovnávacích čtverců
ZAROVNANI = {1: [], 2: [6, 18], 3: [6, 22], 4: [6, 26], 5: [6, 30], 6: [6, 34],
             7: [6, 22, 38], 8: [6, 24, 42], 9: [6, 26, 46], 10: [6, 28, 50]}

# Dvoubitový kód úrovně korekce, jak jde do formátové informace
KOD_UROVNE = {'L': 1, 'M': 0, 'Q': 3, 'H': 2}


# --- aritmetika v Galoisově tělese GF(256) ---------------------------------
EXP = [0] * 512
LOG = [0] * 256
_x = 1
for _i in range(255):
    EXP[_i] = _x
    LOG[_x] = _i
    _x <<= 1
    if _x & 0x100:
        _x ^= 0x11D
for _i in range(255, 512):
    EXP[_i] = EXP[_i - 255]


def nasob(a, b):
    if a == 0 or b == 0:
        return 0
    return EXP[LOG[a] + LOG[b]]


def generator(stupen):
    """Generující polynom Reed-Solomonova kódu."""
    g = [1]
    for i in range(stupen):
        novy = [0] * (len(g) + 1)
        for j, c in enumerate(g):
            novy[j] ^= c                       # posun o x
            novy[j + 1] ^= nasob(c, EXP[i])    # a člen s kořenem α^i
        g = novy
    return g


def oprava(data, kolik):
    """Opravná kódová slova k jednomu bloku."""
    g = generator(kolik)
    zbytek = list(data) + [0] * kolik
    for i in range(len(data)):
        koef = zbytek[i]
        if koef:
            for j, c in enumerate(g):
                zbytek[i + j] ^= nasob(c, koef)
    return zbytek[len(data):]


def bch(hodnota, generujici, bitu):
    """Zbytek po dělení — pro formátovou i verzovou informaci."""
    z = hodnota
    while z.bit_length() - 1 >= bitu:
        z ^= generujici << (z.bit_length() - generujici.bit_length())
    return z


# --- sestavení dat ---------------------------------------------------------
def vyber_verzi(delka, uroven):
    for verze in range(1, 11):
        _, bloky = BLOKY[(verze, uroven)]
        kapacita = sum(p * d for p, d in bloky)
        pocet_bitu = 8 if verze < 10 else 16
        if delka + 2 + (4 + pocet_bitu + 7) // 8 <= kapacita:
            return verze
    raise ValueError(f'{delka} bajtů se do verze 10 nevejde, zvol nižší korekci')


def kodova_slova(text, verze, uroven):
    bajty = text.encode('utf-8')
    _, bloky = BLOKY[(verze, uroven)]
    kapacita = sum(p * d for p, d in bloky)

    bity = '0100'                                  # bajtový režim
    bity += format(len(bajty), '08b' if verze < 10 else '016b')
    bity += ''.join(format(b, '08b') for b in bajty)
    bity += '0' * min(4, kapacita * 8 - len(bity))  # ukončovač
    bity += '0' * (-len(bity) % 8)

    slova = [int(bity[i:i + 8], 2) for i in range(0, len(bity), 8)]
    vypln = [0xEC, 0x11]
    while len(slova) < kapacita:
        slova.append(vypln[(len(slova) - len(bity) // 8) % 2])
    return slova


def prolozeni(slova, verze, uroven):
    """Data i opravu rozdělí do bloků a proloží, jak žádá norma."""
    opravnych, rozdeleni = BLOKY[(verze, uroven)]
    data_bloky, oprava_bloky, i = [], [], 0
    for pocet, delka in rozdeleni:
        for _ in range(pocet):
            blok = slova[i:i + delka]
            i += delka
            data_bloky.append(blok)
            oprava_bloky.append(oprava(blok, opravnych))

    ven = []
    for k in range(max(len(b) for b in data_bloky)):
        for b in data_bloky:
            if k < len(b):
                ven.append(b[k])
    for k in range(opravnych):
        for b in oprava_bloky:
            ven.append(b[k])
    return ven


# --- mřížka ----------------------------------------------------------------
MASKY = [
    lambda r, c: (r + c) % 2 == 0,
    lambda r, c: r % 2 == 0,
    lambda r, c: c % 3 == 0,
    lambda r, c: (r + c) % 3 == 0,
    lambda r, c: (r // 2 + c // 3) % 2 == 0,
    lambda r, c: (r * c) % 2 + (r * c) % 3 == 0,
    lambda r, c: ((r * c) % 2 + (r * c) % 3) % 2 == 0,
    lambda r, c: ((r + c) % 2 + (r * c) % 3) % 2 == 0,
]


def prazdna(verze):
    n = verze * 4 + 17
    return [[None] * n for _ in range(n)], n


def vzory(m, n, verze):
    """Hledáčky, oddělovače, časování a zarovnání. Vrací masku rezervace."""
    rezerva = [[False] * n for _ in range(n)]

    def ctverec(r0, c0):
        for dr in range(-1, 8):
            for dc in range(-1, 8):
                r, c = r0 + dr, c0 + dc
                if not (0 <= r < n and 0 <= c < n):
                    continue
                uvnitr = 0 <= dr <= 6 and 0 <= dc <= 6
                tmave = uvnitr and (dr in (0, 6) or dc in (0, 6)
                                    or (2 <= dr <= 4 and 2 <= dc <= 4))
                m[r][c] = tmave
                rezerva[r][c] = True

    ctverec(0, 0)
    ctverec(0, n - 7)
    ctverec(n - 7, 0)

    for i in range(8, n - 8):
        m[6][i] = m[i][6] = i % 2 == 0
        rezerva[6][i] = rezerva[i][6] = True

    stredy = ZAROVNANI[verze]
    for r in stredy:
        for c in stredy:
            if (r < 9 and c < 9) or (r < 9 and c > n - 10) or (r > n - 10 and c < 9):
                continue
            for dr in range(-2, 3):
                for dc in range(-2, 3):
                    m[r + dr][c + dc] = max(abs(dr), abs(dc)) != 1
                    rezerva[r + dr][c + dc] = True

    m[n - 8][8] = True                       # vždy tmavý modul
    rezerva[n - 8][8] = True

    for i in range(9):                       # místo pro formátovou informaci
        if i != 6:
            rezerva[8][i] = rezerva[i][8] = True
    for i in range(8):
        rezerva[8][n - 1 - i] = rezerva[n - 1 - i][8] = True

    if verze >= 7:                           # a pro verzovou
        for i in range(6):
            for j in range(3):
                rezerva[n - 11 + j][i] = rezerva[i][n - 11 + j] = True
    return rezerva


def poloz(m, n, rezerva, slova):
    bity = ''.join(format(s, '08b') for s in slova)
    i = 0
    sloupec = n - 1
    nahoru = True
    while sloupec > 0:
        if sloupec == 6:                     # sloupec s časováním se přeskakuje
            sloupec -= 1
        rady = range(n - 1, -1, -1) if nahoru else range(n)
        for r in rady:
            for c in (sloupec, sloupec - 1):
                if rezerva[r][c]:
                    continue
                m[r][c] = i < len(bity) and bity[i] == '1'
                i += 1
        nahoru = not nahoru
        sloupec -= 2


def pokuta(m, n):
    """Ohodnocení masky podle čtyř pravidel normy."""
    body = 0

    for pole in (m, [list(r) for r in zip(*m)]):
        for rada in pole:
            beh, predchozi = 1, rada[0]
            for v in rada[1:]:
                if v == predchozi:
                    beh += 1
                else:
                    if beh >= 5:
                        body += beh - 2
                    beh, predchozi = 1, v
            if beh >= 5:
                body += beh - 2
            # 1:1:3:1:1 kolem tmavého vzoru
            text = ''.join('1' if v else '0' for v in rada)
            for vzor in ('10111010000', '00001011101'):
                od = 0
                while (kde := text.find(vzor, od)) != -1:
                    body += 40
                    od = kde + 1

    for r in range(n - 1):
        for c in range(n - 1):
            ctyri = (m[r][c], m[r][c + 1], m[r + 1][c], m[r + 1][c + 1])
            if all(ctyri) or not any(ctyri):
                body += 3

    # Čtvrté pravidlo: jak daleko je podíl tmavých modulů od poloviny,
    # po pětiprocentních krocích. Počítá se celočíselně, aby to nezáviselo
    # na zaokrouhlování desetinných čísel.
    tmavych = sum(v for rada in m for v in rada)
    celkem = n * n
    body += ((abs(tmavych * 20 - celkem * 10) + celkem - 1) // celkem - 1) * 10
    return body


def format_info(uroven, maska):
    hodnota = (KOD_UROVNE[uroven] << 3) | maska
    return ((hodnota << 10) | bch(hodnota << 10, 0x537, 10)) ^ 0x5412


def zapis_format(m, n, uroven, maska):
    bity = format(format_info(uroven, maska), '015b')
    for i in range(15):
        b = bity[14 - i] == '1'
        # první kopie: svisle u levého horního hledáčku, pak vodorovně
        if i < 6:
            m[i][8] = b
        elif i == 6:
            m[7][8] = b
        elif i == 7:
            m[8][8] = b
        elif i == 8:
            m[8][7] = b
        else:
            m[8][14 - i] = b

        # druhá kopie: vodorovně vpravo nahoře, svisle vlevo dole
        if i < 8:
            m[8][n - 1 - i] = b
        else:
            m[n - 15 + i][8] = b


def zapis_verzi(m, n, verze):
    if verze < 7:
        return
    bity = format((verze << 12) | bch(verze << 12, 0x1F25, 12), '018b')
    for i in range(18):
        b = bity[17 - i] == '1'
        r, c = i // 3, i % 3
        m[r][n - 11 + c] = b
        m[n - 11 + c][r] = b


def matice(text, uroven='M', verze=None):
    """Vrátí QR kód jako pole boolů, bez klidové zóny."""
    verze = verze or vyber_verzi(len(text.encode('utf-8')), uroven)
    slova = prolozeni(kodova_slova(text, verze, uroven), verze, uroven)

    m, n = prazdna(verze)
    rezerva = vzory(m, n, verze)
    zapis_verzi(m, n, verze)
    poloz(m, n, rezerva, slova)

    nejlepsi = None
    for maska in range(8):
        kandidat = [rada[:] for rada in m]
        for r in range(n):
            for c in range(n):
                if not rezerva[r][c] and MASKY[maska](r, c):
                    kandidat[r][c] = not kandidat[r][c]
        zapis_format(kandidat, n, uroven, maska)
        skore = pokuta(kandidat, n)
        if nejlepsi is None or skore < nejlepsi[0]:
            nejlepsi = (skore, kandidat)
    return nejlepsi[1]


def svg(text, uroven='M', klid=4, barva='#191413', pozadi='#ffffff'):
    """QR kód jako SVG. Rozměr je v modulech, velikost si řídí CSS."""
    m = matice(text, uroven)
    n = len(m)
    strana = n + 2 * klid

    kusy = []
    for r, rada in enumerate(m):
        c = 0
        while c < n:
            if rada[c]:
                zacatek = c
                while c < n and rada[c]:
                    c += 1
                kusy.append(f'M{zacatek + klid} {r + klid}h{c - zacatek}v1h-{c - zacatek}z')
            else:
                c += 1

    podklad = (f'<path fill="{pozadi}" d="M0 0h{strana}v{strana}H0z"/>' if pozadi else '')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {strana} {strana}" '
            f'shape-rendering="crispEdges">{podklad}'
            f'<path fill="{barva}" d="{"".join(kusy)}"/></svg>')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    uroven = sys.argv[2] if len(sys.argv) > 2 else 'M'
    print(svg(sys.argv[1], uroven))
