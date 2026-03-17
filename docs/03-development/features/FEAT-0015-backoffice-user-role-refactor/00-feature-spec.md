# FEAT-0015 后台用户体系与角色权限重构 - 功能规格

- status: in_progress
- owner: payhon
- last_updated: 2026-03-13
- related_feature: FEAT-0015
- version: v0.1.0

## 1. 背景与目标
- 背景：
  - 现有系统已支持多租户、多用户类型，但 `users` 表当前仅能依赖 `authority` 和 `user_kind` 做粗粒度区分，无法稳定表达“租户主账号/租户后台管理员/机构主账号/机构员工账号”的主从关系。
  - 现有后台账号管理和角色管理主要基于 `authority + dealer_id + casbin` 的简化模型，无法满足同租户多个后台管理员、同机构多个员工账号的细粒度权限分配。
  - 系统中多处“租户”识别逻辑直接以 `TENANT_ADMIN` 代指，引入多个租户管理员后会导致租户列表、默认租户选择、租户信息查询等逻辑失真。
- 目标：
  1. 在 `users` 表引入 `is_main`，完善后台用户体系定义。
  2. 统一租户、租户管理员、机构主账号、机构辅账号的判定口径。
  3. 建立 `roles + user_roles + role_permissions` 业务权限模型，并与现有登录权限获取逻辑叠加。
  4. 改造后台账号管理、后台角色管理、菜单定义和相关文档，使之支撑租户管理员和机构账号两类后台账号。

## 2. 范围
### In Scope
- 数据库新增 `users.is_main` 字段及必要唯一约束。
- 新增 `user_roles`、`role_permissions` 表，并补充角色作用域字段。
- 统一所有“租户识别”口径为：`authority=TENANT_ADMIN AND user_kind=ORG_USER AND is_main=1`。
- 改造后台账号管理的新增、编辑、重置密码、禁用、解禁、删除、角色分配。
- 改造后台角色管理的角色创建、删除校验、权限分配、权限树回显。
- 调整登录后的菜单/权限获取逻辑，叠加后台角色权限。
- 菜单从 `BMS 管理 > 系统管理 > 账号管理/角色管理` 迁移到 `系统管理 > 后台账号管理/后台角色管理`。
- 更新 [backend/docs/README-DEV.md](/Users/payhon/work2025/project/fjbms/backend/docs/README-DEV.md) 相关章节。

### Out of Scope
- 不重构 APP/UniApp 终端用户注册与登录主链路。
- 不替换 Casbin 为全新权限引擎；本次以业务表为准、Casbin 为运行时授权适配层。
- 不新增独立“终端用户后台子账号”模型，`END_USER` 保持无主从定义。

## 3. 用户价值
- 平台可稳定识别每个租户唯一主账号，避免租户概念和管理员账号概念混淆。
- 租户下可新增多个后台管理员，并对菜单/功能权限做差异化授权。
- 机构下可新增主账号和员工账号，并在机构权限范围内进行角色化授权。
- 后台权限来源更加可审计、可维护，避免角色配置仅存在于 Casbin 规则中而缺乏业务表支撑。

## 4. 验收标准
1. `users` 表新增 `is_main` 字段，默认值为 `0`，并完成历史数据回填。
2. 以下用户判定口径可在数据库和接口层稳定成立：
   - `TENANT_ADMIN + ORG_USER + is_main=1`：租户主账号/租户概念载体
   - `TENANT_ADMIN + ORG_USER + is_main=0`：租户后台管理员
   - `TENANT_USER + ORG_USER + is_main=1`：机构主账号
   - `TENANT_USER + ORG_USER + is_main=0`：机构员工账号
   - `TENANT_USER + END_USER`：终端用户
3. 同一 `tenant_id` 仅允许存在一个租户主账号；同一 `tenant_id + org_id` 仅允许存在一个机构主账号。
4. 后台账号管理支持新增、编辑、重置密码、禁用、解禁、删除、角色分配，且创建记录时符合新的用户口径定义。
5. 后台角色管理支持创建角色、分配权限、查看权限树、删除前校验角色下无分配用户。
6. 登录后获取的后台权限遵循“基础权限范围 ∩ 角色权限并集”的规则：
   - 主账号默认拥有本层级基础权限全集。
   - 子账号需通过角色获得可用后台权限。
7. 菜单位置调整完成，并提供增量 SQL 补丁及 `1.sql` 默认定义更新。
8. [backend/docs/README-DEV.md](/Users/payhon/work2025/project/fjbms/backend/docs/README-DEV.md) 已补充新的后台用户体系定义与开发约束。

## 5. 风险与约束
- 历史数据中已有多个 `TENANT_ADMIN` / `TENANT_USER` 账号，需设计稳妥的 `is_main` 回填规则，避免误判主账号。
- 当前系统很多逻辑直接将 `TENANT_ADMIN` 视为租户，若改造不彻底会出现租户列表重复、默认租户错误、权限口径不一致等问题。
- 现有 Casbin 规则已在线上使用，角色业务表引入后需保证迁移阶段接口与旧规则兼容。
- 菜单迁移涉及前端路由、后端菜单 SQL、权限树来源和角色权限回显，需要统一编码与路径映射。

## 6. 回滚方案
- 回滚前端新的后台账号管理/后台角色管理页面入口与角色授权交互。
- 回滚后端 `is_main` 口径、角色业务表读写逻辑和登录权限叠加逻辑。
- 回滚 SQL 补丁涉及：
  - 新增字段 `users.is_main`
  - 新增表 `user_roles`、`role_permissions`
  - 菜单迁移数据
- 若回滚数据库结构，需先导出 `users.is_main`、`user_roles`、`role_permissions` 及新菜单数据，再执行结构回退。
