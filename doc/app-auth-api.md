# APP / 微信小程序认证接口文档

本文档面向 APP/小程序端开发，描述 **新增的 `/api/v1/app/auth/*` 账号体系接口**（手机号/邮箱验证码登录、注册、找回密码、绑定/解绑、微信小程序一键登录/绑定手机号）。

## 约定

### Base URL

- 后端服务：`{SERVER}`
- API 前缀：`/api/v1`

### 必带请求头

- `X-TenantID`: 租户 ID（**APP/小程序认证接口必填**）
- `Content-Type: application/json`

### 登录态请求头（登录后接口必带）

- `x-token`: 登录成功返回的 token

### 统一响应结构

服务端所有接口返回统一结构（示例）：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

> `code != 200` 表示业务失败，`message` 为错误原因。

## 场景枚举（scene）

发送验证码时 `scene` 必须传以下之一（大小写不敏感，服务端会转成大写）：

- `LOGIN`：登录
- `REGISTER`：注册
- `RESET_PASSWORD`：找回/重置密码
- `BIND`：绑定手机号/邮箱

注意：**验证码校验按 `tenant_id + channel + scene + identifier` 维度匹配**，因此发送验证码与提交验证码时的 `scene` 必须一致。

## 认证接口（无需登录）

### 1) 发送邮箱验证码

`POST /api/v1/app/auth/email/code`

请求头：`X-TenantID`

请求体：
```json
{
  "email": "user@example.com",
  "scene": "REGISTER"
}
```

### 2) 发送手机号验证码

`POST /api/v1/app/auth/phone/code`

请求体：
```json
{
  "phone_prefix": "+86",
  "phone_number": "13100000000",
  "scene": "LOGIN"
}
```

### 3) 手机号验证码登录

`POST /api/v1/app/auth/phone/login_by_code`

请求体：
```json
{
  "phone_prefix": "+86",
  "phone_number": "13100000000",
  "verify_code": "123456"
}
```

成功响应 `data`：
```json
{
  "token": "xxxxx",
  "expires_in": 3600
}
```

### 4) 邮箱验证码登录

`POST /api/v1/app/auth/email/login_by_code`

请求体：
```json
{
  "email": "user@example.com",
  "verify_code": "123456"
}
```

### 5) 手机号注册

`POST /api/v1/app/auth/phone/register`

请求体（`password` 可选）：
```json
{
  "phone_prefix": "+86",
  "phone_number": "13100000000",
  "verify_code": "123456",
  "password": "Abcd1234!@#"
}
```

返回同登录，直接下发 token。

### 6) 邮箱注册

`POST /api/v1/app/auth/email/register`

请求体（`password` 可选）：
```json
{
  "email": "user@example.com",
  "verify_code": "123456",
  "password": "Abcd1234!@#"
}
```

### 7) 手机号找回/重置密码（验证码）

`POST /api/v1/app/auth/phone/reset_password`

请求体：
```json
{
  "phone_prefix": "+86",
  "phone_number": "13100000000",
  "verify_code": "123456",
  "password": "NewPassw0rd!"
}
```

### 8) 邮箱找回/重置密码（验证码）

`POST /api/v1/app/auth/email/reset_password`

请求体：
```json
{
  "email": "user@example.com",
  "verify_code": "123456",
  "password": "NewPassw0rd!"
}
```

### 9) 微信小程序一键登录（openid）

`POST /api/v1/app/auth/wxmp/login`

请求体：
```json
{
  "code": "wx.login() 返回的 code"
}
```

返回同登录，直接下发 token。

> 依赖后端已配置该 `X-TenantID` 对应的微信小程序 `appid/app_secret`。

## 认证接口（需要登录）

以下接口需请求头同时包含：`X-TenantID` + `x-token`。

### 10) 查询当前账号绑定信息

`GET /api/v1/app/auth/bindings`

成功响应 `data` 示例：
```json
{
  "user_id": "xxxx",
  "list": [
    {
      "id": "xxxx",
      "identity_type": "WXMP_OPENID",
      "identifier": "openid_xxx",
      "is_primary": true,
      "verified_at": "2025-12-25T07:00:00Z",
      "status": "ACTIVE"
    }
  ]
}
```

### 11) 微信小程序一键绑定手机号（getPhoneNumber）

`POST /api/v1/app/auth/wxmp/bind_phone`

请求体：
```json
{
  "phone_code": "wx.getPhoneNumber 返回的 code"
}
```

### 12) 微信小程序用户信息解析/保存（getUserProfile）

`POST /api/v1/app/auth/wxmp/profile`

请求体（按需传字段）：
```json
{
  "nick_name": "张三",
  "avatar_url": "https://...",
  "gender": 1,
  "country": "China",
  "province": "Guangdong",
  "city": "Shenzhen",
  "language": "zh_CN"
}
```

说明：
- 该接口用于把小程序端拿到的用户资料保存到后端（`users.name/avatar_url/additional_info`）。
- 仅允许 `END_USER`（终端用户）调用更新，避免影响 WEB/业务账号。

### 13) 绑定手机号（短信验证码）

`POST /api/v1/app/auth/bind/phone`

请求体：
```json
{
  "phone_prefix": "+86",
  "phone_number": "13100000000",
  "verify_code": "123456"
}
```

### 14) 绑定邮箱（邮箱验证码）

`POST /api/v1/app/auth/bind/email`

请求体：
```json
{
  "email": "user@example.com",
  "verify_code": "123456"
}
```

### 15) 解绑手机号/邮箱

`POST /api/v1/app/auth/unbind`

请求体：
```json
{
  "identity_type": "PHONE"
}
```

约束：
- 不允许解绑最后一个可登录身份（至少保留一个）。

## 配置接口（WEB 端使用）

这些接口给 WEB 端配置页面使用（需要登录）。通常：
- `TENANT_ADMIN`：配置自己租户
- `SYS_ADMIN`：可通过 query 参数 `tenant_id` 指定租户进行配置

### 1) 获取模板列表

`GET /api/v1/app/auth/config/templates`

SYS_ADMIN 指定租户示例：
`GET /api/v1/app/auth/config/templates?tenant_id=xxxxx`

### 2) 新增/更新模板

`POST /api/v1/app/auth/config/templates`

请求体示例（短信-登录场景）：
```json
{
  "channel": "SMS",
  "scene": "LOGIN",
  "provider": "ALIYUN",
  "provider_template_code": "SMS_123456789",
  "status": "OPEN"
}
```

请求体示例（邮件-注册场景，内容支持 `{{code}}` 或 `${code}` 占位符）：
```json
{
  "channel": "EMAIL",
  "scene": "REGISTER",
  "subject": "注册验证码",
  "content": "您的验证码是：{{code}}，5分钟内有效。",
  "status": "OPEN"
}
```

### 3) 获取微信小程序配置

`GET /api/v1/app/auth/config/wxmp`

> 出于安全考虑，响应不会返回 `app_secret` 明文。

### 4) 新增/更新微信小程序配置

`POST /api/v1/app/auth/config/wxmp`

请求体：
```json
{
  "appid": "wx123...",
  "app_secret": "xxxx",
  "status": "OPEN",
  "remark": "小程序配置"
}
```

## 备注（实现细节）

- 供应商密钥等“服务配置”复用现有 `notification_services_config`（SYS_ADMIN 配置），短信目前实现为 **阿里云**。
- 模板按租户/通道/场景存储：`auth_message_templates(tenant_id, channel, scene)` 唯一。
- 新增账号身份表：`user_identities`，用于同一用户绑定多个身份（PHONE/EMAIL/WXMP_OPENID）。
