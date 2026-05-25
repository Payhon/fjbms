# FEAT-0051 4G模块 OTA 升级包管理 - 实施记录

- status: in_progress
- owner: payhon
- last_updated: 2026-05-18
- related_feature: FEAT-0051
- version: v0.1.0

## 2026-05-07
- 扩展 OTA 升级包模型与请求结构，新增 `OTADeviceKind4GModule=3` 和 `is_latest`。
- 新增 `backend/sql/54.sql`，同步更新 `backend/sql/1.sql` 与数据库模型文档。
- 后端管理接口支持 4G 模块升级包创建、更新与 latest 唯一化。
- 新增公开接口 `GET /api/v1/ota/4g-module/check`。
- 公开接口租户 ID 支持 Query `tenant_id`，并继续兼容 Header `X-Tenant-ID` / `X-TenantID`。
- 公开接口设备标识入参由 `iccid` 调整为 `imei`，后端匹配 `device_batteries.imei`。
- 前端升级包管理页新增 `4G模块升级包` Tab 与固件 URL 复制能力。
- 新增 4G OTA 检查与 latest 唯一化单测。

## 2026-05-18
- 公开接口 `imei` 入参匹配规则调整为 `device_batteries.comm_chip_id` 或 `device_batteries.imei` 任一命中。
- 同步更新 `doc/4g_module_ota_api.md` 与 4G OTA 检查单测。
