# FEAT-0079 测试报告

- status: review
- owner: payhon
- last_updated: 2026-11-03

## 已验证
- `node pages/device-provision/ble-scan-restart.test.js`：通过。使用实际名称选择及身份过滤逻辑，覆盖控制字符、替换字符、广播名恢复、旧名覆盖防护、Unicode、无名称设备匹配及无关设备过滤；续扫/超时回归通过。
- `node pages/device-provision/ble-scan-auto-start.test.js`：通过。
- `pnpm exec tsc -p tsconfig.json --noEmit --pretty false`：通过。
- Vue SFC 模板及脚本编译、根仓库及移动端 `git diff --check`：通过。

## 待验收
- iOS 微信小程序和 App 设备上电前后、断连及重新扫描的实际 name/localName 和界面表现，及 Android 回归均待真机验证；未抓取模块空口数据。
- 若平台未提供有效名称，本方案仅可显示未知设备，不能保证还原原名称；异常字符集合不覆盖所有可能的错误编码。

## 2026-11-03 提交前复核

- 联合运行 23 个相关测试脚本，全部通过；覆盖主动均衡、BLE 重连/取消/租约/校时、扫码续扫/名称/列表与入口策略、仪表恢复、保护状态权限、OTA、数据仲裁、轮询和 MQTT 回复匹配。
- JavaScript 测试用 `node`，TypeScript 及含 TS 导入的 OTA 测试用现有 `../frontend/node_modules/.bin/tsx`，未新增或升级依赖。
- `pnpm exec tsc --noEmit --pretty false` 通过。
- `ble-scan.vue`、`detail.vue`、`cells-tab.vue`、`dashboard-tab.vue` 的微信小程序和 App 两个条件编译分支，经 Vue SFC 脚本及模板编译共 8 项检查通过。
- 扫描重启/续扫/名称恢复与自动启动生命周期测试在完整名称恢复改动中通过。
- 本次未重新执行 HBuilderX 平台构建、设备安装、真实 BLE/MQTT、屏幕布局或客户端发布；历史构建和预览结果不视为本次真机证据。
