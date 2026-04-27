# FEAT-0049 BMS 4G 移动端云端详情链路 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-04-27
- related_feature: FEAT-0049
- version: v0.1.0

## 1. 后端接口
- 新增 `GET /api/v1/app/battery/current-telemetry/:device_id`。
- 接口先调用 `GetBatteryDetailForApp` 完成终端用户绑定、组织账号、租户权限校验。
- 返回 `is_online`、`last_report_ts`、当前遥测键值 map，以及可解析时的 `bms.snapshot`。

## 2. 移动端数据流
- 详情页加载 `appBatteryDetail` 后判断 4G-only：`bms_comm_type=2`，或存在 `comm_chip_id` 且无有效 `ble_mac`。
- 4G-only 设备直接调用当前遥测接口，不执行 BLE 扫描、BLE 连接、MQTT 透传 `BmsClient.readUuid/readAllStatus`。
- 若返回 `bms.snapshot`，直接作为 `BmsStatus`；否则从当前遥测摘要键合成局部 `BmsStatus` 供仪表盘组件使用。
- 详情页以固定间隔轮询当前遥测，保持面板数据刷新。

## 3. 电芯数据
- 电芯列表只来自 `cell.voltagesMv` 或 `bms.snapshot.cell.voltagesMv`。
- 如果设备只上报最高/最低/压差摘要，不生成虚假单体列表，只显示明确空态。

## 4. 兼容策略
- BLE-only 设备维持现有主动连接和状态上报逻辑。
- 蓝牙+4G 设备优先复用 BLE 热连接；BLE 不可用时降级为云端只读展示，不因 BLE 失败覆盖 4G 在线态。
