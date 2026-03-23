# FEAT-0024 item_uuid 大小写归一化防重复注册 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-03-23
- related_feature: FEAT-0024

## 1. 设计原则
- 以后端为最终可信边界，统一对 `item_uuid` 做归一化。
- 以前端为第一道收敛口，尽量减少错误请求进入服务端。
- 不依赖数据库层大小写忽略作为主逻辑，只把它作为历史脏数据兼容兜底。

## 2. 方案
### 2.1 UniApp
- `common/lib/bms-protocol/client.ts`
  - `readUuid()` 返回值改为大写十六进制字符串。
- `service/deviceProvision.ts`
  - 请求 `provision/info` 与 `provision/bind` 前，统一将 `item_uuid` 归一化为大写。

### 2.2 Backend
- `internal/service/device_provision.go`
  - 新增 `normalizeItemUUID()`，统一执行 `TrimSpace + ToUpper`。
  - `findDeviceByItemUUIDWithDB()` 先按规范化值精确查询；若未命中，再按大小写无关方式兜底查询历史小写记录。
  - `createAutoRegisteredDevice()` 使用规范化后的 `item_uuid` 写入 `devices.device_number` 与 `device_batteries.item_uuid`。
  - `GetProvisionInfo()` 与 `BindByItemUUID()` 入口统一先归一化 `req.ItemUUID`。

## 3. 为什么不是只用 SQL 忽略大小写
- PostgreSQL 没有通用“全局忽略大小写等号”开关。
- `ILIKE` 更适合模糊匹配，不适合设备唯一标识等值查询。
- `UPPER(column) = UPPER(?)` 可用，但如果作为唯一主方案，会把“脏数据已存在”长期留在业务链路里。
- 因此最佳实践是：
  - 存储规范统一为大写；
  - 入参统一为大写；
  - SQL 忽略大小写仅作为历史兼容兜底。
