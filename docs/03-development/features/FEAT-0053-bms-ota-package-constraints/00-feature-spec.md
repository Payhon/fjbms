# FEAT-0053 BMS OTA 升级包约束匹配 - 功能规格

- status: in_progress
- owner: payhon
- last_updated: 2026-05-13
- related_feature: FEAT-0053
- version: v0.1.0

## 1. 背景与目标
- 现有 BMS OTA 检测按设备配置匹配升级包，无法针对 BMS 型号、批号或单台序列号发布差异化固件。
- 目标：
  1. 后台 BMS 升级包支持配置可选约束：BMS 型号、批号、序列号。
  2. APP 升级检测上送设备约束字段。
  3. 后端按约束精确度选择最合适的升级包。

## 2. 范围
### In Scope
- 扩展 `ota_upgrade_packages` 约束字段。
- 调整后台 BMS 升级包表单与列表展示。
- 调整 APP BMS OTA 检测请求。
- 调整后端 BMS OTA 检测匹配规则。

### Out of Scope
- 不改造仪表 OTA 升级包链路。
- 不改造 4G 模块 OTA 升级包链路。
- 不删除历史 `device_config_id` 字段。

## 3. 验收标准
1. 后台 BMS 包表单不再展示设备配置、说明、附加信息。
2. 后台 BMS 包表单底部展示 BMS 型号、批号、序列号三个可选约束。
3. APP OTA 检测请求携带 `battery_model_id`、`batch_number`、`item_uuid`。
4. 后端优先返回三字段全匹配包，其次两字段全匹配包，再按 `item_uuid > battery_model_id > batch_number` 返回单字段匹配包。
5. 没有约束命中时，无约束通用包仍可返回。
6. `target_version` 不匹配当前版本的升级包不会返回。

## 4. 风险与约束
- 历史无约束 BMS 包会继续作为通用包参与匹配。
- 同一优先级内按版本号最高、创建时间最新选择。
- 新字段为可空字段，生产迁移不影响历史包读取。

## 5. 回滚方案
- 回滚后端、前端和 UniApp 代码。
- 如需数据库回滚，确认没有使用约束字段的 BMS 包后再删除 `ota_upgrade_packages` 的三个新增字段和索引。
