# FEAT-0026 UniApp 账号注销 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-06-24
- related_feature: FEAT-0026
- version: v0.1.0

## 1. 方案概览
方案分为前后端两层：
- UniApp 设置页增加“账号注销”危险操作入口，采用两段式确认。
- 后端在已登录的 `app/auth` 路由组新增 `POST /api/v1/app/auth/delete_account` 接口。
- 服务层仅允许 `END_USER` 调用；默认先校验当前密码，PACK 微信小程序命中后端可信免密条件时跳过密码校验，再在事务中删除用户及其 APP 侧关联数据。

## 2. 接口与数据结构
- 新增请求体 `model.AppDeleteAccountReq`
  - `password?: string` 当前密码，非 PACK 免密场景必填。
  - `appid?: string` 当前微信小程序 AppID，仅小程序端传入。
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
2. 客户端先刷新微信小程序运行配置，再弹出不可恢复提示。
3. 非 PACK 场景用户确认后再弹出密码输入弹窗；PACK 微信小程序确认后直接调用注销接口。
4. 客户端调用 `POST /api/v1/app/auth/delete_account`，非 PACK 提交当前密码，微信小程序额外提交当前 `appid`。
5. 服务端读取 `claims` 对应用户，校验：
   - 租户匹配
   - `user_kind == END_USER`
   - 若 `appid` 命中启用中的 `pack_wxmp_configs`，且当前用户存在 `identity_type=WXMP_OPENID`、`identifier` 前缀为 `${appid}:`、`status=ACTIVE` 的身份记录，则跳过密码校验
   - 其他场景必须校验当前密码与 `users.password` 哈希匹配
6. 服务端事务删除关联数据与 `users` 记录。
7. 客户端在成功后清空本地登录态并跳转登录页。

## 4. 安全与权限
- 接口仅在已登录的 `appAuthAuthed` 路由组开放。
- 强制 `RequireTenantHeaderMatchClaims()`，避免跨租户误删。
- 仅允许 `END_USER` 自助注销，拒绝组织账号/后台账号。
- 非 PACK 免密场景使用现有 bcrypt 密码校验，避免仅凭现有 token 执行高风险删除。
- PACK 免密场景不信任前端 `isPackWxmp` 状态，只信任后端同租户 PACK 配置和当前用户 scoped 微信身份绑定。

## 5. 测试策略
- 后端：定向 `go test` 覆盖普通密码注销、PACK 绑定免密注销、伪造/未绑定/停用配置拒绝免密。
- UniApp：检查设置页入口、PACK 风险确认后直接注销、非 PACK 密码必填、成功后退出登录流程。
- 回归：确认既有“修改密码”“账号绑定”“退出登录”流程未受影响。

## 6. 兼容性与迁移
- 不新增 SQL 迁移；本次依赖现有表结构执行删除。
- 对未部署新客户端的旧版本无影响。
- 若历史终端用户缺少部分关联表记录，删除逻辑应允许 0 行受影响。
