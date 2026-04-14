# FEAT-0037 用户名字段、账号设置增强与后台用户表格展示 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-04-11
- related_feature: FEAT-0037
- version: v0.1.0

## 1. 测试范围
- `users.username` 字段与历史补丁 SQL。
- APP / 小程序账号注册、设定账号、手机号换绑。
- APP / 小程序密码登录纯数字账号解析顺序。
- UniApp “我的 / 设置”页面展示。
- 后台三张用户表格用户名展示与查询。

## 2. 测试环境
- Backend：本地代码编译与定向校验
- Frontend：`pnpm` TypeScript / 构建校验
- UniApp：`pnpm exec tsc --noEmit`
- 数据库：SQL 脚本静态检查，待测试环境执行补丁

## 3. 用例结果
- [x] Frontend `pnpm typecheck` 通过，后台三张用户表格已补充“用户名”字段展示代码。
- [x] UniApp `pnpm exec tsc --noEmit` 通过，`我的/设置` 页账号与手机号展示逻辑已完成调整。
- [x] Backend `go test ./internal/...` 通过，用户相关服务包编译与测试通过。
- [x] Backend `go test ./internal/api ./internal/dal ./internal/service -count=1` 通过，覆盖本次纯数字账号登录解析改动。
- [ ] 手机号注册默认用户名为手机号
- [ ] 邮箱注册默认用户名为邮箱
- [ ] 微信直注册默认用户名为空
- [ ] 设定账号仅首次成功
- [ ] 手机号换绑后 `users.phone_number` 与 `user_identities` 同步更新
- [ ] 旧 `username == 旧手机号` 时，换绑后自动切到新手机号
- [ ] 纯数字密码登录优先命中 `username`，未命中时回退 `phone_number`
- [ ] UniApp “我的”页不再错误显示“未设置手机号”
- [ ] 后台三张表格可展示用户名并支持查询

## 4. 缺陷与风险
- 待测试环境执行 `backend/sql/48.sql` 后验证历史冲突回填数据。
- 若本地未接入真实微信环境，微信小程序一键换绑需补真机验证。
- `go test ./...` 仍存在仓库历史失败：
  - `backend/initialize/test.TestSetDevice`
  - `backend/test.TestDatebase`
  以上失败与本次用户名改造无直接关联。

## 5. 结论
- 代码改造与静态校验已完成，剩余工作为数据库补丁落地与联调验证。
