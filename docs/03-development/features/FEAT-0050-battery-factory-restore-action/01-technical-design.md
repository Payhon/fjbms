# FEAT-0050 电池列表新增“恢复出厂”操作 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-04-28
- related_feature: FEAT-0050
- version: v0.1.0

## 1. 方案概览
- 新增独立生命周期接口 `POST /api/v1/battery/factory_restore`，不复用回退接口。
- 权限口径复用“出厂”规则：有组织时必须为 `BMS_FACTORY`，无组织管理员维持现有放行口径。
- 恢复目标固定为厂家库存（`owner_org_id=NULL`）。

## 2. 关键流程
1. 校验设备与 `device_batteries` 存在。
2. 校验当前库存不是厂家库存（`owner_org_id` 非空，且当前归属组织不是 `BMS_FACTORY`）。
3. 更新 `device_batteries.owner_org_id = NULL`。
4. 插入 `device_org_transfers`：`from_org_id=原持有方, to_org_id=NULL`。
5. 插入 `battery_operation_logs`：`operation_type=FACTORY_RESTORE`，描述 `恢复出厂：{当前机构} -> 厂家`。

## 3. 前端交互
- 生命周期菜单新增“恢复出厂”按钮（厂家视角行级展示）。
- 点击后弹出确认框：展示电池编号、当前机构、恢复目标（厂家库存）、备注。
- 提交成功后刷新列表。

## 4. 权限与配置
- 新增权限码：`bms_battery_list_action_lifecycle_factory_restore`。
- 增量 SQL：`backend/sql/53.sql`，并同步 `backend/sql/1.sql`。
- `org_type_permissions` 仅自动补齐到 `BMS_FACTORY`。

## 5. 测试策略
- 后端定向：成功恢复、已在厂家库存拒绝、非厂家权限拒绝、三处落账一致。
- 前端定向：入口显示、弹窗确认、成功刷新、日志筛选项可见。
