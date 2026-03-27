# FEAT-0026 UniApp 账号注销 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-03-26
- related_feature: FEAT-0026
- version: v0.1.0

## 1. 方案概览
方案分为前后端两层：
- UniApp 设置页增加“账号注销”危险操作入口，采用两段式确认。
- 后端在已登录的 `app/auth` 路由组新增 `POST /api/v1/app/auth/delete_account` 接口。
- 服务层仅允许 `END_USER` 调用，先校验当前密码，再在事务中删除用户及其 APP 侧关联数据。

## 2. 接口与数据结构
- 新增请求体 `model.AppDeleteAccountReq`
  - `password: string` 当前密码，必填。
- 新增接口
  - `POST /api/v1/app/auth/delete_account`
  - Header: `X-TenantID`, `x-token`
  - Response: 统一 `model.Response`

需清理的数据范围：
- `user_identities` 当前用户的全部身份记录。
- `device_user_bindings` 当前用户的设备绑定关系。
- `app_device_added_records` 当前用户移动端“我添加的设备”记录。
- `message_push_manage`、`message_push_log` 当前用户的推送配置/记录。
- `user_roles` 当前用户角色关系。
- `users` 当前用户主记录。

## 3. 关键流程
1. UniApp 用户点击“账号注销”。
2. 客户端先弹出不可恢复提示，用户确认后再弹出密码输入弹窗。
3. 客户端调用 `POST /api/v1/app/auth/delete_account`，提交当前密码。
4. 服务端读取 `claims` 对应用户，校验：
   - 租户匹配
   - `user_kind == END_USER`
   - 当前密码与 `users.password` 哈希匹配
5. 服务端事务删除关联数据与 `users` 记录。
6. 客户端在成功后清空本地登录态并跳转登录页。

## 4. 安全与权限
- 接口仅在已登录的 `appAuthAuthed` 路由组开放。
- 强制 `RequireTenantHeaderMatchClaims()`，避免跨租户误删。
- 仅允许 `END_USER` 自助注销，拒绝组织账号/后台账号。
- 使用现有 bcrypt 密码校验，避免仅凭现有 token 执行高风险删除。

## 5. 测试策略
- 后端：定向 `go test` / 编译，覆盖接口与服务新增逻辑。
- UniApp：检查设置页入口、风险确认、密码必填、成功后退出登录流程。
- 回归：确认既有“修改密码”“账号绑定”“退出登录”流程未受影响。

## 6. 兼容性与迁移
- 不新增 SQL 迁移；本次依赖现有表结构执行删除。
- 对未部署新客户端的旧版本无影响。
- 若历史终端用户缺少部分关联表记录，删除逻辑应允许 0 行受影响。
