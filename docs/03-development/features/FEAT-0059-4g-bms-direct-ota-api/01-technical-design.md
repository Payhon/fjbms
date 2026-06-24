# FEAT-0059 4G BMS 直连 OTA HTTP 接口 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-06-15
- related_feature: FEAT-0059
- version: v0.1.0

## 1. 方案概览
- 在公共 `v1` 路由下新增 `GET /api/v1/ota/4g-bms/check`，与 `ota/4g-module/check` 同级。
- 请求模型新增 `GetOTA4GBMSUpgradeCheckReq`，响应模型新增 `OTA4GBMSUpgradeCheckResp`。
- 服务层新增 `OTA.Check4GBMSUpgrade`，按 `tenant_id + item_uuid` 校验设备归属后查询 BMS 升级包。

## 2. 接口与数据结构
- Query 参数：
  - `tenant_id`：条件必填，也可从 Header 获取。
  - `item_uuid`：必填，对应 `device_batteries.item_uuid`。
  - `version`：必填，BMS 板当前固件版本。
  - `imei`、`comm_chip_id`：可选，保留为现场排查参数，不参与主匹配。
- 响应沿用统一 `code/message/data` 包装，`data` 返回升级状态、固件 URL、包 ID、版本、目标版本、签名、包类型、模块和附加信息。

## 3. 关键流程
- API 层复用公开 OTA 租户解析逻辑：Query `tenant_id` > `X-Tenant-ID` > `X-TenantID`。
- 服务层查询 `devices` 与 `device_batteries`，只允许当前租户下命中的 `item_uuid` 继续检测。
- 候选包限定为 `(tenant_id = 当前租户 OR tenant_id IS NULL) AND device_kind = 1`。
- 复用现有 BMS OTA 选择器：`target_version` 必须匹配，约束字段全部满足，按约束精确度、版本号、创建时间选包。
- 下载地址复用 `buildOtaDownloadURL`，外部 URL 原样返回，内部路径按 `ota.download_address` 拼接。

## 4. 安全与权限
- 不要求登录 Token，但必须传租户并命中当前租户设备。
- 不返回其他租户设备或升级包信息。
- 不下发 MQTT 指令，不创建任务记录，降低公开接口副作用。

## 5. 测试策略
- 后端 service 单测覆盖租户缺失、设备不存在、`device_kind` 过滤、`target_version` 过滤和 BMS 约束优先级。
- 后端 API 单测沿用租户解析测试。
- 执行定向 `go test` 和 `git diff --check`。
