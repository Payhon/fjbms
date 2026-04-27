# FEAT-0047 BMS 分页修复与电池详情操作记录 Tab - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-04-22
- related_feature: FEAT-0047
- version: v0.1.0

## 1. 本次变更
- 修复后台 BMS 运营管理部分页面分页无法翻页的问题。
- 电池详情页在 BMS 模式下新增 `操作记录` Tab，可查看当前电池的生命周期运营日志。
- 新增电池详情页 `操作记录` 页面元素权限。

## 2. 发布影响
- 后端新增 `GET /api/v1/battery/operation_logs` 可选参数 `device_id`，兼容旧调用。
- 需执行新增 SQL：
  - `backend/sql/51.sql`
- 全量初始化场景需同步使用更新后的：
  - `backend/sql/1.sql`

## 3. 验收关注点
- 运营管理分页是否按总数正确显示页码。
- 电池详情 `操作记录` Tab 是否仅对有权限用户显示。
- `PACK_FACTORY`、`DEALER` 默认是否已具备该权限。
