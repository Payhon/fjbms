# FEAT-0076 测试报告

- status: review
- owner: payhon
- last_updated: 2026-11-03

## 自动化验证

以下命令在 `fjbms-uniapp/` 执行，全部通过：

| 命令 | 覆盖范围 |
| --- | --- |
| `pnpm dlx tsx common/lib/bms-protocol/client-active-balance.test.ts` | 真实客户端帧及 CRC、先查 `0x136`、每轮仅新增一次电流查询、`0/FF/FE`、低字节忽略、超时/短响应、旧板补零、状态位跨 16/32 边界、刷新、取消与告警/动态区兼容 |
| `node pages/device-battery/active-balance-display.test.js` | 实际两个 SFC 脚本与模板编译和 SSR 渲染；电流值、旧快照/异常电流仅隐藏电流、均衡行常显、三个只读开关顺序、状态位独立于电流、归零清电芯背景、最高/最低类保留；实际快照指纹函数验证均衡变化触发更新 |
| `pnpm dlx tsx common/lib/bms-protocol/client-read-registers.test.ts` | 现有读取数量校验、超时透传、参数读取、取消与唤醒回归 |
| `node pages/device-battery/instrument-session-recovery.test.js` | 仪表恢复与实际详情 composable 回归 |
| `node pages/device-battery/protection-status-permission.test.js` | 保护状态权限与实际模板回归 |
| `pnpm dlx tsx pages/device-battery/ota-session.test.js` | OTA 准备、清理与轮询回归 |
| `pnpm dlx tsx pages/device-battery/detail-data-arbiter.test.ts` | 详情实时/云端快照仲裁回归 |
| `pnpm dlx tsx pages/device-battery/detail-polling-policy.test.ts` | 详情轮询策略回归 |
| `pnpm dlx tsx common/lib/bms-protocol/uni-mqtt-socket-transport-response-match.test.ts` | MQTT 回复匹配回归 |
| `pnpm dlx tsx common/lib/bms-protocol/uni-ble-transport-ota.test.ts` | BLE OTA 独占及传输回归 |
| `pnpm exec tsc --noEmit --pretty false` | 移动端类型检查 |
| 主仓库与移动端 `git diff --check` | 差异空白检查 |

## 2026-10-17 定向回归

- 实际 SFC 渲染新增断言通过：首次状态未返回、电流为零、缺失、null 或非法值时均衡行均存在，开关始终按均衡位显示；三个只读开关顺序正确，电流只在有效时显示。
- `node pages/device-battery/active-balance-display.test.js`、`node pages/device-battery/protection-status-permission.test.js`、`pnpm exec tsc --noEmit --pretty false` 通过。
- HBuilderX 5.26 微信小程序仅编译通过；uniCloud 服务空间缺失提示未阻断前端编译。
- 本轮仅修改仪表盘模板/计算/布局及对应测试文档，未重跑下列历史 Android/iOS 编译、浏览器截图和协议/传输回归，未操作真实设备。

## 2026-10-16 平台编译与布局

- HBuilderX 5.26：`launch mp-weixin --project <移动端绝对路径> --compile true --continue-on-error false` 编译成功。
- Android：同参数 `launch app-android` 编译成功。
- iOS：同参数 `launch app-ios --iosTarget simulator` 编译成功。默认真机目标被本地未签名标准基座检查阻止，未进行真机安装。
- 编译提示未关联 uniCloud 服务空间；未阻断三个目标的前端编译。Android 另有现存 UTS 通知插件需要自定义基座的提示，不改基座或签名配置。
- Playwright 检查从实际 SFC 生成的本地预览：375px、320px 无横向溢出；320px 最大有效电流 `25.4A` 不与标签、开关重叠。`51 08 00 11` 高亮第 4、9、13、15、17、21 芯，最高电压红字和最低蓝字保持。
- 本地预览和 SSR 使用开关/仪表组件替身，不代表微信或 App 原生控件、真实连接和设备协议验收。

## 真机验收待完成

1. 主动板在微信小程序、Android、iOS 经蓝牙和 4G 实际读取：`0F FF` 显示 `1.5A`，`00 FF` 显示 `0.0A`，`FF FF` 仅隐藏电流，均衡行保留且开关反映返回的均衡位。
2. 对比设备/上位机实际电流与逐电芯位，确认均衡开始、结束及归零时背景变化。
3. 不支持寄存器或无回复的旧板继续显示普通状态，检查新增请求对实际轮询耗时的影响。
4. 断开重连、切换设备、仪表透传、OTA 前后恢复不串用板型；MQTT 共享快照与蓝牙上报显示一致。

状态保持 `review`，不以本地模拟和编译通过代替真机验收。

## 2026-11-03 提交前复核

- 联合运行 23 个相关测试脚本，全部通过；覆盖主动均衡、BLE 重连/取消/租约/校时、扫码续扫/名称/列表与入口策略、仪表恢复、保护状态权限、OTA、数据仲裁、轮询和 MQTT 回复匹配。
- JavaScript 测试用 `node`，TypeScript 及含 TS 导入的 OTA 测试用现有 `../frontend/node_modules/.bin/tsx`，未新增或升级依赖。
- `pnpm exec tsc --noEmit --pretty false` 通过。
- `ble-scan.vue`、`detail.vue`、`cells-tab.vue`、`dashboard-tab.vue` 的微信小程序和 App 两个条件编译分支，经 Vue SFC 脚本及模板编译共 8 项检查通过。
- 拆分后的首条提交快照独立运行主动均衡协议和实际 SFC 渲染测试通过。
- 本次未重新执行 HBuilderX 平台构建、设备安装、真实 BLE/MQTT、屏幕布局或客户端发布；历史构建和预览结果不视为本次真机证据。
