# FEAT-0014 电池信息补全（电芯品牌/电池型号）- 实现记录

- status: in_progress
- owner: payhon
- last_updated: 2026-03-18
- related_feature: FEAT-0014
- version: v0.1.0

## 变更记录
- 2026-03-13：
  1) 新增 SQL 补丁 `backend/sql/44.sql`，为 `device_batteries` 增加 `cell_brand_seq_no`、`battery_model_seq_no` 字段，并补充两个按钮权限。
  2) 后端扩展电池列表/导出查询，新增电芯品牌与 PACK 电池型号筛选、展示字段。
  3) 新增 `POST /api/v1/battery/complete-info`，支持单条/批量信息补全，并限制 PACK 厂家/租户管理员调用。
  4) 电池运营日志新增 `INFO_COMPLETE` 操作类型，信息补全成功后按设备逐条写入日志。
  5) 前端电池列表新增批量“电池信息补全”按钮、生命周期子菜单“信息补全”、筛选项与展示列。
  6) 新增独立组件 `BatteryModelSelect`，支持只读选择与原地新增型号。
  7) 电池详情页新增 `基本信息` 标签页，展示新增 BMS 表单的只读字段；后端详情接口补齐 `batch_number`、`product_spec`、`order_number`、`production_date`、`warranty_expire_date`、`remark`。
  8) 修复“新增 BMS”备注未持久化问题，保存时同步写入 `devices.remark1`，便于详情页查看。
  9) 电池列表操作菜单新增 `编辑 BMS 信息`、`删除`，前者复用新增 BMS 表单预填后更新，后者带不可恢复确认。
  10) 后端新增单个电池编辑接口与删除接口；删除操作采用事务清理主要关联业务表，并写入 `EDIT_INFO`、`DELETE` 运营日志。
  11) 电池列表 `BMS型号` 后新增 `产品规格` 列，并将第 1~2 列固定，提升宽表滚动体验。
  12) 电池列表首个搜索条件改为“字段下拉 + 文本值”，后端列表/导出接口新增 `search_field` + `search_value` 通用文本检索，支持序列号、批号、BMS型号、产品规格、蓝牙MAC、4G卡ID模糊查询。
