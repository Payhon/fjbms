# 运维脚本使用说明

本目录提供基于 `scripts/devops.py` 的运维脚本入口，统一通过仓库根目录的 `Makefile` 调用。

## 准备工作

1. 初始化脚本依赖：
   - `make devops-venv`
2. 准备配置文件：
   - `scripts/config/test.example.yml` → `scripts/config/test.yml`
   - `scripts/config/prod.example.yml` → `scripts/config/prod.yml`
3. 填写主机、路径、用户信息；敏感信息建议放入环境变量（配置里使用 `*_env`）。
4. SSH 密码登录可用 `ssh.auth: password` + `ssh.password_env`（或 `ssh.password`，不推荐）。
5. 若开启 `use_sudo: true`，请确保目标机已配置免密 sudo（脚本使用 `sudo -n`）。
6. `remote_tmp_dir` 需保证 SSH 用户可写（上传通过 SFTP，非 sudo）。

## 常用命令

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
- `make restart-backend-test`

## 命令说明（非数据库）

### 构建相关

- `make devops-venv`  
  初始化脚本虚拟环境与依赖（`scripts/.venv` + `scripts/requirements.txt`）。

- `make build-frontend`  
  本地构建前端产物（等同 `scripts/devops.py build frontend`）。
  可通过环境变量指定服务环境：`SERVICE_ENV=test|prod`（默认 `prod`）。

- `make build-backend`  
  本地构建后端二进制（等同 `scripts/devops.py build backend`）。
  可通过 `GOOS=linux GOARCH=amd64` 指定目标平台。

### 部署相关

- `make deploy-frontend-test` / `make deploy-frontend-prod`  
  构建前端并上传到测试/生产服务器，覆盖远端目标目录。

- `make deploy-backend-test` / `make deploy-backend-prod`  
  构建后端并上传到测试/生产服务器，包含：
  - 上传后端二进制
  - 上传 `backend/configs` 目录
  - 上传 `backend/sql` 目录
  - 按配置执行重启（测试默认 temp，生产默认 systemd）

### 快速更新

- `make update-frontend-test` / `make update-frontend-prod`  
  仅更新前端产物（不做额外配置同步）。

- `make update-backend-test` / `make update-backend-prod`  
  仅更新后端二进制并重启，不上传 `configs/sql` 目录。

### 重启

- `make restart-backend-test`  
  仅重启测试环境后端服务（按配置的 start_mode 执行）。

### BMS 工具（可选）

- `make build-bms-bridge`  
  构建 `bms-bridge` 二进制（可传 `GOOS/GOARCH`）。

- `make run-bms-bridge`  
  运行 `bms-bridge`，需传 `CONFIG=configs/conf-dev.yml`。

- `make build-bms-sim`  
  构建 `bms-sim` 二进制（可传 `GOOS/GOARCH`）。

- `make run-bms-sim`  
  运行 `bms-sim`，需传 `CONFIG=configs/conf-dev.yml DEVICE_ID=uuid`。

- `make run-bms-gui`  
  启动本地 BMS GUI（会初始化 `tools/bms_mqtt_gui/.venv`）。

## 数据库导出/导入（重点）

### 1) 从测试环境导出完整数据库（本地下载）

命令：
- `make export-db-test`

效果：
- 通过 SSH 在测试环境执行 `pg_dump`/`mysqldump`，并把完整 SQL 直接下载到本地。
- 文件保存目录：`dist/devops/`
- 文件命名格式：`db_test_<dbtype>_<YYYYMMDD_HHMMSS>.sql`
  - 例如：`dist/devops/db_test_postgres_20250205_153000.sql`

### 2) 将测试环境导出的 SQL 导入到生产环境

命令：
- `make import-db-prod`

效果：
- 默认会寻找 `dist/devops/` 下最新的 `db_test_*.sql` 并导入生产环境。
- 如需指定文件，可直接调用脚本：
  - `scripts/devops.py import-db-prod --sql /path/to/file.sql`

### 3) 按序号初始化生产库（导入 backend/sql）

命令：
- `make init-db-prod`

效果：
- 读取 `backend/sql/` 目录下所有 `.sql` 文件，按文件名“数字前缀”顺序依次导入生产环境。
  - 示例顺序：`1.sql, 2.sql, 3.sql, ... 10.sql, 11.sql`
- 需要自定义目录可直接调用脚本：
  - `scripts/devops.py init-db-prod --sql-dir /path/to/sql`

### 4) 通用导出/导入（保留原命令）

- 导出（只导出，不带 test 标签）：
  - `make export-sql-test`
  - `make export-sql-prod`
  - 文件保存目录同样是：`dist/devops/`
  - 文件命名格式：`db_<dbtype>_<YYYYMMDD_HHMMSS>.sql`
- 导入（手工指定 SQL 文件）：
  - `make import-sql ENV=test SQL=/path/to/file.sql`
  - `make import-sql ENV=prod SQL=/path/to/file.sql`

## 导出文件位置汇总

所有导出的数据库文件默认保存在：

- `dist/devops/`

命名规则：

- 测试导出：`db_test_<dbtype>_<YYYYMMDD_HHMMSS>.sql`
- 通用导出：`db_<dbtype>_<YYYYMMDD_HHMMSS>.sql`

## 其他说明

- 远端数据库需安装对应工具：
  - MySQL：`mysqldump`/`mysql`
  - PostgreSQL：`pg_dump`/`psql`
- 如远端未安装上述工具，可在 `scripts/config/*.yml` 中配置：
  - `db.dump_command`：自定义导出命令（可用 `{host} {port} {user} {database}` 占位符）
  - `db.import_command`：自定义导入命令（可用 `{host} {port} {user} {database} {sql}` 占位符）
- 密码环境变量：
  - 测试：`FJBMS_TEST_DB_PASSWORD`
  - 生产：`FJBMS_PROD_DB_PASSWORD`
- SSH 密码环境变量：
  - 测试：`FJBMS_TEST_SSH_PASSWORD`
  - 生产：`FJBMS_PROD_SSH_PASSWORD`

## 附录：本地容器导出/导入示例（可选）

### 导出本地 SQL

```shell
cd ~/project/work2025/project/fjbms
docker exec -t -e PGPASSWORD=postgres thingspanel-postgres pg_dump -U postgres -d ThingsPanel > ./tp-all.sql
```

### 导入 SQL

```shell
cd ~/project/work2025/project/fjbms
docker run --rm -i \
  -e PGPASSWORD='pgRootPwd@2025' \
  -v "$(pwd)/tp-all.sql:/backup.sql:ro" \
  timescale/timescaledb:latest-pg14 \
  psql -h 1.95.190.254 -p 5432 -U postgres -d fjbms -f /backup.sql
```
