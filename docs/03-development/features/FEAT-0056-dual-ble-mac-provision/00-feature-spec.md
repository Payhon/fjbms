# FEAT-0056 外挂蓝牙透传设备双 MAC 添加

- owner: payhon
- status: review
- priority: P1
- created_at: 2026-05-29

## 背景

外挂蓝牙透传设备存在两个 MAC：APP 扫描/连接使用的蓝牙模块 MAC，以及 BMS 协议身份区读取到的设备身份 MAC。旧流程只使用 `device_batteries.ble_mac`，导致两个 MAC 不一致时绑定失败。

## 目标

1. 保留 `device_batteries.ble_mac` 作为 APP 连接/广播 MAC。
2. 新增 `device_batteries.identity_ble_mac` 保存协议身份区 MAC。
3. 移动端添加设备时同时提交连接 MAC 和身份 MAC。
4. 后端允许同一 `item_uuid` 下两个 MAC 不同，但阻止连接 MAC 被其他设备占用。

## 验收标准

- 普通内置 BLE 设备添加成功。
- 外挂蓝牙透传设备连接 MAC 与身份 MAC 不同时添加成功。
- 后续详情页 BLE 自动连接仍使用 `ble_mac`。
- 身份 MAC 已有非空不同值时拒绝绑定，避免错绑。
