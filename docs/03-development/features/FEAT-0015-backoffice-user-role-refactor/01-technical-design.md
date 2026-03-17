# FEAT-0015 后台用户体系与角色权限重构 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-03-13
- related_feature: FEAT-0015
- version: v0.1.0

## 1. 方案概览
- 在 `users` 表新增 `is_main` 字段，补齐“主账号/子账号”维度。
- 用组合条件统一业务概念：
  - 租户：`TENANT_ADMIN + ORG_USER + is_main=1`
  - 租户后台管理员：`TENANT_ADMIN + ORG_USER + is_main=0`
  - 机构主账号：`TENANT_USER + ORG_USER + is_main=1`
  - 机构员工账号：`TENANT_USER + ORG_USER + is_main=0`
  - 终端用户：`TENANT_USER + END_USER + is_main=0`
- 新增 `user_roles`、`role_permissions` 业务表，以业务表为权限事实来源；Casbin 保持运行时授权和接口鉴权适配。
- 登录菜单/权限获取改为“基础权限范围 + 角色权限叠加”模式：
  - 主账号：直接使用基础权限全集。
  - 子账号：在基础权限范围内，取角色权限并集。
- 菜单定义与前端路由同步迁移到 `系统管理 > 后台账号管理/后台角色管理`。

## 2. 接口与数据结构
### 2.1 数据库结构
- `users`
  - 新增：`is_main smallint not null default 0`
  - 约束建议：
    - 租户主账号唯一索引：`tenant_id + authority + user_kind + is_main` 的条件唯一
    - 机构主账号唯一索引：`tenant_id + org_id + authority + user_kind + is_main` 的条件唯一
  - 数据约束：
    - `user_kind = END_USER` 时 `is_main` 只能为 `0`

- `roles`
  - 保留现有主表，补充作用域字段：
    - `authority varchar(50)`：角色适用账号权限类型
    - `user_kind varchar(50)`：角色适用用户类型
    - `org_type varchar(50)`：可空，组织类型范围

- `user_roles`
  - `id varchar(36)`
  - `tenant_id varchar(36)`
  - `user_id varchar(36)`
  - `role_id varchar(36)`
  - `created_at timestamptz`
  - `updated_at timestamptz`
  - 唯一索引：`user_id + role_id`

- `role_permissions`
  - `id varchar(36)`
  - `tenant_id varchar(36)`
  - `role_id varchar(36)`
  - `permission_key varchar(128)`：建议保存 `sys_ui_elements.id`
  - `created_at timestamptz`
  - `updated_at timestamptz`
  - 唯一索引：`role_id + permission_key`

### 2.2 历史数据回填
- 租户主账号回填：
  - 每个 `tenant_id` 下，选取最早创建的 `TENANT_ADMIN + ORG_USER` 账号作为 `is_main=1`
  - 其余 `TENANT_ADMIN + ORG_USER` 账号回填 `is_main=0`
- 机构主账号回填：
  - 每个 `tenant_id + org_id` 下，选取最早创建的 `TENANT_USER + ORG_USER` 账号作为 `is_main=1`
  - 其余同组账号回填 `is_main=0`
- 终端用户：
  - `TENANT_USER + END_USER` 全量回填 `is_main=0`

### 2.3 后端接口改造
- 用户接口扩展：
  - `POST /api/v1/user`
  - `PUT /api/v1/user`
  - `GET /api/v1/user`
  - `GET /api/v1/user/{id}`
  - `DELETE /api/v1/user/{id}`
- 新增/补强请求字段：
  - `user_kind`
  - `is_main`
  - `org_id`
  - `role_ids`
- 新增操作语义：
  - 重置密码：可复用 `PUT /api/v1/user`
  - 禁用/解禁：可复用 `status=F/N`
  - 角色分配：建议直接整合到用户编辑，也可新增独立接口

- 角色接口扩展：
  - `POST /api/v1/role`
  - `PUT /api/v1/role`
  - `GET /api/v1/role`
  - `DELETE /api/v1/role/{id}`
  - 新增：
    - `GET /api/v1/role/{id}/permissions`
    - `PUT /api/v1/role/{id}/permissions`

### 2.4 权限树来源
- `TENANT_ADMIN`
  - 基础权限树来源于现有后台菜单定义 `sys_ui_elements`
- `TENANT_USER + ORG_USER`
  - 基础权限树来源于 `org_type_permissions`
- 角色权限树必须是基础权限树的子集
- `role_permissions.permission_key` 直接保存 `sys_ui_elements.id`
  - 优点：兼容当前前端权限树组件直接使用节点 ID 勾选
  - 机构类型基础权限仍通过 `org_type_permissions.ui_codes` 维护，登录时转换为 `sys_ui_elements.id` 后再与角色权限求交集

## 3. 关键流程
### 3.1 创建租户主账号
1. `SYS_ADMIN` 创建租户。
2. 服务层生成唯一 `tenant_id`。
3. 新用户写入：
   - `authority = TENANT_ADMIN`
   - `user_kind = ORG_USER`
   - `is_main = 1`
4. 初始化默认看板、默认 OpenAPI Key、默认后台角色基础数据。

### 3.2 创建租户后台管理员
1. 当前租户主账号或具备账号管理权限的后台管理员发起创建。
2. 服务层校验目标账号属于当前租户。
3. 新用户写入：
   - `authority = TENANT_ADMIN`
   - `user_kind = ORG_USER`
   - `is_main = 0`
4. 根据提交内容写入 `user_roles`。

### 3.3 创建机构主账号/员工账号
1. 当前租户后台账号选择目标机构。
2. 服务层校验机构属于当前租户。
3. 主账号写入：
   - `authority = TENANT_USER`
   - `user_kind = ORG_USER`
   - `is_main = 1`
   - `org_id = 指定机构`
4. 员工账号写入：
   - `authority = TENANT_USER`
   - `user_kind = ORG_USER`
   - `is_main = 0`
   - `org_id = 指定机构`

### 3.4 登录后权限计算
1. 用户登录成功后读取 `authority/user_kind/is_main/org_id/tenant_id`。
2. 解析基础权限范围：
   - `TENANT_ADMIN` 取租户后台菜单全集。
   - `TENANT_USER + ORG_USER` 取 `org_type_permissions` 对应 `ui_codes`。
3. 若 `is_main=1`，则返回基础权限全集。
4. 若 `is_main=0`，读取 `user_roles -> role_permissions`，取权限并集。
5. 最终菜单/按钮权限 = `基础权限范围 ∩ 角色权限并集`。
6. 为兼容接口鉴权，将最终权限同步到 Casbin，或在鉴权阶段追加业务表校验。

## 4. 安全与权限
- 租户隔离：
  - `TENANT_ADMIN` / `TENANT_USER` 仅可操作本租户数据
- 主账号约束：
  - 不允许删除唯一租户主账号
  - 不允许删除唯一机构主账号，除非先完成主账号迁移
- 角色作用域约束：
  - 角色仅允许分配给同租户且账号类型匹配的用户
  - 机构账号角色权限不得超出所属 `org_type_permissions`
- 删除角色前必须校验 `user_roles` 中无引用

## 5. 测试策略
- SQL 验证：
  - 执行增量脚本后，检查字段、索引、回填结果、菜单迁移结果
- 后端：
  - `cd backend && go test ./...`
  - 重点验证账号新增/编辑/删除、角色分配、权限树回显、登录权限叠加
- 前端：
  - `cd frontend && pnpm lint`
  - `cd frontend && pnpm build`
- 手工联调：
  - 新建租户主账号
  - 新建租户后台管理员并分配角色
  - 新建机构主账号/员工账号并分配角色
  - 登录后菜单显隐与按钮权限校验
  - 菜单迁移后的路由访问和权限回显

## 6. 兼容性与迁移
- `users` 新字段采用默认值与回填脚本，兼容历史数据。
- 角色业务表引入后，保留 Casbin 运行时规则同步，避免一次性推翻现有中间件。
- 前端旧路由建议保留一版重定向到新路由，降低菜单迁移带来的入口失效风险。
- 所有新增 SQL 需同步更新 `backend/sql/1.sql` 默认定义。
