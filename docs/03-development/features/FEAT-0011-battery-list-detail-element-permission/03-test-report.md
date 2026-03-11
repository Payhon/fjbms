# FEAT-0011 电池列表详情路由与元素权限补齐 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-03-10
- related_feature: FEAT-0011
- version: v0.1.1

## 1. 测试范围
- 后端：当前用户 UI 权限接口与权限树按钮节点支持。
- 前端：权限指令行为、电池列表按钮与操作菜单权限控制。
- SQL：新增路由/按钮权限项及机构类型权限补齐逻辑。

## 2. 结果
- [x] 后端测试
  - 命令：`cd backend && go test ./internal/service ./internal/api ./internal/dal ./router/apps`
  - 结果：通过（存在 macOS `IOMasterPort` 废弃告警，不影响结果）
- [x] 前端 ESLint
  - 命令：`cd frontend && pnpm exec eslint --no-warn-ignored src/directives/index.ts src/directives/ui-permission.ts src/utils/common/ui-permission.ts src/service/api/org-type-permissions.ts src/views/bms/battery/list/index.vue src/views/management/auth/index.vue`
  - 结果：通过
- [x] 前端类型检查
  - 命令：`cd frontend && pnpm typecheck`
  - 结果：通过
- [x] 电池列表布局回归（代码级）
  - 位置：`frontend/src/views/bms/battery/list/index.vue`
  - 结果：搜索区支持基础/高级折叠；表格使用独立滚动区；分页条从表格内部拆出并固定在底部。
- [x] 路由重定向兜底校验（代码级）
  - 位置：`frontend/src/router/elegant/transform.ts`
  - 结果：父路由仅在存在“可见子路由”时自动重定向，隐藏子路由不会再成为默认跳转目标。
- [x] 运行时菜单树过滤校验（代码级）
  - 位置：`backend/internal/dal/ui_elements.go`
  - 结果：运行时菜单树仅包含 `element_type in (1,2,3)`，按钮节点（4）不再参与动态路由构建。
- [x] 多语言键补齐校验
  - 命令：`node -e "JSON.parse(require('fs').readFileSync('frontend/src/locales/langs/zh-cn/route.json','utf8')); JSON.parse(require('fs').readFileSync('frontend/src/locales/langs/en-us/route.json','utf8'))"`
  - 结果：通过
- [ ] SQL 补丁验证
  - 脚本：`backend/sql/40.sql`
  - 待验证：`sys_ui_elements` 新增 9 个 `element_code`，`org_type_permissions.ui_codes` 自动补齐新增编码。
- [ ] 手工验收
  - 待验证：PACK/经销商/门店账号点击“操作->查看详情”可进入详情页，按钮/操作按权限显示。

## 3. 风险
- 若租户未执行 `40.sql`，页面元素权限会因缺少新编码默认被隐藏或误放行（取决于租户是否命中 `allow_all`）。
