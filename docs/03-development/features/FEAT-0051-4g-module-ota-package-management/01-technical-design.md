# FEAT-0051 4G模块 OTA 升级包管理 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-05-18
- related_feature: FEAT-0051
- version: v0.1.0

## 1. 数据模型
- 复用 `ota_upgrade_packages`。
- `device_kind` 扩展为：`1=BMS`、`2=仪表`、`3=4G模块`。
- 新增 `is_latest boolean not null default false`。
- 新增唯一索引：同租户 `device_kind=3 AND is_latest=true` 最多一条。

## 2. 后端接口
- 管理接口复用 `/api/v1/ota/package`，支持 `device_kind=3` 与 `is_latest`。
- 保存 4G 包且 `is_latest=true` 时，事务内将同租户其他 4G 包更新为 `false`。
- 公开接口：
  - `GET /api/v1/ota/4g-module/check`
  - Query：`version`、`imei`
  - Query：`tenant_id`，兼容 Header `X-Tenant-ID` / `X-TenantID`
  - Response：`need_upgrade`、`current_version`、`version`、`firmware_url`、`package_id`、`name`、`description`、`is_latest`、`imei`

## 3. 升级包选择
- 先通过 `devices.tenant_id + (device_batteries.comm_chip_id OR device_batteries.imei)` 确认 `imei` 入参属于当前租户。
- 查找当前租户或公共的 `device_kind=3` 包。
- 只考虑版本号大于入参 `version` 的包。
- 若只有一个候选包，直接返回。
- 若有多个候选包，只返回 `is_latest=true` 的包；没有最新标记则 `need_upgrade=false`。

## 4. 前端
- `frontend/src/views/bms/battery/ota/package/index.vue` 新增第三个 Tab。
- 4G 表单字段为名称、版本号、固件、说明、是否最新固件。
- 三类升级包列表均展示固件 URL 与复制按钮。
