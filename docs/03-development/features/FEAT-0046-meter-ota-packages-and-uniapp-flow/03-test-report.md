# FEAT-0046 仪表 OTA 升级包与 UniApp 独立升级链路 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-09-02
- related_feature: FEAT-0046
- version: v0.1.2

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
- [ ] 蓝牙仪表会话显示独立 BMS 升级卡片，未检测到BMS状态时按钮禁用。
- [ ] UUID成功、UUID失败后型号降级、身份缺失阻断三条检查分支符合预期。
- [ ] 仪表透传 BMS 首帧为 `55 FE 01 50 00 00 0C 39 FD`，且使用标准BMS时序。
- [ ] 仪表自身 `0xFC`、透传BMS `0x01`、直接BMS `0x01` 三条链路互不影响。
- [ ] 透传 BMS 必须收到全部 `0x53` ACK 和真实 `0x54 status=0` 才成功。
- [x] 模拟 Boot transport 验证有效 `0x52` ACK 到首个 `0x53`、最后一个 `0x53` ACK 到 `0x54` 均为约 300ms 且不超过700ms。
- [x] 时序策略断言 `0x50`～`0x53` 应答超时600ms、超时重发缓冲220ms、ACK后主动等待预算600ms；BLE `0x54` 最多8次、间隔800ms、单窗口6400ms，MQTT/4G保持单次发送和5000ms窗口。

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
- 2026-07-21：增加 BLE OTA 独占通讯会话并将蓝牙 BMS/仪表 `0x54` 收敛为单个 5s 严格应答窗口；静态检查 `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false` 通过，待 Android、iOS 与微信小程序真机验证 OTA 启动等待和 `0x54 status=0` 收敛。
- 2026-08-03：后端透传身份解析与升级包匹配定向测试通过；UniApp `pnpm exec tsc --noEmit --pretty false` 通过。策略脚本覆盖卡片门控、UUID规范化/降级请求和 `0x01` Boot查询帧，真机验收仍待执行。
- 2026-08-05：新增 OTA 时序常量与模拟 Boot transport 测试，临时编译后两项定向测试通过；`pnpm exec tsc --noEmit --pretty false` 与 UniApp `git diff --check` 通过。Android、iOS、微信小程序和4G/MQTT真实设备的700ms时序仍待验收。
- 2026-08-06：BLE `0x54` 时序常量断言与模拟 transport 场景通过：无应答时首发加7次补发共8次且不启动第二轮，`status=0` 提前应答会清理剩余定时器，非零状态会立即失败并清理定时器；MQTT/4G仍为单次发送和5000ms窗口。`pnpm dlx tsx common/lib/bms-protocol/boot-ota-runtime-options.test.ts`、`pnpm dlx tsx common/lib/bms-protocol/boot-ota-timing.test.ts`、`pnpm exec tsc --noEmit --pretty false`、UniApp及文档 `git diff --check` 均通过。真机BLE发送时间戳仍待验收。
- 2026-08-28：BLE与MQTT/4G共享非完成帧应答超时调整为900ms；`pnpm dlx tsx common/lib/bms-protocol/boot-ota-runtime-options.test.ts`、`pnpm dlx tsx common/lib/bms-protocol/boot-ota-timing.test.ts`、`pnpm exec tsc --noEmit --pretty false` 均通过。Android、iOS、微信小程序及4G/MQTT真实设备成功率仍待客户验证。
- 2026-09-02：BLE与MQTT/4G共享非完成帧应答超时由900ms调整为600ms；定向时序断言和类型检查通过，Android、鸿蒙、iOS、微信小程序及4G/MQTT真机成功率继续待客户验证。
- 待执行前端构建复测。
- 待真机联调仪表 OTA 下载与写包流程。
- 待 Android、iOS、微信小程序分别验证仪表透传 BMS OTA 全流程以及升级后版本变化。
