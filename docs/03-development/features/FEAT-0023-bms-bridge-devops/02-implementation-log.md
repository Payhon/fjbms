# FEAT-0023 bms-bridge 测试/生产部署脚本补充 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-03-23
- related_feature: FEAT-0023
- version: v0.1.0

## 日志
1. 2026-03-23 现状确认
   - 已确认根目录 `Makefile` 与 `scripts/devops.py` 仅支持 `frontend/backend` 两类部署目标。
   - 已确认 `backend/cmd/bms-bridge` 为独立二进制，且 `backend/configs/conf*.yml` 中已包含 `bms_bridge` 配置段。
2. 2026-03-23 DevOps 脚本扩展
   - `scripts/devops.py` 已新增 `build_bridge()`，输出 `backend/bin/bms-bridge`。
   - 已新增 `deploy_bridge()`、`update_bridge()`、`restart_bridge()`。
   - `bridge` 部署链路复用现有 SSH、备份、temp 启停、systemd 安装逻辑。
   - `bridge` 部署不会上传 `backend/sql/`。
3. 2026-03-23 Makefile 入口补充
   - 已新增：
     - `deploy-bridge-test`
     - `deploy-bridge-prod`
     - `update-bridge-test`
     - `update-bridge-prod`
     - `restart-bridge-test`
     - `restart-bridge-prod`
4. 2026-03-23 环境配置示例补充
   - `scripts/config/test.example.yml` 已新增 `bridge` 配置段，默认 `start_mode: temp`。
   - `scripts/config/prod.example.yml` 已新增 `bridge` 配置段，默认 `start_mode: systemd`，服务名为 `fjbms-bms-bridge`。
5. 2026-03-23 配置兼容修复
   - 已兼容真实 `scripts/config/test.yml` / `prod.yml` 尚未显式配置 `bridge` 段的场景。
   - 当 `bridge` 缺失时，运行时会从 `backend` 配置自动推导 bridge 的远端路径、配置路径、日志路径与 systemd 命名。
6. 2026-03-23 文档治理回写
   - 已新增 FEAT-0023 功能文档集。
   - 已更新项目看板，新增 FEAT-0023 条目。
7. 2026-03-23 MQTT 认证兼容修复
   - 已修正 `api/v1/mqtt/auth` 对非设备类 MQTT 客户端的处理逻辑。
   - 当 HTTP 认证接口无法识别为平台受管设备时，接口返回 `ignore`，不再错误返回 `deny`。
   - 该修复避免 `bms-bridge` 等服务端 MQTT 客户端因 EMQX 认证链顺序而被前置 HTTP 认证器拦截。
8. 2026-03-23 bridge 本地配置文件选择优化
   - `deploy-bridge-*` / `update-bridge-*` 覆盖远端配置时，已改为按环境优先选择本地配置文件。
   - 选择顺序为：`backend/configs/conf-{env}.yml` -> `backend/configs/conf.yml`。
   - 该逻辑不再隐式继承 `backend.local_config_path`，避免生产环境误把 `conf.yml` 提前覆盖到 bridge。
