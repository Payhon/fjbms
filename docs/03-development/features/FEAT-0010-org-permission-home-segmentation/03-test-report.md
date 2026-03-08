# FEAT-0010 机构菜单权限生效与首页分层改造 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-03-08
- related_feature: FEAT-0010
- version: v0.1.0

## 1. 测试范围
- 机构类型菜单权限配置生效。
- 首页分层显示（机构/终端用户）。

## 2. 结果
- [x] 后端编译/单测通过
  - 命令：`cd backend && go test ./internal/... ./router/...`
  - 结果：通过（存在 macOS `IOMasterPort` 废弃告警，不影响结果）
- [x] 前端类型检查通过
  - 命令：`cd frontend && pnpm typecheck`
  - 结果：通过
- [x] 前端变更文件 lint 通过
  - 命令：`cd frontend && pnpm exec eslint --no-warn-ignored src/service/api/bms.ts src/views/home/index.vue src/views/home/components/activation-trend-chart.vue src/views/home/components/institution-home.vue src/views/home/components/end-user-home.vue`
  - 结果：通过
- [x] 权限配置页回显修复校验通过
  - 命令：`cd frontend && pnpm exec eslint --no-warn-ignored src/views/management/permission/index.vue && pnpm typecheck`
  - 结果：通过
- [x] 动态路由规范化修复校验通过（门店/经销商快捷菜单）
  - 命令：`cd frontend && pnpm exec eslint --no-warn-ignored src/service/api/management.adapter.ts && pnpm typecheck`
  - 结果：通过
- [x] 动态路由兼容增强校验通过（`/bms/org?ORG_TYPE=...`）
  - 命令：`cd frontend && pnpm exec eslint --no-warn-ignored src/service/api/management.adapter.ts && pnpm typecheck`
  - 结果：通过
- [x] 组织快捷菜单独立页面改造校验通过
  - 命令：`cd frontend && pnpm exec eslint --no-warn-ignored src/views/bms/org/index.vue src/views/bms/org/dealer/index.vue src/views/bms/org/store/index.vue src/views/bms/org/pack-factory/index.vue src/views/bms/org/components/org-management-page.vue src/service/api/management.adapter.ts && pnpm typecheck`
  - 结果：通过
- [x] 机构首页激活曲线 Loading 修复 + Tab 合并改造校验通过
  - 命令：`cd frontend && pnpm exec eslint --no-warn-ignored src/views/home/components/institution-home.vue src/views/home/components/activation-trend-chart.vue && pnpm typecheck`
  - 结果：通过
- [x] BMS 看板告警概览 SQL 修复校验通过
  - 命令：`cd backend && go test ./internal/service -run TestBuildLatestDeviceAlarmsBase -count=1 && go test ./internal/api ./router/apps -count=1`
  - 结果：通过（存在 macOS `IOMasterPort` 废弃告警，不影响结果）
- [x] 首页身份展示与管理员视角切换改造校验通过
  - 命令：`cd frontend && pnpm exec eslint --no-warn-ignored src/views/home/index.vue src/views/home/components/institution-home.vue src/views/home/components/activation-trend-chart.vue src/service/api/bms.ts && pnpm typecheck`
  - 结果：通过
- [x] 管理员角色预览接口能力校验通过
  - 命令：`cd backend && go test ./internal/service -run TestBuildLatestDeviceAlarmsBase -count=1 && go test ./internal/api ./router/apps -count=1`
  - 结果：通过（存在 macOS `IOMasterPort` 废弃告警，不影响结果）
- [ ] SQL 补丁执行校验
  - 脚本：`backend/sql/39.sql`
  - 待验证：执行后 `sys_ui_elements` 中 `org-management-main/org-pack-factory/org-dealer/org-store` 的 `param1/route_path/multilingual` 已更新
- [ ] 手工联调验收
  - 待验证：仅分配 `bms_store` / `bms_dealer` / `bms_pack_factory`（不分配 `bms_org_management`）时，菜单点击可直接进入独立页面且不提示 404

## 3. 风险
- 线上历史脏数据（`ui_codes` 包含已删除菜单编码）会被自动忽略，建议运维抽样核对重点租户菜单配置。
