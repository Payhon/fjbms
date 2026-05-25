# FEAT-0053 BMS OTA 升级包约束匹配 - 实施记录

- status: in_progress
- owner: payhon
- last_updated: 2026-05-13
- related_feature: FEAT-0053
- version: v0.1.0

## 2026-05-13
- 新增 `backend/sql/55.sql`，为 `ota_upgrade_packages` 增加 BMS 型号、批号、序列号约束字段与索引。
- 后端 OTA 包模型、请求结构和列表响应增加约束字段。
- BMS 包创建校验移除 `device_config_id` 必填要求。
- APP BMS OTA 检测改为基于约束字段排序匹配升级包。
- 后台 BMS 升级包表单移除设备配置、说明、附加信息，新增三个可选约束字段。
- UniApp OTA 检测请求补充 `battery_model_id`、`batch_number`、`item_uuid`。
- 新增约束匹配单测。
- 已通过后端定向单测、前端 typecheck 与 UniApp TypeScript 校验。
- 生产排查确认 APP OTA 检测在包匹配前被设备详情权限校验拦截；已调整 `CheckBatteryOtaForApp`，升级检测不再判断用户对设备的绑定/组织访问权限，只保留租户范围内的设备基础信息读取与升级包匹配。
- 新增回归测试覆盖组织用户无设备绑定记录时仍可获得 OTA 检测结果。
