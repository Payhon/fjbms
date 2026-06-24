# FEAT-0059 4G BMS 直连 OTA HTTP 接口 - 功能规格

- status: in_progress
- owner: payhon
- last_updated: 2026-06-15
- related_feature: FEAT-0059
- version: v0.1.0

## 1. 背景与目标
- 4G 类型 BMS 设备需要由 BMS 板 MCU 主动通过 HTTP 获取 OTA 固件信息，不再通过 MQTT 转发执行该升级方式。
- 目标：新增公开 HTTP 检测接口，供 MCU 按租户和 `item_uuid` 获取 `device_kind=1` 的 BMS 固件下载地址。

## 2. 范围
### In Scope
- 新增 `GET /api/v1/ota/4g-bms/check`。
- 接口无需登录 Token，使用 `tenant_id` 或租户 Header 定位租户。
- 复用现有 BMS OTA 约束匹配规则，返回固件 URL、版本、签名、包类型和附加信息。
- 更新接口文档 `doc/4g_bms_ota_api.md`。

### Out of Scope
- 不创建后台 OTA 任务。
- 不通过 MQTT Topic 或 APP WebSocket 转发固件。
- 不改造 4G 模块自身 OTA 接口。

## 3. 验收标准
1. `GET /api/v1/ota/4g-bms/check` 注册为公开路由。
2. 缺少租户、`item_uuid` 或 `version` 时返回参数错误。
3. 设备不属于当前租户或不存在时返回 `need_upgrade=false`。
4. 只匹配 `device_kind=1` 的 BMS 升级包。
5. `target_version` 和 BMS OTA 三约束匹配规则与现有 APP BMS OTA 一致。

## 4. 风险与约束
- 接口公开暴露，必须使用租户 ID 和 `item_uuid` 做最小设备归属校验。
- 历史无约束 BMS 包仍会作为通用包参与匹配。

## 5. 回滚方案
- 回滚新增路由、API handler、请求/响应模型和 service 方法。
- 保留文档时需标注接口未开放；无需数据库回滚。
