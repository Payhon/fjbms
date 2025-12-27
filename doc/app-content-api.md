# APP 内容（政策/FAQ/反馈）接口文档

本文档面向 **APP/小程序端开发**，描述 `/api/v1/app/content/*` 相关接口（单页内容、FAQ、用户反馈），并补充反馈图片上传接口。

## 约定

### Base URL

- 后端服务：`{SERVER}`
- API 前缀：`/api/v1`

### 必带请求头（强烈建议）

- `X-TenantID`: 租户 ID（不传时服务端会默认使用“第 1 个租户”）
- `Content-Type: application/json`（JSON 接口）

### 登录态请求头（需要登录的接口必带）

- `x-token`: 登录成功返回的 token（本项目使用 `x-token`，不是 `Authorization: Bearer`）

### 语言（lang）

- 目前支持：`zh-CN`、`en-US`
- 其他语言值（或不传）默认使用：`en-US`
- 服务端返回字段 `lang` 会被规范化为 `zh-CN` 或 `en-US`

### 统一响应结构（业务成功）

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

> `code != 200` 表示业务失败，`message` 为错误原因。
>
> 注意：当 `x-token` 无效/过期时，中间件会返回 HTTP 401，并返回形如 `{ "code": 40102, "message": "token has expired" }` 的结构（字段与上面成功结构略有差异）。

## 1. 单页内容（用户政策 / 隐私政策）

用于 APP 登录页、我的页等场景展示政策文本。

### ContentKey 枚举

- `user_policy`：用户政策
- `privacy_policy`：隐私政策

### 1.1 获取单页内容（无需登录）

`GET /api/v1/app/content/pages/{content_key}`

Query:
- `appid` string 必填：应用 AppID（`apps.appid`）
- `lang` string 可选：`zh-CN` / `en-US`

Header:
- `X-TenantID`（推荐）

成功响应 `data`：
```json
{
  "content_key": "privacy_policy",
  "lang": "zh-CN",
  "title": "隐私政策",
  "content_markdown": "# 标题\\n...",
  "content_html": "<h1>标题</h1>...",
  "updated_at": "2025-12-27 15:04:05"
}
```

渲染建议：
- APP 端建议使用 `content_html` + `rich-text` 渲染（避免 Markdown 在端上再解析）。
- `content_markdown` 主要用于调试/兜底。

## 2. FAQ（常见问题）

FAQ 不分类，支持 **置顶 + 排序**（服务端默认按 `is_pinned DESC, sort DESC, updated_at DESC` 排序）。

### 2.1 FAQ 列表（无需登录）

`GET /api/v1/app/content/faqs`

Query:
- `appid` string 必填：应用 AppID（`apps.appid`）
- `lang` string 可选：`zh-CN` / `en-US`
- `page` int 必填：页码（从 1 开始）
- `page_size` int 必填：每页数量（1~1000）

Header:
- `X-TenantID`（推荐）

成功响应 `data`：
```json
{
  "list": [
    {
      "id": "uuid",
      "question": "如何重置密码？",
      "answer_markdown": "1) ...",
      "answer_html": "<ol>...</ol>",
      "is_pinned": true,
      "sort": 100,
      "updated_at": "2025-12-27 15:04:05"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

渲染建议：
- 列表页可只展示 `question`，详情展开时展示 `answer_html`（或 `answer_markdown` 兜底）。

## 3. 用户反馈

反馈必须登录后提交；管理员回复后，用户在 APP 端可见（“我的反馈”列表/详情展示 `reply`）。

### 反馈状态枚举（status）

- `NEW`：新建
- `PROCESSING`：处理中
- `RESOLVED`：已解决
- `CLOSED`：已关闭

### 3.1 上传反馈图片（需要登录）

`POST /api/v1/file/up`

Header:
- `x-token` 必填
- `X-TenantID` 推荐（上传接口在登录态下；如不传，服务端会按 token tenant/默认租户处理）

Body（`multipart/form-data`）：
- `file`：文件
- `type`：固定传 `feedback`

成功响应 `data` 示例：
```json
{
  "path": "./files/feedback/2025-12-27/2a0f...c.png"
}
```

说明：
- 之后在提交反馈接口的 `images` 字段中直接传该 `path` 列表。
- 展示图片时可按项目约定拼接访问地址：`{SERVER}` + `path.slice(1)`（例如把 `./files/...` 转为 `/files/...`）。

### 3.2 提交反馈（需要登录）

`POST /api/v1/app/content/feedback`

Header:
- `x-token` 必填
- `X-TenantID` 建议必传（登录后接口会校验 tenant 与 token 一致；缺省时服务端会优先使用 token tenant）

请求体：
```json
{
  "appid": "app_xxx",
  "content": "遇到闪退问题，步骤：...",
  "images": ["./files/feedback/2025-12-27/xxx.png"],
  "platform": "android",
  "app_version": "1.2.3",
  "device_model": "Pixel 8",
  "os_version": "Android 15"
}
```

成功响应 `data`：
```json
{ "id": "uuid" }
```

### 3.3 我的反馈列表（需要登录）

`GET /api/v1/app/content/feedback/mine`

Header:
- `x-token` 必填
- `X-TenantID` 建议必传

Query:
- `appid` string 可选：应用 AppID（不传则返回当前用户全部反馈）
- `page` int 必填
- `page_size` int 必填

成功响应 `data`：
```json
{
  "list": [
    {
      "id": "uuid",
      "appid": "app_xxx",
      "content": "遇到闪退问题...",
      "images": ["./files/feedback/2025-12-27/xxx.png"],
      "status": "PROCESSING",
      "reply": "已收到，我们会在下个版本修复",
      "replied_at": "2025-12-27 16:30:00",
      "created_at": "2025-12-27 15:04:05",
      "updated_at": "2025-12-27 16:30:00"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20
}
```

### 3.4 我的反馈详情（需要登录）

`GET /api/v1/app/content/feedback/{id}`

Header:
- `x-token` 必填
- `X-TenantID` 建议必传

成功响应 `data`：同“我的反馈列表”的单条结构。

