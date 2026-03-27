# FEAT-0023 bms-bridge 测试/生产部署脚本补充 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-03-23
- related_feature: FEAT-0023
- version: v0.1.0

## 发布内容
- 新增 `bms-bridge` 独立构建与部署能力。
- 新增 4 个 Makefile 命令：
- 新增 6 个 Makefile 命令：
  - `deploy-bridge-test`
  - `deploy-bridge-prod`
  - `update-bridge-test`
  - `update-bridge-prod`
  - `restart-bridge-test`
  - `restart-bridge-prod`
- 新增 `scripts/devops.py` 的 `bridge` 子命令。
- 新增测试/生产环境的 `bridge` 示例配置段。
- 修复 `api/v1/mqtt/auth` 对非设备类 MQTT 客户端的返回语义，改为在不属于 HTTP 认证职责范围时返回 `ignore`。
- 优化 bridge 覆盖远端配置时的本地文件选择顺序，按环境优先使用 `conf-{env}.yml`，不存在再回退 `conf.yml`。

## 影响范围
- `Makefile`
- `scripts/devops.py`
- `scripts/config/test.example.yml`
- `scripts/config/prod.example.yml`
- `backend/internal/api/mqtt_http_auth.go`
- `backend/internal/service/mqtt_http_auth.go`
- `scripts/devops.py`
- `docs/` 功能文档与项目看板

## 发布与回滚提示
- 发布前需在 `scripts/config/test.yml` / `prod.yml` 中补齐真实 bridge 远端路径、SSH 与 systemd 配置。
- 首次生产发布建议先执行 `deploy-bridge-prod`，确认 unit 正常安装后再使用 `update-bridge-prod`。
- 若需回滚，可恢复旧版 `bms-bridge` 二进制和配置，并回退 FEAT-0023 对应脚本改动。
