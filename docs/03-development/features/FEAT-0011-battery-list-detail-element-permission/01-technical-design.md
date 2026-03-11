# FEAT-0011 电池列表详情路由与元素权限补齐 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-03-08
- related_feature: FEAT-0011
- version: v0.1.0

## 1. 方案概览
- 后端新增 `GET /api/v1/org_type_permissions/ui_codes/me`，返回当前用户有效 UI 权限编码（含 `allow_all`）。
- `org_type_permissions` 权限补齐逻辑支持按钮节点（`element_type=4`）参与保存与配置树展示。
- 前端新增全局 Vue 指令 `v-ui-permission`：
  - 默认模式：无权限隐藏。
  - `disable` 模式：无权限显示但禁用。
- 电池列表页面接入指令和操作项过滤逻辑，按新增权限编码控制可见性。

## 2. 后端改造点
1. `backend/internal/service/org_type_permissions.go`
   - `expandUICodesWithAncestors` 支持 `element_type IN (1,2,3,4)`。
   - 新增 `GetCurrentUIPermissions`，按用户类型合并 `APP_USER + ORG_TYPE` 的 `ui_codes`。
2. `backend/internal/api/org_type_permissions.go`
   - 新增 `GetCurrentUIPermissions` API。
3. `backend/router/apps/org_type_permissions.go`
   - 注册 `GET /org_type_permissions/ui_codes/me`。
4. `backend/internal/dal/ui_elements.go`
   - 权限配置树查询支持按钮节点（`element_type=4`）。

## 3. SQL 方案
- 新增 `backend/sql/40.sql`：
  1) 新增 `sys_ui_elements`：
     - 路由：`bms_battery_list_detail`（指向 `view.device_details`）。
     - 按钮：导出/添加电池/导入/参数/离线指令/生命周期（出厂、激活、调拨）。
  2) 对已包含 `bms_battery_list` 的机构类型权限记录自动补齐新增编码。
- 同步将上述新增权限项补充到 `backend/sql/1.sql`。

## 4. 前端改造点
1. 新增权限能力：
   - `frontend/src/utils/common/ui-permission.ts`：缓存/加载当前用户 UI 权限。
   - `frontend/src/directives/ui-permission.ts`：权限指令实现。
   - `frontend/src/directives/index.ts` + `frontend/src/main.ts`：全局注册指令。
2. 电池列表页面：
   - `frontend/src/views/bms/battery/list/index.vue`：
     - 顶部按钮通过 `v-ui-permission` 控制。
     - 操作下拉菜单按权限编码过滤。
3. API 封装：
   - `frontend/src/service/api/org-type-permissions.ts` 新增当前用户 UI 权限接口定义。

## 5. 测试策略
- 后端：`go test ./internal/... ./router/...`
- 前端：`pnpm exec eslint --no-warn-ignored ...` + `pnpm typecheck`
- 手工：使用 PACK/经销商/门店账号验证详情页跳转与按钮显隐。
