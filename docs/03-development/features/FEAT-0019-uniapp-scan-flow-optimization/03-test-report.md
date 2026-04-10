# FEAT-0019 UniApp 扫码流程优化 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-04-08
- related_feature: FEAT-0019
- version: v0.1.0

## 1. 测试范围
- 设备类型前缀静态配置化
- 扫码入口统一分流
- BLE 扫描列表点击分流
- 已添加设备扫码直达详情
- BMS 绑定成功后跳转详情页
- 仪表临时 BLE 会话详情与二次扫码绑定 BMS

## 2. 测试环境
- 当前 Codex 桌面执行环境
- Node/TypeScript 静态校验：`cd fjbms-uniapp && pnpm exec tsc --noEmit`
- 代码搜索回归：`rg -n "0xaa|0xAA|0xac|0xAC|'AA'|'AC'|\"AA\"|\"AC\"" fjbms-uniapp`
- 待补充：UniApp 真机或开发者工具联调结果

## 3. 用例结果
- 通过：默认前缀配置下，扫码解析已能将 `ACxxxx...` 识别为 `bms`、`AAxxxx...` 识别为 `meter`。
- 通过：`useAddDeviceActionSheet.ts` 与 `custom-tab-bar/index.js` 均改为依赖统一解析结果，入口分流口径一致。
- 通过：BMS 绑定向导和 UUID 绑定页已在成功后读取 `device_id` 并跳转设备详情页。
- 通过：摄像头扫码入口已新增“先匹配我的设备列表”的分支，命中 `ble_mac` 或 `item_uuid` 后将直接进入 `/pages/device-battery/detail?device_id=...`。
- 通过：仪表扫码已改为直接进入临时 BLE 会话详情模式，详情页支持继续扫码并写入新的 BMS 目标。
- 通过：蓝牙扫描页已在设备行中持久化 `deviceType`，点击 `AA` 前缀且广播 MAC 可用的仪表卡片时将直接进入 `/pages/device-battery/detail?session_mode=instrument&ble_mac=...&allow_scan_handoff=1&device_name=...`。
- 通过：蓝牙扫描页点击 `AC` 前缀 BMS 设备或广播缺少 `advMac` 的设备时，仍按原逻辑进入 `provision-wizard`，未把不确定设备误导向仪表临时会话。
- 通过：`params-tab.vue` 已在仪表临时会话下隐藏 OTA 入口，且 OTA 设备类型判定改为统一 helper。
- 通过：仓库搜索确认 `fjbms-uniapp/` 内不存在散落在业务逻辑里的 `AA/AC` 设备类型硬编码，检索结果仅剩 `device-prefix.js` 配置源文件本身。
- 通过：删除 `device-prefix.ts` 后，TS 页面仍可通过 `device-prefix.js` 的 JSDoc 标注完成类型检查，未出现导入或类型退化问题。
- 通过：`pnpm exec tsc --noEmit` 校验通过，无新增 TypeScript 类型错误。

## 4. 缺陷与风险
- 尚未完成真机蓝牙联调，以下场景仍需设备侧验证：
  - 已添加设备通过扫码直达详情页后的首连时延与页面体验；
  - BLE 扫描列表点击 `AA` 前缀仪表卡片后的路由分流与首连体验；
  - 仪表临时 BLE 会话下的自动连接成功率；
  - 仪表详情页二次扫码后 `configureMeterMac` 的协议写入和设备刷新时序；
  - APP 与微信小程序扫码 API 在不同机型上的体验一致性。

## 5. 结论
- 当前代码实现与静态校验已完成，建议进入真机联调/验收阶段。
