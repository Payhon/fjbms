# FEAT-0047 BMS 分页修复与电池详情操作记录 Tab - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-04-22
- related_feature: FEAT-0047
- version: v0.1.0

## 1. 设计概览
- 分页修复采用最小变更策略：仅对确认走服务端分页的 `NDataTable` 显式启用远程分页模式，不改动原有查询参数与返回结构。
- 电池详情操作记录直接复用现有 `battery_operation_logs` 数据源，不额外引入聚合表或系统日志拼接逻辑。
- 详情 Tab 权限采用现有 `org_type_permissions.ui_codes/me + v-ui-permission/hasUiPermission` 体系。

## 2. 后端设计
### 2.1 `battery_operation_logs` 查询扩展
- 接口：`GET /api/v1/battery/operation_logs`
- 新增参数：`device_id?: string`
- 服务层在现有过滤条件基础上追加 `bol.device_id = ?`。
- 组织隔离保持不变：
  - 按 `tenant_id` 过滤；
  - 若存在组织上下文，仅查询当前机构子树下设备。

### 2.2 日志口径
- 详情页只展示 `battery_operation_logs`。
- 本轮沿用现有日志类型：
  - `CREATE`
  - `IMPORT`
  - `FACTORY_OUT`
  - `TRANSFER`
  - `ROLLBACK`
  - `ACTIVATE`
  - `INFO_COMPLETE`
  - `EDIT_INFO`
  - `DELETE`
  - `WARRANTY_SUBMIT`
  - `WARRANTY_HANDLE`
  - `MAINTENANCE_SUBMIT`
  - `MAINTENANCE_HANDLE`

## 3. 前端设计
### 3.1 分页修复
- 对以下页面的 `NDataTable` 增加 `remote`：
  - `frontend/src/views/bms/ops/operation_log/index.vue`
  - `frontend/src/views/bms/ops/activation_log/index.vue`
  - `frontend/src/views/bms/battery/bms-model/index.vue`
  - `frontend/src/views/management/api/index.vue`
  - `frontend/src/components/EndUserSelect.vue`

### 3.2 电池详情 Tab 装配
- 在 `frontend/src/views/device/details/index.vue` 的 BMS 模式 Tab 列表中插入：
  - `BMS面板`
  - `基本信息`
  - `操作记录`
  - `连接`
- 新增组件 `frontend/src/views/device/details/modules/battery-operation-log.vue`。
- 组件只接收当前 `device_id`，内部自行分页请求 `/battery/operation_logs?device_id=...`。

### 3.3 权限控制
- 权限码：`bms_battery_detail_operation_log`
- 页面装配时通过 `hasUiPermission('bms_battery_detail_operation_log')` 判断是否插入 Tab。
- 初次进入 BMS 详情页前先调用 `ensureUiPermissionState()`，避免无权限用户短暂看到 Tab。

## 4. SQL 与多语言
- 新增增量 SQL：`backend/sql/51.sql`
- 汇总种子：`backend/sql/1.sql`
- locale：
  - `frontend/src/locales/langs/zh-cn/route.json`
  - `frontend/src/locales/langs/en-us/route.json`

## 5. 兼容性
- 新增接口参数为可选字段，不影响现有运营日志页面调用。
- 无权限用户保持现有详情页结构，只是缺少新 Tab。
