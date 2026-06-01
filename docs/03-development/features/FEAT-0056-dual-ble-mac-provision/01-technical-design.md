# 技术设计

## 数据模型

- `device_batteries.ble_mac`: 连接/广播 MAC，用于 APP 扫描匹配与自动 BLE 连接。
- `device_batteries.identity_ble_mac`: BMS 协议身份区读取到的蓝牙 MAC，用于身份留痕与排障。

## 绑定流程

1. 蓝牙扫描页解析 `advMac` 并传入添加向导。
2. 添加向导连接设备后读取 `item_uuid` 与 `identity.bluetoothMac`。
3. 绑定接口提交 `ble_mac=advMac/qrMac`，`identity_ble_mac=identity.bluetoothMac`。
4. 后端按 `item_uuid` 查设备，校验连接 MAC 未被其他设备占用，然后写入/修复两个 MAC 字段。

## 兼容策略

- 旧客户端未提交 `identity_ble_mac` 时仍执行单 MAC 强一致校验。
- BMS 4G bridge 上报的 `identity.bluetoothMac` 写入 `identity_ble_mac`，不再覆盖连接用 `ble_mac`。
