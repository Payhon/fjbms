# FEAT-0078 测试报告

- status: review
- owner: payhon
- last_updated: 2026-11-03

## 自动化
- `node pages/device-provision/ble-scan-restart.test.js`：通过。覆盖超时、保留与追加、重复设备更新、续扫命中跳转、再次超时、失败重试、本轮降级、连续点击、隐藏页及原重扫逻辑；通过隔离平台的模拟扫描运行。
- `node pages/device-provision/ble-scan-auto-start.test.js`：通过。
- `pnpm exec tsc -p tsconfig.json --noEmit --pretty false`：通过。
- Vue SFC 模板与脚本编译：通过；根仓库及移动端 `git diff --check`：通过。
- 按实际显示条件验证 iOS、Android、手动扫描及扫描中状态；未进行实际屏幕布局验收。

## 待验收
- iOS 微信小程序及 App 真机密集设备搜索、实际广播与匹配、多轮交互和中英文显示待验证；未验证真实 1000 台设备环境。

## 2026-11-03 提交前复核

- 联合运行 23 个相关测试脚本，全部通过；覆盖主动均衡、BLE 重连/取消/租约/校时、扫码续扫/名称/列表与入口策略、仪表恢复、保护状态权限、OTA、数据仲裁、轮询和 MQTT 回复匹配。
- JavaScript 测试用 `node`，TypeScript 及含 TS 导入的 OTA 测试用现有 `../frontend/node_modules/.bin/tsx`，未新增或升级依赖。
- `pnpm exec tsc --noEmit --pretty false` 通过。
- `ble-scan.vue`、`detail.vue`、`cells-tab.vue`、`dashboard-tab.vue` 的微信小程序和 App 两个条件编译分支，经 Vue SFC 脚本及模板编译共 8 项检查通过。
- 在尚未包含 FEAT-0079 的提交快照中，扫描重启/续扫与自动启动生命周期测试通过。
- 本次未重新执行 HBuilderX 平台构建、设备安装、真实 BLE/MQTT、屏幕布局或客户端发布；历史构建和预览结果不视为本次真机证据。
