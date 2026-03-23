# FEAT-0024 item_uuid 大小写归一化防重复注册 - 实现日志

- status: in_progress
- owner: payhon
- last_updated: 2026-03-23
- related_feature: FEAT-0024

## 2026-03-23
- 新增功能规格与技术设计，明确“前端先归一化、后端兜底并统一写入大写”的策略。
- 已修改 UniApp BLE `readUuid()`，统一返回大写十六进制 UUID。
- 已修改 UniApp `service/deviceProvision.ts`，对 `provision/info` 与 `provision/bind` 请求参数中的 `item_uuid` 统一执行大写归一化。
- 已修改后端 `internal/service/device_provision.go`：
  - 新增 `normalizeItemUUID()`
  - `GetProvisionInfo()` / `BindByItemUUID()` 入口统一归一化
  - `findDeviceByItemUUIDWithDB()` 先按规范值精确查询，再按 `UPPER(dbat.item_uuid)` 兜底兼容历史小写数据
  - `createAutoRegisteredDevice()` 自动补建写入统一使用大写 `item_uuid`
- 已新增后端单元测试 `TestNormalizeItemUUID`。
