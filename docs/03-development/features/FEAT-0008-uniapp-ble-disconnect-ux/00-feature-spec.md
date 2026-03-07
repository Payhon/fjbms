# FEAT-0008 UniApp 蓝牙信号展示与手动断开连接优化 - 功能规格

- status: in_progress
- owner: payhon
- last_updated: 2026-03-04
- related_feature: FEAT-0008
- version: v0.1.0

## 1. 背景与目标
- 背景：首页与蓝牙扫描页缺少直观的连接控制与信号展示能力，影响设备管理效率与可读性。
- 目标：
  1) 蓝牙扫描页将 RSSI 数值改为信号强度图标。
  2) BMS 设备详情页提供“断开蓝牙连接”入口。
  3) 首页设备卡片在连接状态下方提供“断开连接”图标按钮。

## 2. 范围
### In Scope
- `pages/device-provision/ble-scan.vue`：信号强度显示改为信号图标。
- `pages/device-battery/detail.vue` + `pages/device-battery/useBatteryDetail.ts`：新增蓝牙断开按钮与断开逻辑。
- `components/home/device-card.vue` + `pages/home/home.vue`：新增首页设备卡片断开图标按钮与断开逻辑。
- `common/ble/ble-client-cache.ts`：新增可立即断开指定 BLE 连接的方法。

### Out of Scope
- 不调整 BLE 扫描过滤规则与配网流程。
- 不改动 MQTT 连接策略与参数读写协议。

## 3. 用户价值
- 用户可更快识别设备信号强弱（图标化更直观）。
- 用户可在首页和详情页就地断开蓝牙连接，减少误连或占用问题。

## 4. 验收标准
1. 蓝牙扫描列表不再显示 RSSI 数字，改为 0~4 格信号图标。
2. BMS 详情页仅在当前为蓝牙已连接状态时显示“断开”按钮，点击后连接状态更新为非蓝牙。
3. 首页设备卡片仅在蓝牙连接状态展示断开图标按钮，点击后断开该设备 BLE 连接。
4. 非蓝牙连接状态点击/触发断开逻辑时不会误断开其他连接。

## 5. 风险与约束
- 风险：BLE 连接存在页面间共享缓存，断开时需避免误伤其他设备连接。
- 风险：连接状态 UI 与真实连接状态可能存在短时延迟。
- 约束：断开动作仅作用于 BLE，不影响 MQTT 连接态展示逻辑。

## 6. 回滚方案
- 回滚 `FEAT-0008` 相关 UniApp 提交，恢复原有 RSSI 文本展示与自动缓存释放策略。
- 如需快速止血，可先隐藏新断开按钮并保留原连接逻辑。
