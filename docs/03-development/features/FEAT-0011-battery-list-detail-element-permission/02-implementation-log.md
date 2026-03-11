# FEAT-0011 电池列表详情路由与元素权限补齐 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-03-10
- related_feature: FEAT-0011
- version: v0.1.1

## 日志
1. 完成 FEAT-0011 文档建档（规格/设计/实施/测试/发布）。
2. 后端新增当前用户 UI 权限接口：
   - `backend/internal/service/org_type_permissions.go`
   - `backend/internal/api/org_type_permissions.go`
   - `backend/router/apps/org_type_permissions.go`
3. 后端菜单权限配置树支持按钮节点：
   - `backend/internal/dal/ui_elements.go`（`element_type` 纳入 4）
   - `backend/internal/service/org_type_permissions.go`（保存权限时支持按钮编码）
4. 新增 SQL 补丁：
   - `backend/sql/40.sql`
   - 新增电池列表详情路由权限项与页面元素权限项；
   - 对已配置 `bms_battery_list` 的 PACK/经销商/门店权限自动补齐新增编码。
5. 同步基础初始化脚本：
   - `backend/sql/1.sql` 增补 FEAT-0011 新增的路由/按钮权限项。
6. 前端新增权限指令与能力：
   - `frontend/src/utils/common/ui-permission.ts`
   - `frontend/src/directives/ui-permission.ts`
   - `frontend/src/directives/index.ts`
   - `frontend/src/main.ts`（全局注册）
7. 电池列表页面接入权限控制：
   - `frontend/src/views/bms/battery/list/index.vue`
   - 顶部按钮按权限显隐，操作菜单按权限过滤，页面根节点增加页面权限指令。
8. 鉴权状态联动：
   - `frontend/src/store/modules/auth/index.ts` 登录/登出重置 UI 权限缓存。
9. API 封装补充：
   - `frontend/src/service/api/org-type-permissions.ts` 新增 `fetchCurrentUiPermissions`。
10. 菜单管理显示优化（测试反馈修复）：
   - `frontend/src/views/management/auth/index.vue`：当 `multilingual` 未命中翻译词条时回退显示 `description`，避免显示 i18n key。
   - `frontend/src/locales/langs/zh-cn/route.json`、`frontend/src/locales/langs/en-us/route.json`：补齐 `perm.*` 翻译词条。
   - `backend/sql/40.sql`、`backend/sql/1.sql`：FEAT-0011 新增按钮权限项统一使用 `perm.*` 的 `multilingual`，并修正 `description` 为可读名称（导出/添加电池/导入/参数/离线指令/生命周期-出厂/激活/调拨）。
11. 修复“电池列表点击后跳转到详情页/空白页”的根因：
   - `backend/internal/dal/ui_elements.go`：运行时菜单树查询仅返回 `element_type in (1,2,3)`，剔除按钮节点（`element_type=4`），避免页面路由被按钮子节点污染。
   - `backend/sql/40.sql`：将 `bms_battery_list_detail` 修正为 `bms` 根节点下路由，并保持隐藏菜单属性（`param3='1'`）。
12. 增加前端兜底防护，避免隐藏子路由触发父路由自动重定向：
   - `frontend/src/router/elegant/transform.ts`：父路由自动 `redirect` 优先指向“首个可见子路由”；若全部为隐藏子路由，则不强制跳转隐藏路由。
13. 同步初始化脚本幂等修复：
   - `backend/sql/1.sql`：补充对 `bms_battery_list_detail` 及 FEAT-0011 按钮项的 `UPDATE`，确保已存在数据也会被修正到最新结构。
14. 权限管理交互优化（测试反馈修复）：
   - `frontend/src/views/management/permission/index.vue`：菜单权限树取消父子级联，支持父节点与子节点独立勾选，满足“仅页面路由权限、不含页面内按钮权限”的配置场景。
   - `frontend/src/views/management/permission/index.vue`：菜单权限回显保留原始 `ui_codes`，不再过滤父节点，避免保存后父节点勾选状态丢失。
   - `frontend/src/views/management/permission/index.vue`：顶部“刷新 / 保存”按钮补充图标，提升操作识别效率。
15. 电池列表页面布局与滚动优化（测试反馈修复）：
   - `frontend/src/views/bms/battery/list/index.vue`
   - 搜索区改为“基础条件 + 高级筛选折叠”结构，默认仅展示序列号/型号；
   - 表格区改为独立滚动容器，分页条固定在卡片底部，避免列表记录增多后页面无法滚动访问顶部数据。
