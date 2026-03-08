# FEAT-0010 机构菜单权限生效与首页分层改造 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-03-07
- related_feature: FEAT-0010
- version: v0.1.0

## 1. 方案概览
- 菜单权限：
  - 修复 `org_type_permissions` 下发时的角色绑定覆盖范围（包含 APP_USER/END_USER）。
  - 菜单返回接口优先按机构类型配置 `ui_codes` 生成菜单树，避免仅依赖历史 Casbin 根节点导致“仅首页”问题。
  - 保存菜单配置时补齐父级菜单，保证树结构可达。
- 首页分层：
  - 新增 Dashboard 首页汇总接口（机构/终端用户）。
  - 前端 `home` 页面根据 `user_kind` 渲染机构首页组件或终端用户首页组件。

## 2. 后端改造点
1. `org_type_permissions.Upsert`
   - `ui_codes` 规范化并补齐祖先节点。
   - APP_USER 场景同步给 `END_USER` 账号补齐角色分组策略。
2. `ui_elements/menu`
   - 非管理员用户根据用户类型解析目标 org_type（ORG_USER=PACK/DEALER/STORE，END_USER=APP_USER）。
   - 若存在 org_type 菜单配置，则按配置直接构建菜单树返回。
3. Dashboard 新增接口
   - 机构：电池总数、状态统计、7/30 天激活趋势。
   - 终端用户：用户拥有电池总数。

## 3. 前端改造点
- `views/home/index.vue`：保留管理员原逻辑；普通用户改为分层首页容器。
- 新增两个子组件：
  - `InstitutionHome`: 指标卡 + 状态统计 + 双曲线图。
  - `EndUserHome`: 电池总数 + 欢迎信息。
- `service/api/bms.ts` 增加首页汇总接口封装。

## 4. 测试策略
- 后端：`go test ./...`（或按仓库既有规则排除本地依赖测试）。
- 前端：`pnpm typecheck` + 变更文件定向 lint。
- 手工：4 类账号菜单权限验证 + 两类首页展示验证。
