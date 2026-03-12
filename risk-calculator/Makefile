default: run

ROBLOX_ENVIRONMENT := sitetest3
ROBLOX_REGION := us-west-1

QUIET :=
DOCKER_COMPOSE := $(if $(shell command -v docker-compose),docker-compose,docker compose) -f docker-compose.yml

.PHONY: secrets
secrets: templates/out
templates/out: $(wildcard templates/*.env) Makefile
	@$(eval SWARP_ROBLOX_REGION := $(if $(filter sitetest3 sitetest2,$(ROBLOX_ENVIRONMENT)),,--robloxRegion $(ROBLOX_REGION)))
	@(cd ../.. && swarp secrets refresh $(ROBLOX_ENVIRONMENT) $(SWARP_ROBLOX_REGION) || (swarp login $(ROBLOX_ENVIRONMENT) $(SWARP_ROBLOX_REGION) && swarp secrets refresh $(ROBLOX_ENVIRONMENT) $(SWARP_ROBLOX_REGION)))
	@touch templates/out

.PHONY: ensure-env
ensure-env:
	@mkdir -p templates/out
	@touch templates/out/service.env

.PHONY: build
build: ensure-env
	@$(DOCKER_COMPOSE) build $(if $(QUIET),-q,) risk-calculator

.PHONY: start
start: build
	@docker network create grc >/dev/null 2>&1 || true;
	@$(DOCKER_COMPOSE) --progress quiet run --remove-orphans --service-ports --rm risk-calculator

.PHONY: run
run: start

.PHONY: test
test:
	@python -m pytest tests/ -v --tb=short

.PHONY: test-cov
test-cov:
	@python -m pytest tests/ -v --cov=fair_monte_carlo --cov=webapp --cov-report=term-missing

.PHONY: lint
lint:
	@python -m py_compile webapp/app.py
	@python -m py_compile webapp/health.py
	@python -m py_compile fair_monte_carlo/__init__.py
	@echo "Lint checks passed"

.PHONY: clean
clean:
	@$(DOCKER_COMPOSE) down -v --remove-orphans
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	@rm -rf .coverage htmlcov/
