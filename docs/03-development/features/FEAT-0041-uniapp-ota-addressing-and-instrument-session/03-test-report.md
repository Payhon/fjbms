# FEAT-0041 UniApp OTA 地址口径统一与仪表会话升级支持 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-08-31
- related_feature: FEAT-0041
- version: v0.5.0

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

## 4. 2026-08-31 自动恢复回归

以下命令在 `fjbms-uniapp/` 执行：

- [x] `node pages/device-battery/instrument-session-recovery.test.js`：直接执行生产 `useBatteryDetail` 与详情页扫码、重连、轮询策略和卸载 handler，使用真实 Vue 响应式，仅隔离原生 BLE、外部 API 和时钟。
  - 初始无 BMS，30 秒后可用：不切 Tab 自动更新；模拟请求耗时 5 秒，发起时刻为 0/6200/14200/22200/30200ms，体现串行 1.2/3 秒轮间等待，成功后恢复 2 秒。
  - 同会话首个完整响应在 11 秒返回仍可接收；切换会话后旧完整响应丢弃。
  - 配置 ACK/超时均只写一次 `0xFC`，清除旧状态，等待实际重连后恢复；原 `parsed is not defined` 路径不再异常退出。
  - 超过 30 秒空态后扫码恢复；取消/非法二维码不改旧数据；明确失败恢复读取，重连失败不无限重试。
  - 连续切换、重复点击、旧扫码回调隔离；参数/历史页及 OTA 暂停，配置完成时也遵守当时 Tab/OTA 状态。
  - 配置前等待、重连等待、连接进行中退出均不产生后续重连/读取；主动断开后停止查询。
- [x] `pnpm exec tsc --noEmit --pretty false`、`detail.vue` 的 Vue SFC script/template 编译通过。
- [x] Node 临时 TypeScript loader 执行 `instrument-passthrough-policy`、`detail-polling-policy`、`detail-data-arbiter`、`meter-scan-handoff-policy`、`meter-bms-ota-policy`、`scan-four-g-online-policy`、`detail-entry-source`、`detail-handoff`、`client-read-registers`、`boot-ota-runtime-options`、`ble-client-cache-release` 的测试通过。别名依赖测试由 loader 映射 `@/` 到项目根，未改业务依赖。
- [x] `node pages/device-provision/ble-scan-auto-start.test.js`、`node pages/device-provision/ble-scan-restart.test.js` 回归通过。
- [x] `/Applications/HBuilderX.app/Contents/MacOS/cli publish mp-weixin --project /Users/payhon/work2025/project/fjbms/fjbms-uniapp --upload false`：编译并本地导出成功，无上传。编译器仍提示 4 处既有平台/UA 判断可能未适配鸿蒙；微信开发者工具有 `punycode` 弃用提示，不影响导出。
- [x] 根仓库及 UniApp 的 `git diff --check`。

### 真机验收门禁（未执行）

- [ ] 微信小程序：仪表初始无 BMS，持续停留 30 秒以上后接入，完整数据自动出现，10 秒后无持续遮罩。
- [ ] 微信小程序：A→B 扫码正常响应/超时、不同 BMS 串数、供电延迟、连续切换，不切页面更新；核对目标设备实际数据。
- [ ] 仪表盘、电芯、参数、历史 Tab 与 OTA、主动断开、退出详情，以及有线仪表兼容。
- [ ] iOS/Android App 共享逻辑回归。模拟与编译结果不替代硬件验收。
