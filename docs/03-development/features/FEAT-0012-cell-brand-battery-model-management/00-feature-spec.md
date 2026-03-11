# FEAT-0012 电芯品牌与电池型号管理（租户维度）- 功能规格

- status: in_progress
- owner: payhon
- last_updated: 2026-03-09
- related_feature: FEAT-0012
- version: v0.1.0

## 1. 背景与目标
- 背景：原 `battery_models` 实际承载的是 BMS 板型号；当前需求中的“电池型号”与其字段不对齐，需要拆分独立表管理。
- 目标：
  1) 新增电芯品牌管理（租户全局）。
  2) 改造电池型号管理为 PACK 厂家自维护（按当前登录用户所属机构隔离）。
  3) 在 BMS 管理下新增“BMS型号管理”菜单，恢复原电池型号管理能力（对应 `battery_bms_models`）。
  4) 电池列表“添加电池”按钮文案改为“新增 BMS”。
  5) 前端采用单页行内增删改（不分页、无弹窗）用于电芯品牌与PACK电池型号；BMS型号管理沿用原有 CRUD 形态。

## 2. 范围
### In Scope
- 后端：
  - 新增 `battery_cell_brands` 表与 CRUD API。
  - 将原 `battery_models` 迁移为 `battery_bms_models`（BMS 板型号）。
  - 新建 `battery_models`（电池型号，机构维度）并提供 CRUD。
  - 新增 BMS 型号管理 API（`/api/v1/battery/bms-model`）对 `battery_bms_models` 提供 CRUD。
- SQL：新增迁移脚本，补充菜单项与权限文案。
- 前端：
  - 新增“电芯品牌管理”页面。
  - “电池型号管理”页面改为行内编辑。
  - 电池列表按钮文案改为“新增 BMS”。

### Out of Scope
- 不改动设备详情页展示结构。
- 不改动 BLE 协议字段。
- 不改造现有电池导入模板字段结构。

## 3. 业务规则
1. 电芯品牌：`tenant_id + seq_no` 唯一，`tenant_id + name` 唯一。
2. 电池型号：`tenant_id + org_id + seq_no` 唯一，`tenant_id + org_id + name` 唯一（历史兼容数据允许 `org_id` 为空）。
3. 序号范围：`1~255`。
4. 电芯品牌名长度：`<=16`。
5. 电池型号机构ID默认取当前登录用户所属机构ID。

## 4. 验收标准
1. 租户管理员可在“电芯品牌管理”页面行内新增/编辑/删除品牌。
2. PACK 厂家用户可在“电池型号管理”页面行内新增/编辑/删除本机构型号。
3. 电池列表顶部按钮显示为“新增 BMS”。
4. 两个管理页面均无分页、无弹窗，直接在表格行内操作。
5. 租户管理员可在 “BMS型号管理” 菜单完成 BMS 型号的新增/编辑/删除/查询。

## 5. 风险与回滚
- 风险：历史 `battery_models` 数据迁移为 `battery_bms_models` 后，若未同步回填新 `battery_models`，设备列表型号名称会丢失。
- 回滚：
  1) 回滚前端新页面与电池型号页改造。
  2) 回滚后端新接口与字段写入逻辑。
  3) 回滚 SQL 迁移（删除新增菜单与新表，移除新增字段索引）。
