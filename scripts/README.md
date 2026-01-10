# DevOps scripts

This folder contains Python-based operational scripts, driven via the repository root `Makefile`.

## Setup

1. Copy configs:
   - `scripts/config/test.example.yml` -> `scripts/config/test.yml`
   - `scripts/config/prod.example.yml` -> `scripts/config/prod.yml`
2. Fill in hosts/paths/users. Keep secrets in environment variables (recommended by config via `*_env` keys).
3. Configure SSH password login via `ssh.auth: password` + `ssh.password_env` (or `ssh.password`, not recommended).
4. If you enable `use_sudo: true`, ensure passwordless sudo is configured (scripts use `sudo -n`).
5. Keep `remote_tmp_dir` writable by the SSH user (upload happens via SFTP, not sudo).

## Backend deploy (binary + config + log)

Backend deploy supports 2 modes:

1. `restart_command` mode: upload binary/config, then run your restart command (e.g. systemd).
2. Direct-run mode (default if `restart_command` is empty): stops the old process (pid file), then runs:
   - `<remote_binary_path> -config <remote_config_path>`
   - stdout/stderr appended to `backend.remote_log_file`
   - pid written to `backend.remote_pid_file`

`backend.local_config_path` can point to an existing repo file like `backend/configs/conf-dev.yml` or your own local-only config file.

## Backend deploy (test vs prod)

- `make deploy-backend-test`: defaults to `backend.start_mode: temp` (nohup).
- `make deploy-backend-prod`: defaults to `backend.start_mode: systemd` and uploads a remote installer script (see `backend.systemd.*`).

## Upload configs/sql

`make deploy-backend-*` also uploads:
- `backend.local_configs_dir` -> `backend.remote_configs_dir`
- `backend.local_sql_dir` -> `backend.remote_sql_dir`

## Common commands

- `make build-frontend`
- `make build-backend`
- `make deploy-frontend-test`
- `make deploy-frontend-prod`
- `make deploy-backend-test`
- `make deploy-backend-prod`
- `make update-frontend-test`
- `make update-frontend-prod`
- `make update-backend-test`
- `make update-backend-prod`
- `make export-sql-test`
- `make export-sql-prod`
- `make import-sql ENV=test SQL=./some.sql`

## Update (fast path)

- `make update-backend-test|prod`: only updates the backend binary and restarts (temp/systemd by `backend.start_mode`), and does NOT upload `configs/sql` directories.
- `make update-frontend-test|prod`: only updates frontend `dist` and overwrites the remote target directory.

## Console feedback

By default the scripts print:
- which remote command is executed
- remote stdout/stderr (truncated when very long)

To reduce output, add `--quiet` when running `scripts/devops.py` directly.

## 导出本地 SQL
```shell
cd ~/project/work2025/project/fjbms
docker exec -t -e PGPASSWORD=postgres thingspanel-postgres pg_dump -U postgres -d ThingsPanel > ./tp-all.sql
```
## 导入 SQL

```shell
cd ~/project/work2025/project/fjbms
docker run --rm -i \
  -e PGPASSWORD='pgRootPwd@2025' \
  -v "$(pwd)/tp-all.sql:/backup.sql:ro" \
  timescale/timescaledb:latest-pg14 \
  psql -h 1.95.190.254 -p 5432 -U postgres -d fjbms -f /backup.sql
```
