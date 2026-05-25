# FEAT-0054 后台附件管理 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-05-19
- related_feature: FEAT-0054
- version: v0.1.0

## 1. 自动化/静态检查
- [x] `cd backend && go test ./internal/service ./internal/api ./router/apps`
  - 结果：通过。
- [x] `cd frontend && pnpm typecheck`
  - 结果：通过。
- [x] `cd frontend && pnpm exec eslint src/views/management/attachment/index.vue src/service/api/file.ts src/service/api/index.ts src/router/elegant/imports.ts src/router/elegant/routes.ts src/router/elegant/transform.ts src/typings/elegant-router.d.ts`
  - 结果：通过。
- [x] `cd frontend && pnpm exec eslint src/views/management/attachment/index.vue src/typings/api.d.ts`
  - 结果：通过，覆盖业务类型下拉与上传人账号/名称显示调整。
- [ ] `make update-frontend-prod`
  - 结果：前端生产构建通过并生成更新包，上传更新阶段失败；当前 shell 缺少 `FJBMS_PROD_SSH_PASSWORD` 环境变量。
- [ ] `cd frontend && pnpm lint`
  - 结果：失败，错误来自既有旧文件的大量 `no-empty` 等问题，非本次新增附件管理文件。

## 2. 手工回归
- [ ] 系统管理下显示“附件管理”菜单。
- [ ] 附件列表显示当前租户全部附件，不限制当前用户上传。
- [ ] 关键词、业务类型、存储位置、上传时间范围筛选生效。
- [ ] 图片附件可弹窗预览。
- [ ] 非图片附件可新窗口预览。
- [ ] 本地附件可下载。
- [ ] 云存储附件可打开下载 URL。
- [ ] 删除附件前出现强确认。
- [ ] 删除成功后列表刷新，存储对象不可继续访问。
- [ ] 云存储删除失败时数据库记录保留。

## 3. 风险
- 未执行浏览器运行态验收前，菜单权限与下载体验仍需以实际账号验证为准。
