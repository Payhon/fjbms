# FEAT-0023 bms-bridge 测试/生产部署脚本补充 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-03-23
- related_feature: FEAT-0023
- version: v0.1.0

## 1. 设计概览
- 保持现有 `scripts/devops.py` 为唯一部署编排入口，在其上新增 `bridge` target，而不是新建平行脚本。
- `bridge` 与 `backend` 共用 SSH、SFTP、远端备份、temp 启停、systemd 安装 helper。
- `bridge` 单独维护自己的：
  - 远端二进制路径
  - 远端配置文件路径
  - 日志文件
  - pid 文件
  - systemd 服务名
- `bridge` 部署时同步整个 `backend/configs/` 目录，但不处理 `backend/sql/`。

## 2. 接口与配置调整
- `scripts/devops.py`
  - 新增 `build_bridge(goos, goarch)`
  - 新增 `deploy_bridge(...)`
  - 新增 `update_bridge(...)`
  - 新增 `restart_bridge(...)`
  - CLI 新增 `bridge` 子命令分支
- `scripts/config/test.example.yml` / `prod.example.yml`
  - 新增 `bridge` 顶层配置段
  - 字段与 `backend` 尽量对齐，降低维护心智负担
  - 若真实环境配置暂未补 `bridge` 段，运行时允许从 `backend` 配置推导 bridge 默认路径与 systemd 命名，避免现网配置立即失效

## 3. 部署行为
- `deploy bridge`
  - 编译或复用本地 `backend/bin/bms-bridge`
  - 备份远端旧 bridge 二进制
  - 上传并覆盖 bridge 二进制
  - 上传并替换远端 `configs/` 目录
  - 上传指定 bridge 配置文件
  - 按 `start_mode` 执行 temp 启动或 systemd 安装/重启
- `update bridge`
  - 只上传新的 bridge 二进制
  - 同步指定 bridge 配置文件
  - 不上传 SQL
  - 按 `start_mode` 进行 bridge 重启

## 4. 命名约定
- 本地桥接构建产物：`backend/bin/bms-bridge`
- 测试环境默认路径示例：
  - 二进制：`/opt/fjbms/backend/bms-bridge/bms-bridge`
  - 配置：`/opt/fjbms/backend/bms-bridge/config.yml`
- 生产环境默认路径示例：
  - 二进制：`/www/fjia/fjbms/backend/bms-bridge/bms-bridge`
  - 配置：`/www/fjia/fjbms/backend/bms-bridge/config.yml`
- 生产环境默认 systemd 服务名：`fjbms-bms-bridge`

## 5. 验证策略
- 使用 `python3 -m py_compile scripts/devops.py` 做脚本语法校验。
- 使用 `make help` 校验 Makefile 入口可见性。
- 使用 `make deploy-bridge-test GOOS=linux GOARCH=amd64` 验证本地构建链路。
- 使用 CLI `--help` 验证 `bridge` 子命令已注册。
