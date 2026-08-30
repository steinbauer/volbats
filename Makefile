# Volba pro město Trhové Sviny — statický web
#
#   make url        adresa, na které web běží (kontejner nastartuje sám)
#   make run-dev    nastartuje kontejner
#   make stop-dev   zastaví ho
#   make mirror     znovu stáhne kopii z ostrého volbats.cz

# Větev určuje adresu; lomítka ve větvi doména neunese, tak jdou na pomlčky.
BRANCH_NAME ?= $(shell git rev-parse --abbrev-ref HEAD 2>/dev/null | tr '/' '-')
SITE        ?= site
COMPOSE      = BRANCH_NAME=$(BRANCH_NAME) docker compose
URL          = https://$(BRANCH_NAME).volbats.kamil.lab.home/

.PHONY: url run-dev stop-dev restart-dev status logs mirror

## Vypíše adresu a zajistí, že kontejner běží
url: run-dev
	@echo ""
	@echo "  $(URL)"
	@echo ""

run-dev:
	@$(COMPOSE) up -d --quiet-pull
	@# Traefik si kontejner musí nejdřív všimnout, jinak první request spadne na 404
	@for i in 1 2 3 4 5 6 7 8 9 10; do \
		curl -sk -o /dev/null -w '' --max-time 3 $(URL) && break || sleep 1; \
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

## Pozor: smaže a přepíše celý adresář site/ obsahem z ostrého webu
mirror:
	@./tools/mirror.sh $(SITE)
