# volbats — Volba pro město Trhové Sviny

Web pro komunální volby 2026. Obsah i vzhled zatím odpovídají webu z voleb
2022; nová grafika, kandidátka a program přijdou v dalších krocích.

## Jak to funguje

React + Vite, výstup jsou **statické soubory** — žádný backend. Každá adresa
se při buildu předgeneruje do vlastního `index.html`, takže přímé odkazy
fungují, vyhledávače vidí obsah bez spouštění JS a React se na hotové HTML jen
napojí. Publikuje se na **GitHub Pages** přes Actions při každém pushi do
`main` (`.github/workflows/deploy.yml`).

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
| `src/data/*.json` | **obsah webu** — kandidáti, priority, texty stránek |
| `src/obrazky/` | fotky a obrázky (Vite jim dá hash) |
| `src/styles/main.scss` | šablona volbats2022 přenesená na Bootstrap 5 |
| `tools/prerender.js` | předgenerování stránek do statického HTML |
| `tools/nginx.conf` | hlavičky pro lokální náhled |

Obsah se upravuje v `src/data/*.json`. Kandidáta stačí přidat do
`kandidati.json`; fotku k němu do `src/obrazky/` a odkázat ji jménem souboru.
Priority mají v `priority.json` `slug`, který se rovnou stane adresou.

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
  je vektor (obtažené z původního PNG) a volební číslo je `cislo`
  v `src/data/web.js`. Celé logo se škáluje jedinou hodnotou `font-size`,
  takže na mobilu zůstane čitelné — dřív se zmenšovalo do nečitelna.
