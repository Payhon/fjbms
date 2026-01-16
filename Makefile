.PHONY: help devops-venv \
	build-frontend build-backend \
	build-bms-bridge run-bms-bridge \
	build-bms-sim run-bms-sim \
	bms-gui-venv run-bms-gui \
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

BMS_GUI_VENV := tools/bms_mqtt_gui/.venv
BMS_GUI_PY := $(BMS_GUI_VENV)/bin/python
BMS_GUI_PIP := $(BMS_GUI_VENV)/bin/pip

GOOS ?= linux
GOARCH ?= amd64
SERVICE_ENV ?= prod
CONFIG ?= configs/conf-dev.yml

help:
	@echo "DevOps targets:"
	@echo "  make build-frontend"
	@echo "  make build-backend [GOOS=linux GOARCH=amd64]"
	@echo "  make build-bms-bridge [GOOS=linux GOARCH=amd64]"
	@echo "  make run-bms-bridge [CONFIG=configs/conf-dev.yml]"
	@echo "  make build-bms-sim [GOOS=linux GOARCH=amd64]"
	@echo "  make run-bms-sim [CONFIG=configs/conf-dev.yml DEVICE_ID=uuid]"
	@echo "  make run-bms-gui"
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

bms-gui-venv:
	@test -x "$(BMS_GUI_PY)" || python3 -m venv "$(BMS_GUI_VENV)"
	@$(BMS_GUI_PIP) -q install -r tools/bms_mqtt_gui/requirements.txt

run-bms-gui: bms-gui-venv
	@$(BMS_GUI_PY) tools/bms_mqtt_gui/app.py

build-frontend: devops-venv
	@$(PY) scripts/devops.py build frontend --service-env "$(SERVICE_ENV)"

build-backend: devops-venv
	@$(PY) scripts/devops.py build backend --goos "$(GOOS)" --goarch "$(GOARCH)"

build-bms-bridge:
	@cd backend && GOOS="$(GOOS)" GOARCH="$(GOARCH)" CGO_ENABLED=0 \
		go build -trimpath -ldflags "-s -w" -o ./bin/bms-bridge ./cmd/bms-bridge

run-bms-bridge:
	@test -n "$(CONFIG)" || (echo "Missing CONFIG=configs/conf-dev.yml" && exit 2)
	@cd backend && go run ./cmd/bms-bridge -config "./$(CONFIG)"

build-bms-sim:
	@cd backend && GOOS="$(GOOS)" GOARCH="$(GOARCH)" CGO_ENABLED=0 \
		go build -trimpath -ldflags "-s -w" -o ./bin/bms-sim ./cmd/bms-sim

run-bms-sim:
	@test -n "$(CONFIG)" || (echo "Missing CONFIG=configs/conf-dev.yml" && exit 2)
	@test -n "$(DEVICE_ID)" || (echo "Missing DEVICE_ID=uuid" && exit 2)
	@cd backend && go run ./cmd/bms-sim -config "./$(CONFIG)" -device-id "$(DEVICE_ID)" -v

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
