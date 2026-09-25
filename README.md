# volbats — Volba pro město Trhové Sviny

Web pro komunální volby 2026 a tiskoviny, které z týchž dat vznikají —
leták, plakát a kartičky s QR kódy.

## Jak to funguje

React + Vite, výstup jsou **statické soubory** — žádný backend. Každá adresa
se při buildu předgeneruje do vlastního `index.html`, takže přímé odkazy
fungují, vyhledávače vidí obsah bez spouštění JS a React se na hotové HTML jen
napojí. Publikuje se na **GitHub Pages** přes Actions při každém pushi do
`main` (`.github/workflows/deploy.yml`), veřejná adresa je **volbats.cz** —
vlastní doména nad Pages, drží ji `public/CNAME`.

Názvy souborů v `dist/assets/` obsahují hash obsahu. Po nasazení nové verze
tedy prohlížeč nemá jak podstrčit starou — **ctrl+F5 není potřeba**. Lokální
nginx k tomu ještě posílá `Cache-Control: no-cache` na HTML a roční
`immutable` na hashované assety (`tools/nginx.conf`).

## Lokální práce

```bash
make dev        # vývojový server s hot reloadem
make url        # sestaví web a vypíše adresu, kde běží
make stop-dev   # zastaví kontejner
make status     # kde to stojí
```

Adresa vychází z názvu větve, takže každý worktree má vlastní:

```
https://<vetev>.volbats.kamil.lab.home/
```

Servíruje to nginx v dockeru, vystavený přes labový traefik.

## Struktura

| Cesta | Co to je |
|---|---|
| `src/pages/` | jednotlivé stránky |
| `src/components/` | hlavička, menu, patička, dlaždice kandidáta |
| `src/data/*.json` | **obsah webu** — kandidáti, program, texty stránek |
| `src/obrazky/` | fotky a obrázky (Vite jim dá hash) |
| `src/styles/main.scss` | šablona volbats2022 přenesená na Bootstrap 5 |
| `src/data/ikony.json` | kresby témat programu, vyrábí je `tools/ikony.py` |
| `tools/prerender.js` | předgenerování stránek do statického HTML |
| `tools/tiskoviny.py` | společný základ letáku, plakátů a kartiček |
| `tools/qr.py` | generátor QR kódů (bez závislostí) |
| `tools/nginx.conf` | hlavičky pro lokální náhled |
| `tools/aliasy.py` | krátké adresy kandidat1…10, hp a program.volbats.cz |

Obsah se upravuje v `src/data/*.json`. Kandidáta stačí přidat do
`kandidati.json`; fotku k němu připravit `tools/fotky.py` a odkázat ji
v poli `foto` jménem bez velikosti a přípony. Program je v `program.json`
jako sekce s odrážkami; `slug` sekce je kotva na `/program/` i cíl dlaždice
na úvodní stránce.

Titulek a popisek stránky nastavuje komponenta `Meta`. Při předgenerování je
sbírá `entry-server.jsx` a `tools/prerender.js` je vkládá rovnou do hlavičky,
takže je vyhledávače vidí bez spouštění JS.

## Značka

Logo je srdce s nápisem uvnitř, obtažené z letáku z roku 2022
(`tools/obtahni-logo.py`). Křivky žijí v `src/components/Znak.jsx` a berou si
je i generátory tiskovin, takže značka na webu a na papíře nemůže být každá
jiná. `Logo.jsx` je plná podoba s nápisem uvnitř — čitelná zhruba od 140 px;
menší místa sázejí název vedle srdce. Volební číslo má vlastní srdce
s přechodem, stejně jako na letáku z minula.

Ikony témat programu kreslí `tools/ikony.py` stejnou logikou jako srdce: osa
tahu a profil šířky, který doběhne do špičky. Kresby jdou do
`src/data/ikony.json`, odkud je čte web i tiskoviny.

## Tiskoviny

```bash
make letak      # A3 přeložená napůl, čtyři strany A4
make plakaty    # A5 ve třech variantách: temata, lide, fotka
make qr         # kartičky s QR na A4 a holé kódy v SVG a PNG
```

Všechno se sází jako HTML a tiskne přes Chrome (browserless na `:3000`),
obsah se bere z týchž dat jako web. Před tiskem skripty změří, jestli se
obsah na stranu vejde — přetečení by se v PDF projevilo useknutým řádkem,
což je na hotové tiskovině vidět pozdě. Hesla plakátu jsou v
`src/data/plakat.json`, ať se dají přeházet bez sahání do sazby.

QR kódy generuje `tools/qr.py`, vlastní kodér bez závislostí. Správnost se
ověřovala proti `qrcode-generator` a hotové kódy se četly přes `jsQR`.

## Krátké adresy kandidátů

`kandidat1.volbats.cz` až `kandidat10.volbats.cz` přesměrují na medailonek
kandidáta s tím číslem na listině. GitHub Pages unese jen jednu vlastní
doménu na repozitář, takže každá zkratka je samostatný repozitář
`steinbauer/<subdoména>` se stránkou, která hned přesměruje, a HTTPS
certifikát k ní vydá GitHub. V DNS u Wedosu na ně míří
`<subdoména> CNAME steinbauer.github.io.` Stejně fungují `hp.volbats.cz`
(úvodní stránka) a `program.volbats.cz` — další se přidávají do `OSTATNI`
v `tools/aliasy.py`.

```bash
make aliasy     # token v ~/.config/volbats/github-token
```

Skript je idempotentní — když se změní pořadí nebo slug, stačí ho pustit
znovu. HTTPS jde vynutit až po vydání certifikátu, to hlásí ve výpisu.

## Poznámky k migraci

Web vznikl přenesením kopie volbats.cz z roku 2022. Skripty
`tools/mirror.sh` (stažení originálu do `site/`) a `tools/extract.py`
(vytažení obsahu do `src/data/`) byly jednorázové — obsah už žije v repu
a znovu se nespouštějí. Původní kopie je v historii v commitu, kterým se
sem dostala.

Co se proti roku 2022 změnilo:

- **Bootstrap 4 → 5.** `.jumbotron` nahradil vlastní `.box`,
  `.embed-responsive` je `.ratio`, `.text-right` je `.text-end`.
- **jQuery, fancybox a bootstrap.bundle jsou pryč.** Rozbalovací menu jede
  na CSS (`:hover` / `:focus-within`), takže funguje i bez JS.
- **Kontaktní formulář je pryč.** Dřív odesílal data na server PolyWeb CMS
  s reCAPTCHOU; statický web backend nemá a psát se dá e-mailem.
- **Hlavička už není obrázek.** Název, město i claim jsou text, srdce
  je vektor a volební číslo je `cislo` v `src/data/web.js`.

Proti prvnímu návrhu pro rok 2026 se pak ještě změnilo:

- **Plocha není bílá.** Stránka má krémový podklad z letáku
  (`#fdf7e4` → `#fdeee7`), obsahové bloky stojí na bílém papíře (`.papir`).
- **Lišta se drží nahoře.** Na úvodní stránce začíná logo velké a přesahuje
  do společné fotky; po odrolování se scvrkne do řádkové podoby v liště.
  Na mobilu i na širokém displeji tentýž mechanismus, takže se srdce nikde
  neobjeví dvakrát.
- **Sekce programu mají místo čísel ikony.** Čísla 01, 02, 03 jen
  přeříkávala pořadí.
