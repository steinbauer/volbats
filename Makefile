# Volba pro město Trhové Sviny — React + Vite, statický výstup
#
#   make url        adresa, na které web běží (build i kontejner sám naskočí)
#   make dev        vývojový server s hot reloadem
#   make build      sestaví web do dist/
#   make letak      vyrobí volební leták jako PDF
#   make plakaty    vyrobí tři varianty plakátu A5
#   make qr         vyrobí kartičky s QR kódy a kódy samotné
#   make socialni   vyrobí karty na Instagram a Facebook
#   make video      složí video k jednomu tématu (make video TEMA=doprava)
#   make videa-web  zmenšené kopie a náhledy videí, která jsou na webu
#   make videa      namluví a složí videa ke všem tématům programu
#   make ikony      přegeneruje ikony sekcí programu
#   make aliasy     nasadí kandidat1…10.volbats.cz (potřebuje GITHUB_TOKEN)
#   make stop-dev   zastaví kontejner

# Větev určuje adresu; lomítka ve větvi doména neunese, tak jdou na pomlčky.
BRANCH_NAME ?= $(shell git rev-parse --abbrev-ref HEAD 2>/dev/null | tr '/' '-')
COMPOSE      = BRANCH_NAME=$(BRANCH_NAME) docker compose
URL          = https://$(BRANCH_NAME).volbats.kamil.lab.home/

# npm v tomhle prostředí běží s NODE_ENV=production a bez tohohle by
# přeskočil devDependencies, tedy i samotné Vite.
NPM = NODE_ENV=development npm

.PHONY: url dev build install run-dev stop-dev restart-dev status logs letak plakaty qr socialni video videa videa-web ikony aliasy clean

## Vypíše adresu a zajistí, že běží aktuální build
url: build run-dev
	@echo ""
	@echo "  $(URL)"
	@echo ""

install: node_modules

node_modules: package.json
	@$(NPM) install --no-audit --no-fund --include=dev
	@touch node_modules

## Vývojový server s hot reloadem (běží na portu, ne přes traefik)
dev: install
	@$(NPM) run dev

build: install
	@$(NPM) run build

run-dev:
	@$(COMPOSE) up -d --quiet-pull
	@# Traefik si kontejner musí nejdřív všimnout, jinak první request spadne na 404
	@for i in 1 2 3 4 5 6 7 8 9 10; do \
		curl -sk -o /dev/null --max-time 3 $(URL) && break || sleep 1; \
	done

stop-dev:
	@$(COMPOSE) down

restart-dev: stop-dev run-dev

status:
	@$(COMPOSE) ps
	@printf '\nHTTP: '
	@curl -sk -o /dev/null -w '%{http_code}\n' --max-time 5 $(URL) || echo "nedostupné"

logs:
	@$(COMPOSE) logs -f

## Volební leták do PDF (potřebuje běžící browserless na :3000)
letak:
	@python3 tools/letak.py

## Plakát A5 ve třech variantách do plakaty/
plakaty:
	@python3 tools/plakat.py

## Kartičky s QR kódy na A4 a holé kódy v SVG a PNG do qr/
qr:
	@python3 tools/qr-karticky.py

## Karty na Instagram a Facebook do socialni/ (taky přes browserless)
socialni:
	@python3 tools/socialni.py

## Video 4:5 z hlasu, obrázků a titulků do video/ (taky přes browserless)
TEMA ?= seniori
video:
	@python3 tools/video.py $(TEMA)

## Videa, která jsou na webu u sekcí programu — zmenšená kopie a náhled.
## Která to jsou, říká src/data/videa.json.
videa-web:
	@python3 tools/video.py --web $$(python3 -c "import json;print(' '.join(v['soubor'] for v in json.load(open('src/data/videa.json'))['videa']))")

## Všechna témata programu: hlas z textu a z něj video.
## Mluvení je placené, takže se přeskakuje, co už hlas má — viz tools/hlas.py.
videa:
	@python3 tools/hlas.py --sluzba openai
	@python3 tools/video.py $$(python3 -c "import json;print(' '.join(json.load(open('src/data/video-temata.json'))['temata']))")

## Ikony sekcí programu do src/data/ikony.json
ikony:
	@python3 tools/ikony.py

## Přesměrování kandidat1…10.volbats.cz na medailonky, každé jako vlastní
## repozitář na GitHub Pages (viz hlavička tools/aliasy.py)
aliasy:
	@python3 tools/aliasy.py --nasadit

clean:
	@rm -rf dist dist-ssr letak.pdf letak.html plakaty qr socialni video aliasy
