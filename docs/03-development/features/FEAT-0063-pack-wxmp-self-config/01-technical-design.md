# FEAT-0063 PACK 厂小程序配置自助入口 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-07-01
- related_feature: FEAT-0063
- version: v0.1.0

## 1. 方案概览
- 后端继续复用 `GET/PUT /api/v1/org/{id}/wxmp-config`，不新增业务接口。
- SQL 新增 `bms_pack_wxmp_config` 菜单并调整 PACK_FACTORY 类型权限。
- Web 将原 PACK 厂家管理弹窗中的配置表单抽为共享组件，管理员弹窗和 PACK 自助页面共同使用。
- 新页面从登录态读取当前用户 `org_id` 和 `org_type`，仅 PACK_FACTORY 且有机构归属时展示表单。

## 2. 权限与菜单
- 新菜单 code：`bms_pack_wxmp_config`
- 路径：`/bms/pack-wxmp-config`
- 组件：`view.bms_pack_wxmp_config`
- 标题：`小程序配置`
- 挂载位置：BMS 根菜单下。
- SQL `backend/sql/61.sql`：
  - 幂等插入或更新 `sys_ui_elements`。
  - 所有租户 `PACK_FACTORY` 类型权限新增 `bms_pack_wxmp_config`。
  - 所有租户 `PACK_FACTORY` 类型权限移除 `bms_pack_factory`。

## 3. 后端规则
- `ensurePackWxMpConfigAccess` 继续作为最终访问控制：
  - PACK_FACTORY 业务账号只能访问自己的 `claims.OrgID`。
  - 租户/系统管理员可访问当前租户下 PACK 机构配置。
- 后端接口不信任前端传入的机构 ID；跨机构读写由服务端拒绝。

## 4. Web 结构
- 新增共享组件：
  - `frontend/src/views/bms/_shared/components/pack-wxmp-config-panel.vue`
  - 输入：`orgId`
  - 输出：`saved`
  - 能力：基础配置、图片选择、质保卡片开关、备注、内容配置、发布。
- 改造旧入口：
  - `frontend/src/views/bms/org/components/org-management-page.vue`
  - 原弹窗改为挂载共享组件。
- 新增自助页面：
  - `frontend/src/views/bms/pack-wxmp-config/index.vue`
  - 非 PACK_FACTORY 显示无权限提示。
  - PACK_FACTORY 缺少 `org_id` 显示无机构归属提示。
  - 正常账号直接展示配置表单，不需要先打开弹窗。

## 5. 国际化与路由
- 路由 name：`bms_pack_wxmp_config`
- i18n key：`route.bms_pack_wxmp_config`
- Web BMS 词包新增：
  - `packWxmpSelfConfig.title`
  - `packWxmpSelfConfig.packOnly`
  - `packWxmpSelfConfig.missingOrg`

## 6. 测试策略
- 后端增加 PACK_FACTORY 自身配置访问测试，覆盖可读写自己机构、不能读写其他 PACK 机构。
- SQL 只读校验菜单存在、PACK_FACTORY 权限包含新 code 且不包含旧 `bms_pack_factory`。
- Web 执行受影响文件 ESLint 和显式类型检查过滤。
- 运行态使用 PACK_FACTORY 账号确认菜单可见性、保存配置和 FEAT-0062 质保卡片开关回显。
