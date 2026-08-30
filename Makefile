# Volba pro město Trhové Sviny — React + Vite, statický výstup
#
#   make url        adresa, na které web běží (build i kontejner sám naskočí)
#   make dev        vývojový server s hot reloadem
#   make build      sestaví web do dist/
#   make stop-dev   zastaví kontejner

# Větev určuje adresu; lomítka ve větvi doména neunese, tak jdou na pomlčky.
BRANCH_NAME ?= $(shell git rev-parse --abbrev-ref HEAD 2>/dev/null | tr '/' '-')
COMPOSE      = BRANCH_NAME=$(BRANCH_NAME) docker compose
URL          = https://$(BRANCH_NAME).volbats.kamil.lab.home/

# npm v tomhle prostředí běží s NODE_ENV=production a bez tohohle by
# přeskočil devDependencies, tedy i samotné Vite.
NPM = NODE_ENV=development npm

.PHONY: url dev build install run-dev stop-dev restart-dev status logs clean

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

clean:
	@rm -rf dist dist-ssr
