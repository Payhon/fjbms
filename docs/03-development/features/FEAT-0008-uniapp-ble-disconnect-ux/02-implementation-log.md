# FEAT-0008 UniApp 蓝牙信号展示与手动断开连接优化 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-03-04
- related_feature: FEAT-0008
- version: v0.1.0

## 日志
1. 新增 BLE 缓存强制断开能力：
   - `fjbms-uniapp/common/ble/ble-client-cache.ts`
   - 新增 `disconnectBleClient(mac)`，支持立即断开与缓存清理。
2. 设备详情页新增断开按钮与逻辑：
   - `fjbms-uniapp/pages/device-battery/detail.vue`
   - `fjbms-uniapp/pages/device-battery/useBatteryDetail.ts`
   - 仅蓝牙已连接时显示“断开”按钮，点击后执行 BLE 断连。
3. 首页设备卡片新增断开图标按钮：
   - `fjbms-uniapp/components/home/device-card.vue`
   - `fjbms-uniapp/pages/home/home.vue`
   - 卡片新增 `disconnect` 事件，首页处理断开并回写连接态。
4. 蓝牙扫描信号改为图标：
   - `fjbms-uniapp/pages/device-provision/ble-scan.vue`
   - RSSI 数值文本改为 4 档信号柱图展示。
5. i18n 文案补充：
   - `fjbms-uniapp/lang/zh-CN.ts`
   - `fjbms-uniapp/lang/en-US.ts`
6. 蓝牙扫描页广播 MAC 展示修复：
   - `fjbms-uniapp/pages/device-provision/ble-scan.vue`
   - `advMac` 行改为本地 `format` 插值，避免 `{mac}` 原样显示；
   - 当 `advMac` 为空字符串/空值时隐藏该行。
7. 蓝牙自动连接兼容性修复：
   - `fjbms-uniapp/common/ble/ble-client-cache.ts`
   - `canBleAutoConnect` 调整为“有有效 BLE MAC 即允许尝试连接”，避免 `bms_comm_type` 与实际能力不同步导致不连接。
8. 蓝牙自动连接配置读取兼容性修复：
   - `fjbms-uniapp/pages/home/home.vue`
   - `fjbms-uniapp/pages/my/my.vue`
   - 新增布尔存储解析，兼容 `1/0`、`true/false`、`on/off` 等历史存储值。
9. BLE MAC 归一化增强（前端）：
   - `fjbms-uniapp/common/device-provision/ble.ts`
   - `normalizeMac` 增加“尾部 00 补位裁剪”逻辑，支持异常值修复为标准 12 位 MAC。
10. Status 解析中的蓝牙 MAC 修复（前端）：
   - `fjbms-uniapp/common/lib/bms-protocol/status-parser.ts`
   - 将动态区 10-byte MAC 统一裁剪为 6-byte，避免 `...:00:00:00:00` 上报。
11. 绑定与上报链路 MAC 存储修复（后端）：
   - `backend/internal/service/ble_mac.go`
   - `backend/internal/service/device_provision.go`
   - `backend/internal/service/app_battery.go`
   - 后端统一归一化 BLE MAC；对于尾部补零/历史异常值支持修复写回，避免污染 `device_batteries.ble_mac`。
