# FEAT-0019 UniApp 扫码流程优化 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-04-18
- related_feature: FEAT-0019
- version: v0.1.0

## 1. 方案概览
- 新增 `fjbms-uniapp/common/device-provision/device-prefix.js` 作为设备前缀配置真源。
- 扫码解析模块在识别到 `MAC` 后，通过 `resolveDeviceTypeByMac(mac)` 得到 `bms | meter | null`。
- 摄像头扫码新增“已添加设备直达详情”分支：先基于绑定设备列表匹配 `ble_mac / item_uuid`，命中后直接以 `device_id` 打开详情页。
- BMS 扫码继续复用：
  - `ble-scan.vue` 自动匹配 BLE 设备
  - `provision-wizard.vue` 完成 UUID 读取、可选 DTU 写入和绑定
- BMS 绑定成功后，向导页将当前 BLE 会话接管进缓存，并写入一次 `provision -> detail` handoff；详情页优先消费该 handoff，先展示基础信息并直接接管已连 BLE，再后台刷新云端详情。
- 仪表扫码以及 BLE 扫描列表点击命中仪表设备时，不再走云端绑定链路，直接进入 `pages/device-battery/detail` 的临时 BLE 会话模式。

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
- `provision-wizard.vue` 在 BLE 绑定成功后：
  - 若当前会话已拿到 `ble_mac`，先将 `transport/client/deviceId/mac` 接管进 `ble-client-cache.ts`；
  - 再写入轻量 handoff（`deviceId/bleMac/deviceName/itemUuid/bmsCommType/source/createdAt`）；
  - 最后跳转详情页。
- `detail.vue` 进入云端详情模式时先按 `device_id` 消费 handoff：
  - 命中 handoff 且缓存中存在同 MAC 的已连接 BLE 会话时，直接 attach，不再重新探测 `readUuid()`；
  - 若缓存 miss，则基于 handoff 中的 `ble_mac` 立即发起 BLE 自动连接，不等待 `appBatteryDetail`；
  - `appBatteryDetail` 改为后台刷新，成功后只更新视图模型，不再强制打断现有 BLE 会话。
- `detail.vue` 进入普通云端详情模式且未命中 handoff 时：
  - 先完成一次 `appBatteryDetail(device_id)` 获取准确 `ble_mac`；
  - 若 `ble-client-cache.ts` 中已存在同 MAC 的活跃连接，则直接 attach 该会话并启动轮询，不再强制 `disconnectAll() + reconnect`；
  - 这样首页或“我的设备”列表已连通的 BLE 连接可被扫码直达详情页直接复用，尤其避免 iOS 二次建连带来的额外时延。
- `ble-client-cache.ts` 额外承担 iOS 直连加速：
  - 新增轻量 `ble-device-id-memory.ts`，将标准化 `MAC` 对应的 iOS `deviceId` 持久化到本地；
  - iOS 新建 BLE 连接时，先尝试当前缓存 entry 的 `deviceId`，再尝试本地记忆的 `deviceId`，均失败后才回退到扫描；
  - 扫描回退改为两段式短扫，先约 `1.5s`，未命中再补扫到累计约 `5s`，命中后立即停止并建连；
  - 每次 iOS 直连或扫描建连成功后，都用最新 `deviceId` 覆盖本地记忆。

### 3.5 BLE 扫描列表点击分流
- `pages/device-provision/ble-scan.vue`
- `DeviceRow` 记录 `deviceType: SupportedDeviceType | null`。
- `upsertDevice()` 在解析到广播 MAC 后调用 `resolveDeviceTypeByMac(advMac)` 写入行数据；若本次广播缺失 `advMac`，沿用已存在行上的 `deviceType`，避免设备类型在重复广播中闪断。
- `selectDevice()` 的点击规则固定为：
  - `deviceType === 'meter'` 且 `advMac` 可用 -> 跳转 `/pages/device-battery/detail?session_mode=instrument&ble_mac=...&allow_scan_handoff=1&device_name=...`
  - 其它情况 -> 继续跳转 `/pages/device-provision/provision-wizard?deviceId=...`
- 不调整 `onDeviceFound()` 的自动匹配逻辑；`mode=qr` 仍只服务 BMS 添加链路，仪表仅在用户点击扫描卡片时进入临时会话。
- BLE 扫描页的蓝牙 API 调用需要增加超时保护：
  - `openBluetoothAdapter` / `startBluetoothDevicesDiscovery` 超时后直接抛错，结束按钮 loading 并展示初始化失败；
  - `stopBluetoothDevicesDiscovery` 在 iOS App 端若未处于 `discovering` 状态则不调用，若回调长时间不返回则超时放行，避免阻塞后续启动扫描。
- `uni-ble-transport.ts` 对 iOS 写入回调噪声做单次诊断收敛：
  - `writeBLECharacteristicValue` 在部分 iPhone + uni runtime 组合下会出现底层已发出、设备也正常 notify 回复，但 write API 的 success/fail 回调迟迟不返回；
  - transport 继续保留 soft-timeout 快速放行，避免请求队列被原生桥接层卡死；
  - 同时将“继续等待 notify”的日志改为每次连接仅记录一次 info 级 callback latency diagnostic，避免轮询期间持续刷出 timeout 告警干扰问题判断。

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
- 手工验证扫码入口分流、BLE 扫描卡片点击分流、BMS 绑定后跳转、绑定成功后详情页首连时延、仪表临时详情和二次扫码绑定流程。
