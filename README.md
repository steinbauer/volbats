# volbats — Volba pro město Trhové Sviny

Web pro komunální volby 2026. Základem je statická kopie webu
[volbats.cz](https://volbats.cz/) z voleb 2022, nad kterou přepisujeme
grafiku, kandidáty a program.

## Jak to funguje

Žádný build, žádný generátor, žádný backend. V `site/` leží hotové statické
soubory, které se publikují **na GitHub Pages** přes GitHub Actions — každý
push do `main` spustí `.github/workflows/deploy.yml`. Cokoliv se do webu
přidá, musí fungovat bez serveru: formuláře a podobné věci klientsky nebo
přes externí službu.

## Lokální náhled

```bash
make url        # vypíše adresu, kontejner nastartuje sám
make stop-dev   # zastaví ho
make status     # kde to stojí
make logs       # log nginxu
```

Adresa vychází z názvu větve, takže každý worktree má vlastní:

```
https://<vetev>.volbats.me.lab.home/
```

Servíruje to nginx v dockeru, vystavený přes labový traefik (`docker-compose.yml`).

## Struktura

| Cesta | Co to je |
|---|---|
| `site/` | publikovaný obsah — přesně to, co skončí na Pages |
| `site/theme/volbats2022/` | šablona: `style.css`, obrázky, favicon |
| `site/img/11610/` | fotky kandidátů a priorit, ve variantách podle šířky |
| `site/asset/` | bootstrap 4.0.0, jQuery 3.3.1, fancybox 3.2.5 |
| `site/assets/fonts/` | Roboto 300/400/700, staženo lokálně |
| `tools/mirror.sh` | znovustažení kopie z ostrého webu |

## Znovustažení originálu

```bash
make mirror   # POZOR: smaže a přepíše celý adresář site/
```

Skript po sobě uklidí názvy souborů s query stringem (`style.css?v=0.3.7`)
a stáhne fonty z `cdn.polyweb.cz` k sobě, aby kopie nezávisela na cizím
serveru. Až začneme obsah přepisovat, `make mirror` už nepouštěj — přišel
bys o práci.
