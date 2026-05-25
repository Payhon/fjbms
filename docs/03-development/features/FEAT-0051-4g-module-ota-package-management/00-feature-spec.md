# FEAT-0051 4G模块 OTA 升级包管理 - 功能规格

- status: in_progress
- owner: payhon
- last_updated: 2026-05-18
- related_feature: FEAT-0051
- version: v0.1.0

## 1. 背景与目标
- 当前 OTA 升级包管理已支持 BMS 与仪表设备，4G 模块自身固件缺少独立管理与升级检查能力。
- 目标：
  1. 在后台升级包管理中新增 `4G模块升级包` Tab。
  2. 支持 4G 模块升级包的版本、固件 URL、说明与最新固件标记。
  3. 提供无需登录、基于租户 ID 的 4G 模块升级检查接口。

## 2. 范围
### In Scope
- 扩展 `ota_upgrade_packages.device_kind=3` 表示 4G 模块升级包。
- 新增 `is_latest` 字段并保证同租户 4G 模块最多一个最新包。
- 后台升级包管理页新增 4G 模块 Tab、固件 URL 展示和复制。
- 新增 `GET /api/v1/ota/4g-module/check`。

### Out of Scope
- 不实现 4G 模块升级任务下发。
- 不新增独立 4G 模块升级包表。
- 不改造 BMS 与仪表 OTA 升级流程。

## 3. 验收标准
1. 后台可新增、编辑、删除 4G 模块升级包。
2. 4G 模块升级包列表展示固件 URL，并可复制到剪贴板。
3. 同租户下保存一个 4G 包为最新固件时，其他 4G 包自动取消最新标记。
4. 未登录调用升级检查接口不触发 JWT 校验。
5. 接口缺少租户 ID 时返回参数错误。
6. 接口按 `version + imei + tenant_id` 返回是否需要升级与固件 URL，租户 ID 可通过 Query 或 Header 传递；`imei` 入参匹配 `device_batteries.comm_chip_id` 或 `device_batteries.imei`，任一字段命中即可。

## 4. 风险与约束
- 公开接口仍依赖租户 ID 隔离数据，调用方必须传 Query `tenant_id`、Header `X-Tenant-ID` 或兼容头 `X-TenantID`。
- 多个更高版本包同时存在时，必须人工标注 `is_latest=true` 才返回升级包。

## 5. 回滚方案
- 回滚前后端 4G 模块升级包入口与公开检查接口。
- 回滚 `54.sql` 中新增字段和索引前需确认没有生产 4G 包数据依赖。
