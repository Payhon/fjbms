# 实现记录

## 2026-05-29

- 新增迁移 `backend/sql/59.sql`，为 `device_batteries` 添加 `identity_ble_mac` 与索引。
- 移动端蓝牙扫描页向添加向导传递扫描/连接 MAC。
- 添加向导绑定请求新增 `identity_ble_mac`。
- 后端设备开通绑定支持双 MAC，旧客户端保持单 MAC 强校验。
- APP 电池详情、后台 BMS 电池列表透出 `identity_ble_mac`。
- BMS bridge DB 同步改为将协议身份 MAC 写入 `identity_ble_mac`。
