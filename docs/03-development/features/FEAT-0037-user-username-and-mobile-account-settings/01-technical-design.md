# FEAT-0037 用户名字段、账号设置增强与后台用户表格展示 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-04-07
- related_feature: FEAT-0037
- version: v0.1.0

## 1. 方案概览
本次拆分 `users.name` 与新增 `users.username` 的职责：
- `name`：昵称 / 姓名，继续用于资料展示和后台人员姓名。
- `username`：账号名，作为稳定的账号展示字段，不参与登录鉴权。

实现分三层：
1. 数据层新增 `users.username` 和唯一索引，并补充历史回填 SQL。
2. 后端 APP 账号体系、后台用户返回结构、终端用户聚合接口统一返回 `username`。
3. UniApp 设置页与后台用户表格新增 `username` 展示和查询能力。

## 2. 接口与数据结构
### 2.1 数据库
- `public.users`
  - 新增 `username varchar(255) NULL`
  - 新增唯一索引：`(tenant_id, lower(username)) WHERE username IS NOT NULL AND username <> ''`

### 2.2 默认值策略
- APP 手机号注册：`username = phone_number`
- APP 邮箱注册：`username = email`
- 微信小程序直注册：`username = NULL`
- 后台 / 组织账号创建：优先 `email`，无真实邮箱时回退手机号

### 2.3 后端返回
- `/api/v1/user/detail`
- `/api/v1/user`
- `/api/v1/end_user`

以上接口都补充 `username` 字段；`/api/v1/end_user` 保留 `user_name` 作为姓名/昵称，并新增独立 `username`。

### 2.4 移动端设置相关接口
- `POST /api/v1/app/auth/username`
  - 请求体改为 `{"username": "..."}`，仅允许 `END_USER` 首次设置。
- `POST /api/v1/app/auth/bind/phone`
  - 保持路由不变，语义扩展为绑定或换绑手机号。
- `POST /api/v1/app/auth/wxmp/bind_phone`
  - 保持路由不变，支持微信小程序一键绑定或换绑手机号。

## 3. 关键流程
### 3.1 历史补丁
1. 找出 `username` 为空的用户。
2. 过滤占位邮箱 `u_<id>@app.local`。
3. 根据 `user_kind` 选择手机号 / 真实邮箱作为候选值。
4. 在同租户内对冲突候选值追加稳定后缀，最后写回 `username`。

### 3.2 APP 账号创建
1. 手机号 / 邮箱注册成功后创建 `users` 记录。
2. 按注册类型直接写入默认 `username`。
3. 微信直注册只创建占位邮箱和微信身份，不自动生成 `username`。

### 3.3 设定账号
1. 终端用户在设置页提交 `username`。
2. 服务层校验租户、用户类型、仅首次设置和唯一性。
3. 成功后只写 `users.username`，不影响 `name`。

### 3.4 手机号换绑
1. 绑定接口检测当前用户是否已有 `PHONE` 身份。
2. 无旧手机号时走新增绑定；有旧手机号时走换绑更新。
3. 同一事务内更新 `user_identities` 和 `users.phone_number`。
4. 如果旧 `username` 与旧手机号相同，且新手机号未占用用户名，则同步改为新手机号。

## 4. 安全与权限
- `username` 不参与登录，不影响现有密码、验证码和 JWT 逻辑。
- `SetUsername`、绑定 / 换绑手机号接口仅允许已登录且租户匹配的终端用户调用。
- 后台用户表格仅展示 `username`，不开放后台编辑，避免绕过“仅首次设置”规则。

## 5. 测试策略
- 后端定向测试 / 编译：
  - `internal/service/app_auth.go`
  - `internal/service/end_user.go`
  - `internal/dal/users.go`
- UniApp 运行态验证：
  - “我的”页手机号显示
  - 设置页账号展示与设定账号
  - 手机号换绑
- 前端后台验证：
  - 三张用户表格的用户名列展示
  - 用户名搜索
- 数据修复验证：
  - 执行 `backend/sql/48.sql`
  - 抽样核对手机号用户 / 邮箱用户 / 微信直注册用户

## 6. 兼容性与迁移
- 登录方式不变，旧客户端不会因新增 `username` 字段失效。
- 新版 UniApp 会优先读取 `phone_number`，并兼容旧缓存中的 `mobile`。
- 需要在部署后执行 `backend/sql/48.sql` 完成历史数据补齐。
