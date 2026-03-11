# FEAT-0012 电芯品牌与电池型号管理（租户维度）- 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-03-09
- related_feature: FEAT-0012
- version: v0.1.0

## 发布内容
- 新增：电芯品牌管理（租户全局）页面与接口。
- 改造：电池型号管理（机构维度、行内增删改、无分页）。
- 新增：BMS型号管理（租户维度）页面与接口，管理 `battery_bms_models`。
- 文案：电池列表“添加电池”调整为“新增 BMS”。
- 数据层：历史 `battery_models` 重命名为 `battery_bms_models`（BMS 板型号）；新建机构维度 `battery_models`（PACK 电池型号）；新增 `battery_cell_brands`（电芯品牌）。
- 权限层：新增菜单 `bms_battery_cell_brand`、`bms_battery_bms_model`，并补齐 PACK 厂家 `bms_battery_model` 菜单码。

## 升级步骤
1. 执行数据库迁移（新增 `41.sql`）。
2. 发布后端服务。
3. 发布前端静态资源。

## 回滚说明
- 回滚前端构建版本。
- 回滚后端版本。
- 视情况回退 `41.sql`（先评估数据影响）。
