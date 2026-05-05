# FEAT-0046 仪表 OTA 升级包与 UniApp 独立升级链路 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-04-28
- related_feature: FEAT-0046
- version: v0.1.0

## 1. 自动化验证
- [x] `cd backend && go test ./internal/service/...`
- [ ] `cd frontend && pnpm build`
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit`

## 2. 手工验证清单
- [ ] 后台升级包管理页双 TAB 可切换。
- [ ] BMS TAB 新增/编辑/删除维持原有行为。
- [ ] 仪表 TAB 仅要求名称、固件文件、说明。
- [ ] OTA 任务页和电池列表批量 OTA 只出现 BMS 升级包。
- [ ] 蓝牙仪表详情页隐藏旧 OTA 检测入口与红点。
- [ ] 蓝牙仪表详情页可拉取仪表固件列表、选择固件、确认升级。
- [ ] 仪表升级时 Boot 目标地址固定为 `0xFC`。

## 3. 待补充
- 2026-04-21：已复测 `cd backend && go test ./internal/service/...`，通过。
- 2026-04-21：已复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-26：修复 Android 仪表扫描进入详情连接候选、iOS 0x53 超时重试、`status=5` 文案后，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-26：继续修复 Android 仪表详情“连接中”无退出问题，增加 BLE 连接队列与 `createBLEConnection` 超时出口后，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-26：继续修复 Android 仪表 OTA 17% 写包超时，调整仪表 `0x53` 超时和 Android 写入节奏后，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-26：继续修复 Android 仪表 OTA 13% 写包超时，针对 4KB 固件边界增加 Android 仪表 OTA 专用边界等待参数后，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-26：根据 Android 仪表 OTA 10% 卡住日志确认 20 字节 BLE 分片会导致首个 `0x53` 无 ACK，已撤回分片并保持 Boot 帧单次 BLE 写入，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-26：根据 Android 仪表 OTA 95% finalize 日志确认数据包已完整 ACK，优化 `0x54` 超时/断开成功收敛与静默预期超时日志后，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-26：优化蓝牙扫描页停止扫描与扫描超时状态复位后，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-26：根据 iOS 仪表 OTA 95% finalize 日志确认全部数据包已 ACK，补齐 iOS `0x54` 后 `no device` 断连成功收敛与静默 finalize 重试策略后，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-26：根据 iOS 成功升级日志确认 `0x53` 全部 ACK 与 `0x54` finalize 收敛，并优化 iOS 扫描进详情直连候选与取消旧连接后的锁等待，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-27：新增开发者模式下仪表 OTA 端上调试日志、复制与清空能力后，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-27：优化微信小程序主包体积，将 OTA 调试日志模块迁入设备详情分包并删除未引用 `static/js/moment.js` 后，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-28：根据微信小程序仪表 OTA 95% 日志，补齐最后一个 `0x53` 写入遇到 `10006/writeValueToCharacteristics` 时进入 `0x54` finalize 的成功收敛策略，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-28：统一蓝牙 BMS 与蓝牙仪表在 Android/iOS 运行时的 OTA 末尾边界策略，仪表 Android 专用写包节奏保持独立，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-28：根据小程序仪表 OTA 成功界面但版本未变化日志，将仪表 OTA 改为 `0x53` 全部 ACK + 延迟 2s + `0x54 status=0` 的严格成功条件，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-28：借鉴旧版微信小程序 OTA 可用实现，蓝牙 BMS 与蓝牙仪表 OTA 均增加 `0x54` 300ms/600ms/900ms 补发；两者均要求 `0x54 status=0` 才判定成功，仪表额外兼容 `0xFD` Boot 回包源地址，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 2026-04-28：优化 Android 仪表 `0x53` ACK 驱动发包速度，取消默认 ACK 后固定等待、降低最小帧间隔与 4KB 边界等待，并增加超时后的自动慢速保护，复测 `cd fjbms-uniapp && pnpm exec tsc --noEmit`，通过。
- 待执行前端构建复测。
- 待真机联调仪表 OTA 下载与写包流程。
