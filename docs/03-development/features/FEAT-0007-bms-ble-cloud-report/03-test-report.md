# FEAT-0007 蓝牙 BMS 经 App 上云 + 后台 BMS 实时/历史可视化 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-03-09
- related_feature: FEAT-0007
- version: v0.2.1

## 1. 测试范围
- 后端接口编译与基础单测回归。
- Web/UniApp 代码级联调准备（静态检查与关键路径自检）。

## 2. 已执行
- [x] `cd backend && go test ./...`（关键模块通过，存在历史环境依赖失败）
  - 通过：`internal/service`、`internal/api`、`router/apps` 等包
  - 失败：`backend/test/pg_test.go` 依赖本地 DB 环境（`run_env=localdev`），与本次改动无直接耦合
- [x] `cd backend && go test ./internal/service ./internal/api ./router/apps`
  - 结果：通过（含 Relay 相关编译校验）
- [x] `cd backend && go test ./internal/service -run "TestNormalizeAppBattery" -count=1`
  - 结果：通过（覆盖本次改动涉及的 APP 上报核心校验单测）
- [x] `cd backend && go test ./internal/api ./router/apps -run TestDoesNotExist -count=1`
  - 结果：通过（用于验证 API/路由包编译通过）
- [x] `cd frontend && pnpm typecheck`
  - 结果：通过
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit`
  - 结果：通过

## 3. 待执行（联调阶段）
- [ ] Android + BLE：5s 内后台显示实时值，历史曲线可查
- [ ] iOS + BLE：断网后重连补传队列生效
- [ ] 微信小程序：非 BLE 场景走 WS 桥接可读状态
- [ ] BLE-only 设备：WEB 端参数读写通过 APP Relay 成功执行
- [ ] 多用户同设备：仅当前 BLE owner 的 APP 会话收到并执行 WEB 命令
- [ ] 多端同设备连接态：A 端断开且 B 端仍连接时，不应误置离线
- [ ] BLE 主动断开：后台列表/看板在线数在 <5s 内更新为离线
- [ ] 后台参数设置回归：直连读写功能不回退
- [ ] 权限回归：未绑定/跨租户用户无法上报

## 4. 风险与阻塞
- 本地完整回归需要可用的测试数据库配置（`conf-localdev.yml`）。
- Web 与 UniApp 端需真机联调验证跨端传输差异（尤其微信小程序网络栈）。

## 5. 结论
- 当前进入联调测试阶段，代码改动已完成主要实现，待执行端到端验收用例。
