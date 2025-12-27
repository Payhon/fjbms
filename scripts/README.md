# DevOps scripts

This folder contains Python-based operational scripts, driven via the repository root `Makefile`.

## Setup

1. Copy configs:
   - `scripts/config/test.example.yml` -> `scripts/config/test.yml`
   - `scripts/config/prod.example.yml` -> `scripts/config/prod.yml`
2. Fill in hosts/paths/users. Keep secrets in environment variables (recommended by config via `*_env` keys).
3. Ensure SSH key login works (and `sudo` is passwordless if you enable `use_sudo: true`).
4. Keep `remote_tmp_dir` writable by the SSH user (upload happens via SFTP, not sudo).

## Common commands

- `make build-frontend`
- `make build-backend`
- `make deploy-frontend-test`
- `make deploy-frontend-prod`
- `make deploy-backend-test`
- `make deploy-backend-prod`
- `make export-sql-test`
- `make export-sql-prod`
- `make import-sql ENV=test SQL=./some.sql`
