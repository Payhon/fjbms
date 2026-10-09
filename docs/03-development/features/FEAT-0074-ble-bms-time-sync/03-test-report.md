# FEAT-0074 测试报告

- status: review
- owner: payhon
- last_updated: 2026-09-16

## 自动化验证

以下命令在 `fjbms-uniapp/` 执行：

| 命令 / 检查 | 结果 |
| --- | --- |
| `pnpm dlx tsx common/ble/ble-time-sync.test.ts` | 通过：完整示例帧/CRC、默认 Unix 秒、uint32 边界及非法输入、请求参数透传、资格排除、未知类型补校时、并发单次、配网交接、实际连接 MAC、重连、连接中取消、iOS 超时不重发/拒绝/断连 |
| `pnpm dlx tsx common/lib/bms-protocol/client-read-registers.test.ts` | 通过：协议读取回归 |
| `pnpm dlx tsx common/ble/ble-client-cache-release.test.ts` | 通过：缓存释放与关闭屏障 |
| `pnpm dlx tsx common/lib/bms-protocol/uni-ble-transport-connect-cancel.test.ts` | 通过：连接取消及旧请求代际保护 |
| `node pages/device-battery/instrument-session-recovery.test.js` | 通过：生产 composable 与页面处理器回归；测试缓存补齐真实连接 MAC 与接管查询行为 |
| `pnpm dlx tsx common/lib/bms-protocol/uni-ble-transport-ota.test.ts` | 通过：OTA 传输及独占回归 |
| `pnpm dlx tsx pages/device-battery/ota-session.test.js` | 通过：OTA 页面准备/清理与轮询回归 |
| `pnpm exec tsc --noEmit --pretty false` | 通过 |
| `@vue/compiler-sfc` 的 parse、compileScript、compileTemplate | 通过：首页和配网向导 |
| 主仓库及移动端 `git diff --check` | 通过 |

时间同步断言调用实际 BmsClient、连接缓存和 BLE 请求队列，替换原生 BLE API；超时后保留连接并验证后续读取，主动断连验证校时异常被捕获。连接编排断言确认校时结束前不将新连接交给业务读取。以上均为本地自动化证据。

## 真机验收（待完成）

- Android、iOS、微信小程序连接 AC 纯蓝牙 BMS：校时帧一次，当前 Unix 秒正确，设备 RTC/历史时间一致。
- 首页连接后进入详情、配网交接：不重复；断开重连重新发送。
- AA 仪表（含透传 AC BMS）、4G、双模、未知通信类型：零校时帧。
- 旧固件不支持、无应答、连接中断：不弹窗或重复校时，存活连接继续读取，重连后恢复。
- OTA 中无普通校时；升级后重连仍遵循资格及单次规则。

自动化模拟结果不代表真实硬件验收。


## 2026-10-09 Git 交付前复核

- 重新运行校时协议/资格/去重/异常、协议读取、缓存释放、连接取消、仪表恢复、BLE OTA 和 OTA 会话回归，全部通过。
- UniApp TypeScript 及首页/配网向导在微信小程序和 App 分支的 SFC 编译通过。
- 本轮按用户授权拆分 Git 提交并推送；未重新打包/发布移动端、部署服务或操作数据库，真机验收和功能状态保持原记录。
