# FEAT-0010 机构菜单权限生效与首页分层改造 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-03-08
- related_feature: FEAT-0010
- version: v0.1.0

## 日志
1. 新建 FEAT-0010 文档集并登记看板。
2. 后端菜单权限链路修复：
   - `backend/internal/service/org_type_permissions.go`
     - 保存菜单权限时补齐祖先菜单编码，避免仅勾选子菜单导致根菜单缺失。
     - `APP_USER` 配置下发时，角色自动同步到 `END_USER` 账号。
   - `backend/internal/dal/ui_elements.go`
     - 新增按 `ui_codes` 构建菜单树能力（自动补齐祖先节点）。
   - `backend/internal/service/sys_ui_elements.go`
     - 非管理员账号登录时，若命中机构类型菜单配置，优先按配置树返回菜单（修复“仅首页”问题）。
3. 后端首页分层接口实现：
   - `backend/internal/model/bms_dashboard.http.go`：新增首页汇总响应结构（机构/终端用户）。
   - `backend/internal/service/bms_dashboard.go`：新增首页汇总服务，输出机构状态统计、7/30天激活趋势、终端用户电池总数。
   - `backend/internal/api/bms_dashboard.go`、`backend/router/apps/bms_dashboard.go`：新增 `GET /api/v1/dashboard/home/summary`。
4. 前端首页分层改造：
   - `frontend/src/service/api/bms.ts`：新增首页汇总接口定义。
   - `frontend/src/views/home/index.vue`：管理员沿用原租户首页；普通用户按 `user_kind` 切换机构/终端首页。
   - 新增组件：
     - `frontend/src/views/home/components/institution-home.vue`
     - `frontend/src/views/home/components/end-user-home.vue`
     - `frontend/src/views/home/components/activation-trend-chart.vue`
5. 权限配置页回显修复（测试反馈）：
   - `frontend/src/views/management/permission/index.vue`
     - 回显时过滤后端自动补齐的父菜单编码，仅回显可选子菜单编码，修复“父菜单下子项全部被勾选”的视觉误导。
     - 菜单树增加 `check-strategy=\"child\"`，勾选与保存统一按子节点口径处理。
6. 动态路由适配修复（仅分配快捷菜单时可进入页面）：
   - `frontend/src/service/api/management.adapter.ts`
     - 增加 legacy 菜单路由解析器：将 `/bms/org/management?org_type=...` 规范化映射到真实可用路由（`/bms/org/dealer`、`/bms/org/store`、`/bms/org/pack-factory`）。
     - 动态路由 `name` 与页面组件 key 统一使用规范化后的 canonical route key，避免 `element_code` 与真实路由 key 不一致导致“菜单可见但点击路由不存在”。
7. 动态路由兼容增强（测试反馈二次修复）：
   - `frontend/src/service/api/management.adapter.ts`
     - 补充兼容 `/bms/org?ORG_TYPE=...`（含大写 query key `ORG_TYPE`）的快捷菜单路由映射。
     - 对 `bms_store` / `bms_pack_factory` / `bms_org_management` 增加按 `element_code` 的兜底 canonical 映射，避免脏数据或大小写差异导致 404。
8. 组织快捷菜单页面重构（按确认方案 A 落地）：
   - 共享组件抽离：`frontend/src/views/bms/org/components/org-management-page.vue`
     - 抽离机构管理通用页面逻辑（列表、新增编辑、重置密码、Tab）为可复用组件。
   - 页面改造：
     - `frontend/src/views/bms/org/index.vue` 使用共享组件的“全量 Tab”模式。
     - `frontend/src/views/bms/org/pack-factory/index.vue` 使用共享组件固定 `PACK_FACTORY`。
     - `frontend/src/views/bms/org/dealer/index.vue` 使用共享组件固定 `DEALER`。
     - `frontend/src/views/bms/org/store/index.vue` 使用共享组件固定 `STORE`。
     - 移除原“进入后再 `router.replace('/bms/org?org_type=...')`”跳转逻辑，避免未分配父菜单时 404。
9. 菜单配置 SQL 补丁：
   - 新增 `backend/sql/39.sql`
     - 将组织快捷菜单配置改为独立路由（`/bms/org/pack-factory`、`/bms/org/dealer`、`/bms/org/store`）。
     - 修正组织管理主菜单为 `/bms/org`，并同步 `route_path/multilingual` 到真实路由键。
10. 机构首页激活曲线修复与交互优化：
   - `frontend/src/views/home/components/activation-trend-chart.vue`
     - 修复图表初始数据已存在时仍停留 Loading 的问题：图表渲染/更新阶段统一 `hideLoading`，并在初始化时直接注入 props 数据。
   - `frontend/src/views/home/components/institution-home.vue`
     - 将“最近一周激活曲线 + 最近一月激活曲线”合并为一个“最近激活”区块，使用 Tab（近一周/近一月）切换，默认近一周。
11. BMS 看板告警概览接口 SQL 修复：
   - `backend/internal/service/bms_dashboard.go`
     - `GetAlarmOverview` 改为每个统计查询使用独立 base query 实例，避免复用同一 `*gorm.DB` 链路导致 join 别名 `org_dev` 重复拼接（`SQLSTATE 42712`）。
12. 首页身份信息展示与管理员视角切换优化：
   - `frontend/src/views/home/index.vue`
     - 首页顶部新增“当前账号身份信息”区域：展示账号名称、账号权限；普通账号额外展示机构用户/终端用户标识及类型/机构名称。
     - 平台管理员/租户管理员新增身份切换 Tab：`租户管理员 / PACK 厂家 / 经销商 / 门店 / 终端用户`，可切换预览不同角色首页。
   - `backend/internal/api/bms_dashboard.go`、`backend/internal/service/bms_dashboard.go`
     - `GET /api/v1/dashboard/home/summary` 支持 `view_as` 查询参数（管理员预览角色首页）。
     - 新增按 `org_type` 统计机构首页指标与激活趋势、按租户统计终端用户电池数能力。
13. 机构首页交互微调：
   - `frontend/src/views/home/components/institution-home.vue`
     - 移除提示文案“当前首页为 ... 机构视图，数据范围...自动隔离”。
     - 刷新按钮移动至右上角并改为图标按钮（无文案）。
