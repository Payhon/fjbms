# FEAT-0037 用户名字段、账号设置增强与后台用户表格展示 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-04-11
- related_feature: FEAT-0037
- version: v0.1.0

## 1. 实施记录
1. 新建 FEAT-0037 文档目录，并在项目看板登记 Backend / Frontend / UniApp 条目。
2. 为 `users` 新增 `username` 字段、唯一索引和历史补丁 SQL。
3. 调整后端 APP 账号创建、设定账号、手机号绑定 / 换绑逻辑，统一 `username` 默认值和联动更新规则。
4. 扩展 `/user/detail`、`/user`、`/end_user` 返回结构，补充 `username`。
5. 修复 UniApp “我的”页手机号显示与设置页账号展示、设定账号、手机号换绑流程。
6. 为后台 `bms/system/user`、`app_manage/users`、`bms/end_user` 三张表新增“用户名”列及相应搜索能力。
7. 根据生产问题补充 `/api/v1/login` 纯数字账号解析修复：先查 `users.username`，查不到再按 `users.phone_number` 回退。
8. 为登录解析新增定向单测，覆盖邮箱、非法数字、用户名优先、手机号回退四种路径。

## 2. 当前状态
- 文档与看板已建档。
- 后端、UniApp、Frontend 代码已完成联动改造并完成本地格式化。
- 已完成密码登录解析顺序修复，兼容纯数字账号名用户。
- 已完成 Backend `go test ./internal/...`，用户相关服务包通过；全量 `go test ./...` 仍存在仓库内历史失败用例。
- 已完成 Frontend `pnpm typecheck` 与 UniApp `pnpm exec tsc --noEmit`。
- 待测试环境执行 `backend/sql/48.sql` 并完成真实短信 / 微信小程序换绑验证。
