# FEAT-0023 bms-bridge 测试/生产部署脚本补充 - 功能规格

- status: in_progress
- owner: payhon
- last_updated: 2026-03-23
- related_feature: FEAT-0023
- version: v0.1.0

## 1. 背景与目标
- 背景：
  - 仓库根目录已有 `Makefile + scripts/devops.py + scripts/config/{test,prod}.yml` 的前后端部署体系。
  - `backend/cmd/bms-bridge` 已是独立二进制，但当前没有测试/生产环境的独立部署与更新入口。
  - 直接复用 `deploy-backend-*` 会把主服务二进制、SQL 目录等行为错误绑定到 `bms-bridge`。
- 目标：
  1. 为 `bms-bridge` 提供独立的测试/生产部署入口。
  2. 为 `bms-bridge` 提供独立的测试/生产更新入口。
  3. 为 `bms-bridge` 提供独立的测试/生产远端重启入口。
  4. 保持目录结构、配置命名和 systemd 约定与现有 `backend` DevOps 体系一致。

## 2. 范围
### In Scope
- 扩展 `scripts/devops.py`，新增 `build/deploy/update/restart bridge` 子命令。
- 扩展根目录 `Makefile`，新增 4 个公开命令：
- 扩展根目录 `Makefile`，新增 6 个公开命令：
  - `deploy-bridge-test`
  - `deploy-bridge-prod`
  - `update-bridge-test`
  - `update-bridge-prod`
  - `restart-bridge-test`
  - `restart-bridge-prod`
- 扩展 `scripts/config/test.example.yml` 与 `scripts/config/prod.example.yml`，新增 `bridge` 配置段。
- 新增 FEAT-0023 文档并同步项目看板。

### Out of Scope
- 不修改现有 `deploy-backend-*` / `update-backend-*` 行为。
- 不新增数据库发布、SQL 上传或前端发布能力到 `bms-bridge` 流程。
- 不修改 `backend/configs/conf*.yml` 中 `bms_bridge` 业务配置结构。

## 3. 验收标准
1. `scripts/devops.py` 支持：
   - `build bridge`
   - `deploy --env {test|prod} bridge`
   - `update --env {test|prod} bridge`
   - `restart --env {test|prod} bridge`
2. `make help` 中可见 6 个新的 bridge 目标。
3. `make deploy-bridge-test GOOS=linux GOARCH=amd64` 的本地构建阶段可产出 `backend/bin/bms-bridge`。
4. `bridge` 部署流程只上传 bridge 二进制、共享 `backend/configs/` 目录和指定配置文件，不上传 `backend/sql/`。
5. 测试环境默认支持 `temp` 启动，生产环境默认支持 `systemd` 启动。

## 4. 风险与约束
- `bms-bridge` 运行依赖 `backend/configs/` 下共享资源，若远端未同步该目录，服务可能因缺失规则文件或密钥文件而启动失败。
- 如果将 `bridge` 错误并入 `backend` 发布链路，可能引入 SQL 上传或主服务重启的副作用。
- 远端路径与 systemd service name 采用示例值，实际部署仍需在 `scripts/config/{test,prod}.yml` 中填写真实配置。
- bridge 覆盖远端配置文件时，本地优先读取 `backend/configs/conf-{env}.yml`，若不存在再回退到 `backend/configs/conf.yml`。

## 5. 回滚方案
- 回滚 `Makefile`、`scripts/devops.py` 与 `scripts/config/*.example.yml` 中的 FEAT-0023 改动。
- 删除 FEAT-0023 文档目录并回退看板条目。
- 若远端已安装 bridge systemd unit，则按运维流程停用并恢复旧版 bridge 发布方式。
