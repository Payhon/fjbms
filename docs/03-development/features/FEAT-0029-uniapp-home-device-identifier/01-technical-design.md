# FEAT-0029 UniApp 首页设备标识展示切换 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-06-12
- related_feature: FEAT-0029
- version: v0.1.0

## 1. 方案概览
- 后端 `app/device/list` 统一返回 `imei` 字段，并保留 `iccid` 字段；`iccid` 继续优先取 `device_batteries.iccid`，为空时回退 `comm_chip_id`。
- UniApp 首页将卡片副标题从 `model` 拆为显式 `identifierText`，在 `toHomeModel()` 中根据 `bms_comm_type` 计算显示值。
- 蓝牙 MAC 复用现有 `mac12ToColon()` 统一格式化；4G/双模 BMS 优先输出 IMEI，IMEI 缺失时保留 ICCID 兼容回退。

## 2. 接口与数据结构
- `model.DeviceUserBindingResp` 返回：
  - `iccid?: string`
  - `imei?: string`
- UniApp 首页卡片类型新增：
  - `identifierText: string`
  - `iccid?: string | null`
  - `imei?: string | null`

## 3. 关键流程
1. 首页设备列表接口返回 `ble_mac`、`bms_comm_type`、`iccid`、`imei`。
2. 前端 `toHomeModel()` 根据 `bms_comm_type` 生成 `identifierText`：
   - `1 -> format(MAC)`
   - `2 -> IMEI -> ICCID`
   - `3 -> IMEI -> ICCID`
   - 默认回退旧副标题
3. 卡片组件直接渲染 `identifierText`，不再在组件内部判断通讯类型。

## 4. 安全与权限
- 不新增权限点。
- 仅调整展示字段，不改变设备归属、绑定或连接行为。

## 5. 测试策略
- 后端定向 Go 测试。
- 首页静态回归验证不同 `bms_comm_type` 的显示值。
- 手工验证首页点击、长按、蓝牙自动连接不受影响。

## 6. 兼容性与迁移
- 不新增 SQL 迁移。
- 历史只有 `comm_chip_id` 的设备通过后端映射继续返回 `iccid`，避免前端分叉兼容。
- 历史未补 IMEI 的 4G 设备仍按 ICCID 兼容值展示，不影响列表可读性。
