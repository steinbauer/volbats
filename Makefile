# Volba pro město Trhové Sviny — React + Vite, statický výstup
#
#   make url        vypíše adresy, na kterých web běží
#   make run-dev    připraví .env i override, sestaví web a nastartuje kontejner
#   make dev        vývojový server s hot reloadem
#   make build      sestaví web do dist/
#   make letak      vyrobí volební leták jako PDF
#   make stop-dev   zastaví kontejner

# Větev určuje adresu; lomítka ve větvi doména neunese, tak jdou na pomlčky.
BRANCH_NAME ?= $(shell git rev-parse --abbrev-ref HEAD 2>/dev/null | tr '/' '-')
COMPOSE      = BRANCH_NAME=$(BRANCH_NAME) docker compose

# Lab proměnné: přednost má vygenerovaný .env, jinak se vezme ~/.lab.env.
LAB_DOMAIN  ?= $(shell grep -h '^LAB_DOMAIN=.' .env $(HOME)/.lab.env 2>/dev/null | head -1 | cut -d= -f2)
LAB_USER    ?= $(shell grep -h '^LAB_USER=.' .env $(HOME)/.lab.env 2>/dev/null | head -1 | cut -d= -f2)
URL          = https://$(BRANCH_NAME).volbats.me.$(LAB_DOMAIN)/

# npm v tomhle prostředí běží s NODE_ENV=production a bez tohohle by
# přeskočil devDependencies, tedy i samotné Vite.
NPM = NODE_ENV=development npm

.PHONY: url dev build install run-dev stop-dev restart-dev status logs letak clean

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
	@if [ ! -f compose.override.yaml ] && [ -f compose.override.yaml.example ]; then \
		cp compose.override.yaml.example compose.override.yaml; \
	fi; \
	if [ ! -f .env ] && [ -f .env.example ]; then \
		cp .env.example .env; \
	fi; \
	BRANCH_NAME=$$(git rev-parse --abbrev-ref HEAD | sed 's/[^a-zA-Z0-9-]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$$//'); \
	if [ -f .env ]; then \
		if grep -q '^BRANCH_NAME=' .env; then \
			sed -i "s/^BRANCH_NAME=.*/BRANCH_NAME=$$BRANCH_NAME/" .env; \
		else \
			printf '\nBRANCH_NAME=%s\n' "$$BRANCH_NAME" >> .env; \
		fi; \
	else \
		echo "BRANCH_NAME=$$BRANCH_NAME" > .env; \
	fi; \
	echo "    BRANCH_NAME=$$BRANCH_NAME"; \
	if [ -f ~/.lab.env ]; then \
		for KEY in LAB_USER LAB_DOMAIN; do \
			grep -q "^$$KEY=." .env 2>/dev/null && continue; \
			VAL=$$(grep -oP "^$$KEY=\\K\\S+" ~/.lab.env 2>/dev/null | head -1); \
			[ -z "$$VAL" ] && continue; \
			if grep -q "^$$KEY=" .env 2>/dev/null; then \
				sed -i "s|^$$KEY=.*|$$KEY=$$VAL|" .env; \
			else \
				echo "$$KEY=$$VAL" >> .env; \
			fi; \
		done; \
	fi; \
	LAB_DOMAIN_VAL=$$(grep -oP 'LAB_DOMAIN=\K\S+' .env 2>/dev/null); \
	DOMAIN_VAL="$$BRANCH_NAME.volbats.me.$$LAB_DOMAIN_VAL"; \
	if grep -q '^DOMAIN=' .env 2>/dev/null; then \
		sed -i "s|^DOMAIN=.*|DOMAIN=$$DOMAIN_VAL|" .env; \
	else \
		echo "DOMAIN=$$DOMAIN_VAL" >> .env; \
	fi; \
	echo "    DOMAIN=$$DOMAIN_VAL"; \
	MISSING=""; \
	grep -q '^LAB_USER=.' .env 2>/dev/null || MISSING="$$MISSING LAB_USER"; \
	grep -q '^LAB_DOMAIN=.' .env 2>/dev/null || MISSING="$$MISSING LAB_DOMAIN"; \
	if [ -n "$$MISSING" ]; then echo "Chyba: V .env chybi:$$MISSING (vloz do ~/.lab.env)"; exit 1; fi; \
	if [ -f package.json ] && [ ! -d node_modules ]; then \
		echo "==> node_modules/ chybi, spoustim npm install..."; \
		$(NPM) install --no-audit --no-fund --include=dev; \
	fi; \
	if [ ! -f dist/index.html ]; then \
		echo "==> dist/ chybi, sestavuji web..."; \
		$(NPM) run build; \
	fi; \
	docker network create proxy 2>/dev/null || true; \
	docker compose up -d --quiet-pull; \
	printf '==> Cekam, az si traefik kontejneru vsimne'; \
	for i in 1 2 3 4 5 6 7 8 9 10; do \
		curl -sk -o /dev/null --max-time 3 "https://$$DOMAIN_VAL/" && break || { printf '.'; sleep 1; }; \
	done; \
	echo ""; \
	echo ""; \
	echo "Dev prostredi je pripraveno!"; \
	LAB_USER2=$$(grep -oP 'LAB_USER=\K\S+' .env 2>/dev/null); \
	echo "   - App: https://$$BRANCH_NAME.volbats.me.$$LAB_DOMAIN_VAL"; \
	echo "   - App: https://$$BRANCH_NAME.volbats.$$LAB_USER2.$$LAB_DOMAIN_VAL"

url:
	@BRANCH_NAME=$$(grep -oP 'BRANCH_NAME=\K\S+' .env 2>/dev/null); \
	LAB_USER=$$(grep -oP 'LAB_USER=\K\S+' .env 2>/dev/null); \
	LAB_DOMAIN=$$(grep -oP 'LAB_DOMAIN=\K\S+' .env 2>/dev/null); \
	echo "   - App: https://$$BRANCH_NAME.volbats.me.$$LAB_DOMAIN"; \
	echo "   - App: https://$$BRANCH_NAME.volbats.$$LAB_USER.$$LAB_DOMAIN"

stop-dev:
	@echo "==> Zastavuji Docker kontejnery..."
	docker compose down
	@echo "Kontejnery zastaveny"

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

clean:
	@rm -rf dist dist-ssr letak.pdf letak.html
