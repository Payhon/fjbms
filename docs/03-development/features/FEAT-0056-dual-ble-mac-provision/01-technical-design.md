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

- 客户端未提交 `identity_ble_mac` 时，仍以 `item_uuid` 作为主身份；若本次连接 MAC 与档案 `ble_mac` 不同，允许更新当前设备 `ble_mac`。
- 连接 MAC 被其他设备档案占用时，若对方 `identity_ble_mac` 不等于该连接 MAC，则视为可复用外挂蓝牙模块的历史占用，清空旧设备档案 `ble_mac` 后让当前 `item_uuid` 接管。
- 连接 MAC 被其他设备档案占用且对方 `identity_ble_mac` 等于该连接 MAC 时，视为内置 BLE/真实身份 MAC，继续阻断绑定，避免错绑真实设备。
- 终端用户重复绑定同一 `item_uuid` 时返回成功，保持绑定接口幂等，移动端可按成功流程跳转设备详情。
- BMS 4G bridge 上报的 `identity.bluetoothMac` 写入 `identity_ble_mac`，不再覆盖连接用 `ble_mac`。

## 解绑释放连接 MAC

外挂蓝牙模块属于可复用连接介质，用户解绑后不应继续占用旧设备档案的 `ble_mac`。

后端新增公共释放逻辑，在解除 APP 侧关联后执行：

1. 检查 `device_user_bindings` 是否仍存在当前 `device_id` 记录。
2. 检查 `app_device_added_records` 是否仍存在当前 `device_id` 记录。
3. 两类 APP 侧关联都为空时，更新 `device_batteries.ble_mac = NULL` 与 `updated_at`。
4. 不清理 `identity_ble_mac`、`item_uuid`、`comm_chip_id` 等设备身份字段。

接入入口：

- `/api/v1/app/device/unbind`: 终端用户解绑后释放连接 MAC。
- `/api/v1/app/device/remove`: 机构用户移除添加记录后释放连接 MAC。
- `/api/v1/end_user/force_unbind`: 后台强制解绑终端用户后释放连接 MAC。

激活状态回退仍按原规则以终端用户绑定数量判断；连接 MAC 释放独立按“无任何 APP 侧关联”判断。
