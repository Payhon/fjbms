# FEAT-0041 UniApp OTA 地址口径统一与仪表会话升级支持 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-07-25
- related_feature: FEAT-0041
- version: v0.4.0

## 1. 已执行验证
- [x] 2026-04-15 历史验证：`cd fjbms-uniapp && pnpm exec tsc --noEmit`
- [x] 2026-04-15 历史验证：`cd backend && go test ./internal/service/...`
- [x] 2026-06-29 本次验证：`cd fjbms-uniapp && pnpm exec tsc --noEmit`
- [x] 2026-06-29 本次验证：`cd fjbms-uniapp && git diff --check -- pages/device-battery/detail.vue`
- [x] 2026-06-29 本次验证：`git diff --check -- docs/03-development/features/FEAT-0041-uniapp-ota-addressing-and-instrument-session docs/04-project-tracking/board.md`
- [x] 2026-06-30 本次验证：`cd fjbms-uniapp && pnpm exec tsc --noEmit`
- [x] 2026-06-30 本次验证：`cd fjbms-uniapp && git diff --check -- pages/device-battery/detail.vue pages/device-battery/useBatteryDetail.ts lang/zh-CN.ts lang/en-US.ts`
- [x] 2026-06-30 本次验证：`git diff --check -- docs/03-development/features/FEAT-0041-uniapp-ota-addressing-and-instrument-session docs/04-project-tracking/board.md`
- [ ] 手工验证仪表 / BMS OTA 升级
- [ ] 真机验证有线仪表读到 BMS 状态后隐藏“仪表临时连接”提示
- [ ] 真机验证有线仪表未接 BMS 时约 10 秒后返回主面板并显示“仪表临时连接”提示
- [ ] 真机验证蓝牙透传型仪表无法读取 BMS 状态后仍提示继续扫码绑定 BMS
- [x] 自动化验证 9999ms/10000ms 边界、成功优先和非仪表会话隔离

## 2. 验证结果
- 2026-04-15 历史验证：`cd fjbms-uniapp && pnpm exec tsc --noEmit`
  - 结果：通过。
- 2026-04-15 历史验证：`cd backend && go test ./internal/service/...`
  - 结果：通过。
  - 备注：存在 `gopsutil/disk` 的 macOS `IOMasterPort` 弃用编译告警，不影响测试通过。
- 2026-06-29 本次验证：`cd fjbms-uniapp && pnpm exec tsc --noEmit`
  - 结果：通过。
- 2026-06-29 本次验证：`cd fjbms-uniapp && git diff --check -- pages/device-battery/detail.vue`
  - 结果：通过。
- 2026-06-29 本次验证：`git diff --check -- docs/03-development/features/FEAT-0041-uniapp-ota-addressing-and-instrument-session docs/04-project-tracking/board.md`
  - 结果：通过。
- 2026-06-30 本次验证：`cd fjbms-uniapp && pnpm exec tsc --noEmit`
  - 结果：通过。
- 2026-06-30 本次验证：`cd fjbms-uniapp && git diff --check -- pages/device-battery/detail.vue pages/device-battery/useBatteryDetail.ts lang/zh-CN.ts lang/en-US.ts`
  - 结果：通过。
- 2026-06-30 本次验证：`git diff --check -- docs/03-development/features/FEAT-0041-uniapp-ota-addressing-and-instrument-session docs/04-project-tracking/board.md`
  - 结果：通过。
- 2026-07-25 本次验证：`cd fjbms-uniapp && pnpm exec tsc --noEmit --project tsconfig.json`
  - 结果：通过。
- 2026-07-25 本次验证：将仪表等待策略、详情轮询策略和数据仲裁测试临时编译为 CommonJS 后使用 Node 执行
  - 结果：通过。
  - 覆盖：9999ms 继续等待、10000ms 到期、状态成功优先、云端/MQTT 隔离，以及既有详情轮询和迟到数据仲裁。
- 2026-07-25 本次验证：`cd fjbms-uniapp && git diff --check`
  - 结果：通过。

## 3. 本次待真机验收
- 微信小程序、iOS、Android：未接下级 BMS 时从开始读取到提示出现约 10 秒。
- 10 秒内成功回包时正常展示仪表盘，不出现临时连接提示。
- 临界和迟到回包不造成 loading、仪表盘、扫码提示反复切换。
- 人工重新读取、重新连接、新会话和页面退出后不存在旧计时器回写。
