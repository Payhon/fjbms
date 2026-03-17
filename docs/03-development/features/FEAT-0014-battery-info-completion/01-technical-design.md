# FEAT-0014 电池信息补全（电芯品牌/电池型号）- 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-03-13
- related_feature: FEAT-0014
- version: v0.1.0

## 1. 方案概览
- `device_batteries` 新增两个字段：
  - `cell_brand_seq_no`
  - `battery_model_seq_no`
- 电池列表查询在保留历史 `battery_model_id` / BMS 型号逻辑的同时，新增电芯品牌和 PACK 电池型号的关联查询与展示。
- 后端新增 `POST /api/v1/battery/complete-info`，支持单条/批量统一补全。
- 前端新增独立 `BatteryModelSelect` 组件：
  - 只读模式：仅选择已有型号。
  - 可创建模式：允许在组件内原地新增型号后自动刷新选项。
- 电池详情页在 BMS 电池详情模式下新增 `基本信息` Tab，复用电池详情接口展示新增 BMS 表单字段。
- 电池列表操作菜单新增 `编辑 BMS 信息` 与 `删除`，其中删除采用事务删除业务关联数据并保留运营日志审计。

## 2. 接口与数据结构
### 2.1 数据库
- `device_batteries`
  - `cell_brand_seq_no smallint`
  - `battery_model_seq_no smallint`
- 说明：
  - `cell_brand_seq_no` 关联 `battery_cell_brands.seq_no`
  - `battery_model_seq_no` 关联 `battery_models.seq_no`
  - 均通过 `tenant_id + seq_no` 运行时关联；电池型号额外受 `org_id` 约束

### 2.2 后端接口
- 新增 `POST /api/v1/battery/complete-info`
  - 请求：
    - `device_ids: []string`
    - `cell_brand_seq_no: int16`
    - `battery_model_seq_no: int16`
  - 响应：成功数量/总数
- 扩展 `GET /api/v1/battery`
  - 新增筛选：
    - `cell_brand_seq_no`
    - `battery_model_seq_no`
  - 新增返回字段：
    - `cell_brand_seq_no`
    - `cell_brand_name`
    - `battery_model_seq_no`
    - `pack_battery_model_name`
- 扩展 `GET /api/v1/battery/export`
  - 导出列增加电芯品牌、PACK 电池型号
- 扩展 `GET /api/v1/app/battery/detail/{device_id}`
  - 新增返回字段：
    - `batch_number`
    - `product_spec`
    - `order_number`
    - `production_date`
    - `warranty_expire_date`
    - `remark`
- 新增 `PUT /api/v1/battery/single/{id}`
  - 复用新增 BMS 请求体，按 `device_id` 更新设备编号与 `device_batteries` 扩展信息
- 新增 `DELETE /api/v1/battery/{id}`
  - 事务删除设备及主要关联业务表记录，并写入 `DELETE` 运营日志

## 3. 关键流程
1. 用户在电池列表勾选一条或多条设备，点击“电池信息补全”。
2. 前端弹出补全弹窗，加载并展示当前选中设备的基础信息。
3. 用户选择电芯品牌和电池型号；必要时在电池型号选择器中原地新增型号。
4. 前端提交 `/api/v1/battery/complete-info`。
5. 后端校验权限、品牌存在性、型号可见性后更新 `device_batteries`。
6. 后端为每台设备写入一条运营日志，操作类型为 `INFO_COMPLETE`。
7. 列表刷新后展示新字段，并支持按新增条件筛选。
8. 电池详情页 `基本信息` Tab 通过详情接口读取新增 BMS 表单的只读数据，与 `BMS面板` 并列展示。
9. 电池列表“编辑 BMS 信息”操作打开复用表单，预填当前设备信息并提交更新接口。
10. 电池列表“删除”操作经二次确认后调用删除接口，删除后刷新列表与勾选状态。

## 4. 安全与权限
- 前端按钮权限：
  - `bms_battery_list_batch_info_complete`
  - `bms_battery_list_action_lifecycle_info_complete`
- 后端接口权限：
  - 仅 `PACK_FACTORY`、`TENANT_ADMIN`、`SYS_ADMIN` 可调用。
  - `PACK_FACTORY` 只能选择本机构 `battery_models`。
  - 租户管理员创建型号时必须指定归属 PACK 厂家。
- “新增 BMS” 的备注字段持久化到 `devices.remark1`，用于详情页只读展示。
- 电池删除时保留 `battery_operation_logs` 作为审计记录；`latest_device_alarms` 为数据库视图，不参与物理删除，其余主要设备业务数据在同一事务内删除。

## 5. 测试策略
- 后端：
  - `go test ./...`
  - 重点回归电池列表查询、信息补全接口、运营日志查询
- 前端：
  - `pnpm lint`
  - `pnpm build`
- 手工联调：
  - 批量补全
  - 单条补全
  - 权限显隐
  - 原地新增型号
  - 查询筛选与导出字段

## 6. 兼容性与迁移
- 历史数据无补全字段时按空值展示，不影响现有列表查询与生命周期操作。
- 继续保留原列表“BMS 型号”字段所依赖的 `battery_model_id` 逻辑，避免影响已有导入、单个新增和 OTA 关联流程。
- 新 SQL 通过 `IF NOT EXISTS` 方式新增字段与权限项，兼容已部署环境的增量执行。
