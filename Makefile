.PHONY: help devops-venv \
	build-frontend build-backend \
	deploy-frontend-test deploy-frontend-prod \
	deploy-backend-test deploy-backend-prod \
	update-frontend-test update-frontend-prod \
	update-backend-test update-backend-prod \
	restart-backend-test \
	export-sql-test export-sql-prod \
	import-sql

PY_VENV := scripts/.venv
PY := $(PY_VENV)/bin/python
PIP := $(PY_VENV)/bin/pip

GOOS ?= linux
GOARCH ?= amd64
SERVICE_ENV ?= prod

help:
	@echo "DevOps targets:"
	@echo "  make build-frontend"
	@echo "  make build-backend [GOOS=linux GOARCH=amd64]"
	@echo "  make deploy-frontend-test"
	@echo "  make deploy-frontend-prod"
	@echo "  make deploy-backend-test [GOOS=linux GOARCH=amd64]"
	@echo "  make deploy-backend-prod [GOOS=linux GOARCH=amd64]"
	@echo "  make update-frontend-test"
	@echo "  make update-frontend-prod"
	@echo "  make update-backend-test [GOOS=linux GOARCH=amd64]"
	@echo "  make update-backend-prod [GOOS=linux GOARCH=amd64]"
	@echo "  make restart-backend-test"
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
	@$(PY) scripts/devops.py build frontend --service-env "$(SERVICE_ENV)"

build-backend: devops-venv
	@$(PY) scripts/devops.py build backend --goos "$(GOOS)" --goarch "$(GOARCH)"

deploy-frontend-test: devops-venv
	@$(PY) scripts/devops.py build frontend --service-env test
	@$(PY) scripts/devops.py deploy --env test frontend --service-env test --skip-build

deploy-frontend-prod: devops-venv
	@$(PY) scripts/devops.py build frontend --service-env prod
	@$(PY) scripts/devops.py deploy --env prod frontend --service-env prod --skip-build

deploy-backend-test: devops-venv
	@$(PY) scripts/devops.py build backend --goos "$(GOOS)" --goarch "$(GOARCH)"
	@$(PY) scripts/devops.py deploy --env test backend --goos "$(GOOS)" --goarch "$(GOARCH)" --skip-build

deploy-backend-prod: devops-venv
	@$(PY) scripts/devops.py build backend --goos "$(GOOS)" --goarch "$(GOARCH)"
	@$(PY) scripts/devops.py deploy --env prod backend --goos "$(GOOS)" --goarch "$(GOARCH)" --skip-build

update-frontend-test: devops-venv
	@$(PY) scripts/devops.py build frontend --service-env test
	@$(PY) scripts/devops.py update --env test frontend --service-env test --skip-build

update-frontend-prod: devops-venv
	@$(PY) scripts/devops.py build frontend --service-env prod
	@$(PY) scripts/devops.py update --env prod frontend --service-env prod --skip-build

update-backend-test: devops-venv
	@$(PY) scripts/devops.py build backend --goos "$(GOOS)" --goarch "$(GOARCH)"
	@$(PY) scripts/devops.py update --env test backend --goos "$(GOOS)" --goarch "$(GOARCH)" --skip-build

update-backend-prod: devops-venv
	@$(PY) scripts/devops.py build backend --goos "$(GOOS)" --goarch "$(GOARCH)"
	@$(PY) scripts/devops.py update --env prod backend --goos "$(GOOS)" --goarch "$(GOARCH)" --skip-build

restart-backend-test: devops-venv
	@$(PY) scripts/devops.py restart --env test backend

export-sql-test: devops-venv
	@$(PY) scripts/devops.py db --env test export

export-sql-prod: devops-venv
	@$(PY) scripts/devops.py db --env prod export

import-sql: devops-venv
	@test -n "$(ENV)" || (echo "Missing ENV=test|prod" && exit 2)
	@test -n "$(SQL)" || (echo "Missing SQL=path/to/file.sql" && exit 2)
	@$(PY) scripts/devops.py db --env "$(ENV)" import --sql "$(SQL)"
