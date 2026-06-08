# 实现记录

## 2026-05-29

- 新增迁移 `backend/sql/59.sql`，为 `device_batteries` 添加 `identity_ble_mac` 与索引。
- 移动端蓝牙扫描页向添加向导传递扫描/连接 MAC。
- 添加向导绑定请求新增 `identity_ble_mac`。
- 后端设备开通绑定支持双 MAC，旧客户端保持单 MAC 强校验。
- APP 电池详情、后台 BMS 电池列表透出 `identity_ble_mac`。
- BMS bridge DB 同步改为将协议身份 MAC 写入 `identity_ble_mac`。

## 2026-06-05

- 后端新增解绑后连接 MAC 释放 helper：当 `device_user_bindings` 与 `app_device_added_records` 均无当前设备记录时，清空 `device_batteries.ble_mac` 并更新 `updated_at`。
- APP 终端用户解绑、机构用户移除“我添加的设备”、后台强制解绑终端用户均接入同一释放逻辑。
- 释放逻辑只清连接/广播 MAC，不清 `identity_ble_mac`，保留 BMS 板身份 MAC。

## 2026-06-08

- 修复外挂蓝牙模块更换后，移动端未读出协议身份 MAC 时被旧 `ble_mac` 强一致校验拦截的问题。
- 绑定仍按 `item_uuid` 找设备；`identity_ble_mac` 为空时允许连接 MAC 替换为本次扫描/连接 MAC，但会先校验该连接 MAC 未被其他设备占用。
- 修复同一个外挂蓝牙模块曾绑定到其他 BMS 档案后，再被移动到当前 BMS 时被“蓝牙模块 MAC 已关联其他设备”拦截的问题：若旧档案不是内置 BLE 身份占用，则自动清空旧档案 `ble_mac` 并让当前 BMS 接管。
- 修复蓝牙添加向导重复绑定已属于当前用户的设备时返回 `device already bound to current user` 的问题；后端改为幂等成功返回，移动端按绑定成功跳转详情页。
