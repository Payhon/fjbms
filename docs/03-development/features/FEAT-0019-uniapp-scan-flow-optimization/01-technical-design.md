# FEAT-0019 UniApp 扫码流程优化 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-03-25
- related_feature: FEAT-0019
- version: v0.1.0

## 1. 方案概览
- 新增 `fjbms-uniapp/common/device-provision/device-prefix.js` 作为设备前缀配置真源。
- 扫码解析模块在识别到 `MAC` 后，通过 `resolveDeviceTypeByMac(mac)` 得到 `bms | meter | null`。
- 摄像头扫码新增“已添加设备直达详情”分支：先基于绑定设备列表匹配 `ble_mac / item_uuid`，命中后直接以 `device_id` 打开详情页。
- BMS 扫码继续复用：
  - `ble-scan.vue` 自动匹配 BLE 设备
  - `provision-wizard.vue` 完成 UUID 读取、可选 DTU 写入和绑定
- 仪表扫码不再走云端绑定链路，直接进入 `pages/device-battery/detail` 的临时 BLE 会话模式。

## 2. 静态配置设计
### 2.1 模块位置
- 新增：`fjbms-uniapp/common/device-provision/device-prefix.js`

### 2.2 导出内容
- `DEVICE_TYPE_BMS = 'bms'`
- `DEVICE_TYPE_METER = 'meter'`
- `DEVICE_MAC_PREFIXES = { bms: ['AC'], meter: ['AA'] }`
- `SUPPORTED_DEVICE_TYPES`
- `resolveDeviceTypeByMac(mac)`
- `isBmsMac(mac)`
- `isMeterMac(mac)`

### 2.3 约束
- helper 内部只能读取 `DEVICE_MAC_PREFIXES`，不得硬编码 `AA/AC`。
- TS 与 JS 页面都引用同一个 `device-prefix.js` 模块；不再保留额外的 TS 同名桥接文件。

## 3. 扫码入口与页面流转
### 3.1 扫码解析
- `common/device-provision/scan-code.ts`
  - 维持对 `MAC/UUID` 的识别。
  - 对 `MAC` 结果补充 `deviceType` 字段，来源于 `device-prefix.js`。

### 3.2 入口统一
- `common/composables/useAddDeviceActionSheet.ts`
- `custom-tab-bar/index.js`
- `common/device-provision/scan-routing.js`
- 两处均按同一规则跳转：
  - `已命中绑定设备` -> `device-battery/detail?device_id=...`
  - `UUID`（未命中） -> `uuid-bind`
  - `MAC + bms`（未命中） -> `ble-scan?mode=qr&mac=...`
  - `MAC + meter`（未命中） -> `device-battery/detail?session_mode=instrument&ble_mac=...`
  - `MAC + null` -> 提示无效或不支持的二维码

### 3.3 已绑定设备匹配
- `store/bound-devices.ts` 扩展 `item_uuid` 字段和查找能力：
  - `findByBleMac(mac12)`
  - `findByItemUuid(uuid32)`
- `scan-routing.js` 统一执行以下优先级：
  - `MAC` 先匹配 `ble_mac`
  - `UUID` 先匹配 `item_uuid`
  - 命中后返回 `bound_detail` 决策
  - 未命中再回落到现有添加/临时会话链路

### 3.4 BMS 成功跳转
- `provision-wizard.vue` 和 `uuid-bind.vue` 绑定成功后读取 `bind` 返回的 `device_id`，统一跳转 `/pages/device-battery/detail?device_id=...`。

## 4. 仪表临时会话模式
### 4.1 路由参数
- `session_mode=instrument`
- `ble_mac`
- `device_name`（可选）
- `allow_scan_handoff=1`

### 4.2 详情页行为
- `pages/device-battery/detail.vue` 新增对临时会话参数的识别。
- `pages/device-battery/useBatteryDetail.ts` 新增本地 BLE 会话加载能力：
  - 不调用 `appBatteryDetail`
  - 使用最小 `battery` 对象承载 `ble_mac/device_name/bms_comm_type`
  - 仅尝试 BLE 连接
  - 禁用连接状态上报、报告上云、MQTT、Relay

### 4.3 二次扫码绑定 BMS
- 在仪表临时会话模式下显示“继续扫码绑定 BMS”按钮。
- 按钮触发扫码，仅允许 `deviceType === 'bms'` 的 MAC。
- 成功后调用 `client.configureMeterMac({ meterAddress: 0xFC, mac })`。

## 5. 验证策略
- `cd fjbms-uniapp && pnpm exec tsc --noEmit`
- 搜索回归：确认 `fjbms-uniapp` 业务逻辑中不再存在裸 `AA/AC` 设备类型判断。
- 手工验证扫码入口分流、BMS 绑定后跳转、仪表临时详情和二次扫码绑定流程。
