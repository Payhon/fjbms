# FEAT-0055 PACK 厂微信小程序配置接入 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-08-15
- related_feature: FEAT-0055
- version: v0.1.0

## 1. 测试范围
- PACK 厂小程序配置接口。
- APP 用户管理来源筛选和增强列表接口。
- 微信小程序登录配置选择与身份隔离。
- WEB PACK 厂配置弹窗。
- UniApp 微信小程序登录、Banner、内容页展示。

## 2. 测试环境
- 本地开发环境。
- 测试环境：`https://fjbms.yz6688.cn`。

## 3. 用例结果
- [x] 后端定向测试：`cd backend && go test ./internal/service ./internal/api ./router/apps`，通过。
- [x] 测试环境回归：`GET https://fjbms.yz6688.cn/api/v1/org/895a3430-0143-8ecd-f9e3-89d9079350a0/wxmp-config`，通过；未配置小程序时返回 `code=200` 和空配置默认值，不再返回 `100404`。
- [x] 前端定向类型检查：`cd frontend && pnpm exec vue-tsc --noEmit --skipLibCheck --pretty false 2>&1 | rg "app_manage/users|org-management-page|app-manage.ts|bms.ts|FilePicker|MarkdownEditor" || true`，当前用户管理、小程序配置弹框、文件选择组件和 Markdown 编辑器无新增类型错误输出。
- [x] 图片回显体验定向检查：`cd frontend && pnpm exec vue-tsc --noEmit --skipLibCheck --pretty false 2>&1 | rg "file-picker|org-management-page|FilePicker" || true`，共享文件选择组件与 PACK 小程序配置弹框无新增类型错误输出。
- [x] UniApp 定向类型检查：`cd fjbms-uniapp && pnpm exec tsc --noEmit --skipLibCheck --pretty false 2>&1 | rg "pages/login/login|service/app-auth|common/public-content|pages/home/home" || true`，登录 Logo 相关路径无新增类型错误输出。
- [x] 小程序登录方式定向检查：`cd fjbms-uniapp && pnpm exec tsc --noEmit --skipLibCheck --pretty false 2>&1 | rg "pages/login/login|pages/login/register|pages/login/forgot|wxmp-runtime|service/app-auth|common/public-content" || true`，PACK/租户级小程序登录分流相关路径无新增类型错误输出。
- [x] 小程序设置页定向检查：`cd fjbms-uniapp && pnpm exec tsc --noEmit --skipLibCheck --pretty false 2>&1 | rg "pages/my/setting|pages/my/my|wxmp-runtime" || true`，PACK 小程序设置页隐藏项和我的页头像样式相关路径无新增类型错误输出。
- [x] 小程序内容配置定向检查：`cd backend && go test ./internal/service ./internal/api ./router/apps`，通过；runtime `org_name` 与内容接口相关后端路径编译通过。
- [x] PACK 小程序内容前端定向检查：`cd frontend && pnpm exec vue-tsc --noEmit --skipLibCheck --pretty false 2>&1 | rg "src/views/bms/org/components/org-management-page|src/service/api/(app-manage|bms)" || true`，本次 PACK 配置弹框和内容 API 路径无新增类型错误输出。
- [x] UniApp 关于我们/联系客服定向检查：`cd fjbms-uniapp && pnpm exec tsc --noEmit --skipLibCheck --pretty false 2>&1 | rg "pages/my/about|pages/my/contact|pages/content/page|wxmp-runtime" || true`，关于我们厂商名、协议内容和联系客服相关路径无新增类型错误输出。
- [x] 测试环境前端更新：`make update-frontend-test`，通过；构建和静态资源更新完成。
- [~] 前端 typecheck：`cd frontend && pnpm typecheck` 在当前 macOS 下因脚本使用 Windows 风格 `set NODE_OPTIONS=...` 返回 0；额外执行 `pnpm exec vue-tsc --noEmit --skipLibCheck`，仓库存在大量既有类型错误；按本次新增/修改文件路径过滤后未输出匹配错误。
- [x] UniApp TypeScript 校验：`cd fjbms-uniapp && pnpm exec tsc --noEmit --skipLibCheck --pretty false`，通过。
- [ ] 微信开发者工具/真机小程序回归。
- [x] 默认小程序运行时 AppID 解析定向测试：`cd backend && go test ./internal/service -run 'TestResolveRuntimeApp|TestGetPackWxMpConfigMissingReturnsEmptyConfig|TestPackFactoryUserCanOnlyManageOwnWxMpConfig' -count=1`，通过。
- [x] 后端相关包回归：`cd backend && go test ./internal/service ./internal/api ./router/apps -count=1`，通过。
- [~] 后端全量测试：`cd backend && go test ./... -count=1`；本次涉及的 `internal/service`、`internal/api`、`router/apps` 均通过，全量仍受既有环境测试阻塞：`initialize/test.TestSetDevice` 未初始化依赖导致空指针，`test.TestDatebase` 缺少 `run_env`/本地数据库配置后空指针。
- [x] 生产接口回归：2026-08-15 发布后，`fjbms-backend` 为 `active (running)`，服务本机 `GET http://127.0.0.1:9999/health` 返回 `code=200`；默认租户微信 AppID `wxea563e4e504e24c7`、UniApp 主应用 ID `__UNI__40EADE1` 和缺省 AppID 的隐私政策/用户协议均返回 `code=200`，未知 AppID 保持返回 `100404`。
- [x] 生产 PACK 路径回归：从生产库选取 2 条 `OPEN` 且已发布隐私政策的 PACK AppID，请求隐私政策均返回 `code=200`、完整内容长度一致，确认 PACK 独立应用直接解析路径未受影响。

## 4. 缺陷与风险
- 已修复：测试环境 PACK 厂“小程序配置”弹窗首次打开时，因后端将“未配置”当作资源不存在返回 `100404`，导致前端展示“未知错误”。
- 需要在微信开发者工具/体验版验证 `uni.getAccountInfoSync().miniProgram.appId` 能正确命中 PACK 厂配置。
- 需要分别用租户级 FJIABMS 小程序 AppID 和 PACK 厂小程序 AppID 验证登录页分流：租户级显示账号密码登录，PACK 厂仅显示微信登录。
- 需要在 PACK 厂小程序设置页验证账号、修改密码、手机号绑定和 Email 绑定入口已隐藏；租户级小程序仍显示这些入口。
- 需要在 PACK 厂小程序中验证“联系客服”显示该小程序独立 `contact_service` 内容，“关于我们”厂商信息显示关联 PACK 厂机构名称，用户协议和隐私政策跳转后显示该小程序独立内容。
- 需要配置真实 AppSecret 后验证微信 code2session、登录注册自动创建用户、绑定手机号流程。
- 前端全量 `vue-tsc` 当前仍受仓库既有类型问题阻塞，非本功能新增阻塞项。
- 默认租户微信 AppID 的内容读取修复无需重新发布小程序；仍需在现有小程序版本中点击隐私政策/用户协议做最终页面验收。

## 5. 结论
- 后端兼容解析、相关包测试和生产接口回归均已通过；无需重新发布移动端微信小程序。现有微信小程序页面点击仍作为最终真机/UI 验收边界。
