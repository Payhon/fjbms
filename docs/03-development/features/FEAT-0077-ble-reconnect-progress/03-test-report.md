# FEAT-0077 测试报告

- status: review
- owner: payhon
- last_updated: 2026-11-03
- related_feature: FEAT-0077
- version: v0.1.0

## 自动化验证

以下命令在 `fjbms-uniapp/` 执行，18 组测试全部通过：

| 命令 | 覆盖范围 |
| --- | --- |
| `node common/ble/ble-reconnect-progress.test.js` | 实际缓存、MAC/广播匹配、传输和租约；启动即命中、25/1499ms 命中、第二阶段命中、无关设备、取消、启动/停止失败、直连与回退、并发共享进度及回调异常；实际详情计算文案、两语言词条、微信/APP 分支 SFC 编译 |
| `node pages/device-battery/instrument-session-recovery.test.js` | 实际详情 composable 与页面 handler；新增旧会话/同会话旧连接/卸载后阶段隔离，保留全部仪表与 OTA 恢复回归 |
| `pnpm dlx tsx common/ble/ble-time-sync.test.ts` | 校时资格、去重、交接、重连、异常后继续和取消 |
| `pnpm dlx tsx common/ble/ble-client-cache-release.test.ts` | 缓存引用、关闭屏障、超时/失败不误释放新连接 |
| `pnpm dlx tsx common/ble/ble-discovery-coordinator.test.ts` | 扫描租约串行与归还 |
| `pnpm dlx tsx common/lib/bms-protocol/uni-ble-transport-connect-cancel.test.ts` | 原生连接取消、迟到回调、关闭及队列隔离 |
| `pnpm dlx tsx common/lib/bms-protocol/uni-ble-transport-ota.test.ts` | BLE OTA 独占与请求行为 |
| `pnpm dlx tsx common/lib/bms-protocol/boot-ota-transport.test.ts` | Boot 传输与普通请求隔离 |
| `pnpm dlx tsx pages/device-battery/ota-session.test.js` | OTA 准备、恢复与轮询策略 |
| `pnpm dlx tsx common/lib/bms-protocol/client-read-registers.test.ts` | 原读取、唤醒、取消与超时透传 |
| `pnpm dlx tsx common/lib/bms-protocol/client-active-balance.test.ts` | 既有未提交主动均衡功能回归 |
| `node pages/device-battery/active-balance-display.test.js` | 既有主动均衡页面渲染和快照指纹回归 |
| `pnpm dlx tsx pages/device-battery/detail-data-arbiter.test.ts` | 实时/云端数据会话仲裁 |
| `pnpm dlx tsx pages/device-battery/detail-polling-policy.test.ts` | 详情轮询策略 |
| `pnpm dlx tsx common/device-provision/detail-handoff.test.ts` | 配网到详情的连接交接 |
| `pnpm dlx tsx common/device-provision/detail-entry-source.test.ts` | 入口来源及返回断连策略 |
| `pnpm dlx tsx pages/device-battery/scan-four-g-online-policy.test.ts` | 4G 在线宽限 |
| `pnpm dlx tsx common/lib/bms-protocol/uni-mqtt-socket-transport-response-match.test.ts` | MQTT 回复匹配 |

模拟结果：iOS 首次扫描在 0/25/1499ms 收到目标即结束等待；第二窗口 25ms 收到目标时累计扫描 1525ms；Android 回退扫描 25ms 命中即结束。无匹配仍累计扫描 5000ms。停止扫描先于原生连接，扫描监听和租约均释放；既有串行任务的超时定时器不属于本功能新增内容，测试只允许该原有计时器保留。

## 类型、平台编译与差异检查

- `pnpm exec tsc --noEmit --pretty false`：通过。
- `git diff --check`（根仓与移动端）：通过。
- HBuilderX 5.26 `launch mp-weixin --project <移动端绝对路径> --compile true --continue-on-error false`：成功。
- 同参数 `launch app-android`：成功。
- 同参数 `launch app-ios --iosTarget simulator`：成功。
- 编译提示项目未关联 uniCloud，但三个目标前端编译均成功；Android 保留原有 UTS 通知插件需要自定义基座的提示。微信编译对原有平台判断提示鸿蒙适配风险，本次未扩展平台识别行为。
- 仅编译模式，未安装/启动客户端或发布；编译工具改写的 Android 基座选择已恢复原配置。

## 真机验收待完成

1. 微信小程序在 iPhone/Android 上，从列表重连休眠板，记录点击、广播、原生连接和首帧时间；核对搜索、连接、初始化提示。
2. 无目标、蓝牙关闭/权限拒绝、切后台、快速返回/切换设备后不串用提示或连接。
3. 新添加交接、首页暖连接、手动断连重连、纯蓝牙校时、仪表透传、OTA 后恢复、4G/MQTT 原功能保持。

模拟及编译不能证明真机总耗时或旧固件兼容性，保持 review。

## 2026-11-03 提交前复核

- 联合运行 23 个相关测试脚本，全部通过；覆盖主动均衡、BLE 重连/取消/租约/校时、扫码续扫/名称/列表与入口策略、仪表恢复、保护状态权限、OTA、数据仲裁、轮询和 MQTT 回复匹配。
- JavaScript 测试用 `node`，TypeScript 及含 TS 导入的 OTA 测试用现有 `../frontend/node_modules/.bin/tsx`，未新增或升级依赖。
- `pnpm exec tsc --noEmit --pretty false` 通过。
- `ble-scan.vue`、`detail.vue`、`cells-tab.vue`、`dashboard-tab.vue` 的微信小程序和 App 两个条件编译分支，经 Vue SFC 脚本及模板编译共 8 项检查通过。
- 拆分后的提交快照独立运行蓝牙重连进度和仪表会话恢复测试通过。
- 本次未重新执行 HBuilderX 平台构建、设备安装、真实 BLE/MQTT、屏幕布局或客户端发布；历史构建和预览结果不视为本次真机证据。
