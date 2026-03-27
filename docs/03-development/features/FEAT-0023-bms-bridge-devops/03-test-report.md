# FEAT-0023 bms-bridge 测试/生产部署脚本补充 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-03-23
- related_feature: FEAT-0023
- version: v0.1.0

## 1. 测试范围
- `scripts/devops.py` 的 bridge 子命令注册与脚本语法。
- `Makefile` 的 bridge 公开入口。
- `bms-bridge` 本地构建产物输出。
- bridge 部署流程不会触发 SQL 上传的行为约束。
- 真实 `scripts/config/test.yml` / `prod.yml` 缺少 `bridge` 段时的兼容性。

## 2. 已执行验证
- [x] `python3 -m py_compile scripts/devops.py`
- [x] `make help`
- [x] `python3 scripts/devops.py build bridge --help`
- [x] `python3 scripts/devops.py deploy --help`
- [x] `python3 scripts/devops.py update --help`
- [x] `python3 scripts/devops.py restart --help`
- [x] `make restart-bridge-test -n`
- [x] `make restart-bridge-prod -n`
- [x] `python3 scripts/devops.py build bridge --goos linux --goarch amd64`
- [x] 使用真实 `scripts/config/test.yml` / `prod.yml` 验证 bridge 配置可从 `backend` 推导
- [x] `cd backend && go test ./internal/service -run TestAuthMQTTRequest -v`
- [x] 在 `1.95.190.254` 验证 `server-bms-bridge` 被前置 HTTP 认证器错误 `deny` 的根因
- [x] 在 `1.95.190.254` 验证 HTTP 返回 `ignore` / built-in 优先后，`server-bms-bridge` 可成功连接 EMQX
- [x] `python3 -m py_compile scripts/devops.py`
- [x] 校验 bridge 本地配置选择结果：
  - `test -> backend/configs/conf-test.yml`
  - `prod -> backend/configs/conf-prod.yml`（若缺失则回退 `backend/configs/conf.yml`）
- [ ] 远端验证：
  - [ ] 测试环境首次部署完成 bridge 备份、上传、配置落盘与 temp 启动
  - [ ] 生产环境首次部署完成 systemd 安装/重启
  - [ ] `update-bridge-*` 仅替换 bridge 二进制与配置，不触发 SQL 上传

## 3. 当前结论
- 本地语法与入口校验通过，`bms-bridge` 构建链路可用。
- 已确认测试环境 bridge 进程、EMQX 认证链与客户端连通性问题，根因为 HTTP 认证器对非设备类客户端返回 `deny`。
- `api/v1/mqtt/auth` 修复后，可避免 EMQX 认证顺序导致服务端 MQTT 客户端被误拒绝。
