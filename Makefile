.PHONY: help devops-venv \
	build-frontend build-backend \
	deploy-frontend-test deploy-frontend-prod \
	deploy-backend-test deploy-backend-prod \
	export-sql-test export-sql-prod \
	import-sql

PY_VENV := scripts/.venv
PY := $(PY_VENV)/bin/python
PIP := $(PY_VENV)/bin/pip

GOOS ?= linux
GOARCH ?= amd64

help:
	@echo "DevOps targets:"
	@echo "  make build-frontend"
	@echo "  make build-backend [GOOS=linux GOARCH=amd64]"
	@echo "  make deploy-frontend-test"
	@echo "  make deploy-frontend-prod"
	@echo "  make deploy-backend-test [GOOS=linux GOARCH=amd64]"
	@echo "  make deploy-backend-prod [GOOS=linux GOARCH=amd64]"
	@echo "  make export-sql-test"
	@echo "  make export-sql-prod"
	@echo "  make import-sql ENV=test SQL=path/to/file.sql"
	@echo ""
	@echo "Config files:"
	@echo "  scripts/config/test.yml (copy from scripts/config/test.example.yml)"
	@echo "  scripts/config/prod.yml (copy from scripts/config/prod.example.yml)"

devops-venv:
	@test -x "$(PY)" || python3 -m venv "$(PY_VENV)"
	@$(PIP) -q install -r scripts/requirements.txt

build-frontend: devops-venv
	@$(PY) scripts/devops.py build frontend --service-env prod

build-backend: devops-venv
	@$(PY) scripts/devops.py build backend --goos "$(GOOS)" --goarch "$(GOARCH)"

deploy-frontend-test: devops-venv
	@$(PY) scripts/devops.py deploy frontend --env test --service-env test

deploy-frontend-prod: devops-venv
	@$(PY) scripts/devops.py deploy frontend --env prod --service-env prod

deploy-backend-test: devops-venv
	@$(PY) scripts/devops.py deploy backend --env test --goos "$(GOOS)" --goarch "$(GOARCH)"

deploy-backend-prod: devops-venv
	@$(PY) scripts/devops.py deploy backend --env prod --goos "$(GOOS)" --goarch "$(GOARCH)"

export-sql-test: devops-venv
	@$(PY) scripts/devops.py db export --env test

export-sql-prod: devops-venv
	@$(PY) scripts/devops.py db export --env prod

import-sql: devops-venv
	@test -n "$(ENV)" || (echo "Missing ENV=test|prod" && exit 2)
	@test -n "$(SQL)" || (echo "Missing SQL=path/to/file.sql" && exit 2)
	@$(PY) scripts/devops.py db import --env "$(ENV)" --sql "$(SQL)"

