# FEAT-0009 管理端登录验证码与二维码配置展示 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-03-07
- related_feature: FEAT-0009
- version: v0.1.0

## 1. 测试范围
- 管理端登录图形验证码获取、刷新与登录校验。
- 系统设置主题 Tab 新增二维码上传配置。
- 登录页二维码展示布局与动态显隐。

## 2. 测试环境
- backend: 本地 Go 开发环境
- frontend: pnpm + Vite 本地环境

## 3. 用例结果
- [x] 后端编译通过（`cd backend && go test $(go list ./... | rg -v "project/test")`）
  - 结果：通过（`project/test` 依赖本地数据库环境，按现有项目约定排除后其余包通过）
- [x] 前端类型检查通过（`cd frontend && pnpm typecheck`）
  - 结果：通过
- [ ] 前端 lint 全量通过（`cd frontend && pnpm lint`）
  - 结果：未通过（仓库存在大量历史 `no-empty/no-unused-vars` 问题，非本次改动引入）
- [x] 前端变更文件定向 lint（`cd frontend && pnpm exec eslint --no-warn-ignored ...`）
  - 结果：通过（本次改动相关文件无新增 lint 问题）
- [x] 后端编译复测（联调修复后）（`cd backend && go test $(go list ./... | rg -v "project/test")`）
  - 结果：通过
- [x] 前端类型复测（联调修复后）（`cd frontend && pnpm typecheck`）
  - 结果：通过
- [x] 前端登录页变更文件定向 lint（`cd frontend && pnpm exec eslint --no-warn-ignored src/views/_builtin/login/modules/pwd-login.vue src/views/_builtin/login/index.vue`）
  - 结果：通过
- [x] 前端 loading 插件修复验证（`cd frontend && pnpm exec eslint --no-warn-ignored src/plugins/loading.ts` + `pnpm typecheck`）
  - 结果：通过
- [ ] 手工验证：验证码错误/过期时登录失败
- [ ] 手工验证：主题设置保存二维码后登录页正确展示
- [ ] 手工验证：主题设置上传后预览图正确显示
- [ ] 手工验证：主题设置标签在 1366+ 分辨率下不换行
- [ ] 手工验证：无其他登录方式时不显示 “or” 分割线
- [ ] 手工验证：登录背景动效展示为电路板电流粒子效果
- [ ] 手工验证：登录页不再停留在全屏 loading（刷新/切换语言后均可进入表单）

## 4. 缺陷与风险
- 全量 `pnpm lint` 被历史问题阻塞，当前仅完成本次改动文件的定向 lint 校验。
- 仍需补充页面联调与视觉验收（二维码展示样式、移动端适配）。

## 5. 结论
- 代码改造与静态检查已完成，待手工联调通过后可进入 `review`。
