# FEAT-0012 电芯品牌与电池型号管理（租户维度）- 实现记录

- status: in_progress
- owner: payhon
- last_updated: 2026-03-10
- related_feature: FEAT-0012
- version: v0.1.0

## 2026-03-09
- 完成规格与技术设计初稿。
- 完成后端/前端联动开发：
  1) 后端新增 `battery_cell_brands` 模型、服务、API、路由（`/api/v1/battery/cell-brand`）。
  2) 数据层拆分：历史 `battery_models` 迁移为 `battery_bms_models`（BMS 板型号），新建 `battery_models` 承载机构维度电池型号。
  3) 电池型号接口改造为 `seq_no + name + org_id(当前登录用户所属机构)` 核心管理模式，并增加机构权限隔离。
  4) SQL 新增 `backend/sql/41.sql`：表重命名/新建、历史数据回填、菜单 `bms_battery_cell_brand`、按钮文案“新增BMS”、PACK 权限补齐。
  5) 前端新增“电芯品牌管理”页面（行内增删改、无分页）。
  6) 前端改造“电池型号管理”页面为行内增删改、无分页，移除弹窗流程。
  7) 电池列表按钮文案改为“+ 新增 BMS”。
  8) 按产品澄清完成模型拆分落地：历史 `battery_models` 明确为 BMS 板型号，迁移后命名为 `battery_bms_models`；新 `battery_models` 专用于机构维度电池型号。
  9) 兼容性修正：补齐 `sql/31.sql` 对拆表前后结构的自适应处理，避免新 `battery_models` 被回写 `device_config_id` 字段。
  10) 关联逻辑修正：电池单个新增/批量导入在 PACK 电池型号基础上，优先按 ID 再按名称回查 BMS 板型号，继承 `device_config_id` 与质保月数（若存在）以保持历史行为兼容。
  11) OTA 检查修正：移除对新 `battery_models` 不存在字段 `device_config_id` 的直接查询，改为通过 BMS 板型号回查设备模板。
  12) 新增 BMS 型号管理能力：新增后端 API `/api/v1/battery/bms-model`，实现 `battery_bms_models` 的增删改查。
  13) 新增前端菜单与页面：`BMS型号管理`（`/bms/battery/bms-model`），沿用原电池型号管理交互（查询+分页+弹窗编辑）。
  14) 菜单 SQL 补齐：在 `sql/1.sql` 与 `sql/41.sql` 增加 `bms_battery_bms_model` 菜单项，限定租户管理员可见。
  15) 组织列表分页校验修正：`GET /api/v1/org` 的 `page_size` 上限由 100 放宽到 1000，兼容 BMS 管理 > 电池型号管理 页面按 `org_type=PACK_FACTORY` 拉取全量 PACK 厂家选项。
  16) “新增 BMS”表单口径修正：
      - `frontend/src/views/bms/battery/modules/battery-single-modal.vue`
      - `frontend/src/views/bms/battery/list/index.vue`
      - `backend/internal/service/battery_single_create.go`
      - 新增弹窗中的型号下拉改为读取 `battery_bms_models`（BMS 型号），后端单个新增兼容按 BMS 型号 ID / 名称解析并写入，避免表单仍误用机构电池型号列表。

## 待补充
- 测试环境 SQL 执行记录（待联调环境补录）。
- 租户联调记录（待补录）。
