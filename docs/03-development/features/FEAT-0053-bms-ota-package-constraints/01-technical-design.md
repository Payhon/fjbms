# FEAT-0053 BMS OTA 升级包约束匹配 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-05-13
- related_feature: FEAT-0053
- version: v0.1.0

## 1. 方案概览
- BMS OTA 包不再通过 `device_config_id` 适配设备。
- BMS OTA 包新增三个可选约束：`battery_model_id`、`batch_number`、`item_uuid`。
- APP 检测接口从设备详情中携带上述字段，后端缺失时回退查询 `device_batteries`。

## 2. 接口与数据结构
- `ota_upgrade_packages` 新增：
  - `battery_model_id varchar(36)`
  - `batch_number varchar(100)`
  - `item_uuid varchar(64)`
- `POST/PUT /api/v1/ota/package` 支持 BMS 包写入三个约束字段。
- `POST /api/v1/app/battery/ota/check` 支持：
  - `battery_model_id`
  - `batch_number`
  - `item_uuid`

## 3. 关键流程
- 后台 BMS 表单保存时只提交版本、目标版本、模块、包类型、签名算法、固件、备注和三个约束字段。
- 后端查询 BMS 候选包时只限制租户与 `device_kind=1`。
- 匹配规则：
  1. 配置了约束的包必须全部匹配。
  2. 三字段全匹配优先于两字段全匹配。
  3. 单字段约束按 `item_uuid > battery_model_id > batch_number` 排序。
  4. 无约束包作为通用兜底。
  5. 同级别按版本号最高、创建时间最新选择。

## 4. 安全与权限
- 管理接口沿用现有 OTA 包权限与租户隔离。
- APP 检测接口不再复用设备详情的绑定/组织访问权限校验；只按请求登录态解析出的租户范围读取设备基础信息并返回升级检测结果。
- 设备详情、遥测、MQTT 透传等其他 APP 接口继续沿用原有设备访问权限校验。

## 5. 测试策略
- 后端单测覆盖校验规则、约束匹配排序、通用包兜底和 `target_version` 过滤。
- 前端执行 `pnpm typecheck`。
- UniApp 执行 `pnpm exec tsc --noEmit`。

## 6. 兼容性与迁移
- 保留 `device_config_id` 字段，BMS 新建/编辑包写空值。
- 历史 BMS 包无约束字段时作为通用包继续生效。
