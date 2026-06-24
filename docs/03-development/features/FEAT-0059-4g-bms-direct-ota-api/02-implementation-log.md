# FEAT-0059 4G BMS 直连 OTA HTTP 接口 - 实施记录

- status: in_progress
- owner: payhon
- last_updated: 2026-06-15
- related_feature: FEAT-0059
- version: v0.1.0

## 1. 实施内容
- 新增公开路由 `GET /api/v1/ota/4g-bms/check`。
- 新增 4G BMS 直连 OTA 请求/响应模型。
- 新增 `OTA.Check4GBMSUpgrade` 服务方法。
- 复用现有 BMS OTA 包选择器和下载 URL 构造逻辑。
- 新增 service 单测覆盖核心匹配规则。
- 更新 `doc/4g_bms_ota_api.md`，明确约束优先级与现有 BMS OTA 一致。

## 2. 影响范围
- 后端 OTA 公共检测接口。
- BMS OTA 升级包读取链路。
- 不影响 APP 登录态 OTA 检测、批量 OTA 任务、4G 模块 OTA 检测和 MQTT Socket 透传链路。

## 3. 验证记录
- `cd backend && go test ./internal/api ./internal/service -run 'TestResolve4GModuleTenantID|TestCheck4GBMSUpgrade|TestCheck4GModuleUpgrade|TestSelectAppBatteryOtaPackage' -count=1` 通过。
- 空白检查通过。
