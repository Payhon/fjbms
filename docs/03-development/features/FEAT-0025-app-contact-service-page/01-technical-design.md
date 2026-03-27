# FEAT-0025 APP 联系客服单页内容接入 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-03-25
- related_feature: FEAT-0025
- version: v0.1.0

## 1. 方案概览
复用现有 APP 内容管理的单页内容能力，将 `contact_service` 作为新的 `content_key` 接入。实现分为三层：
- 后端：扩展 `content_key` 白名单与接口注释，继续复用 `app_content_pages` / `app_content_page_i18n`。
- 管理端：扩展单页内容枚举，新增“联系客服”选项。
- UniApp：将“我的 > 联系客服”从占位页改造成实际内容展示页，请求 `/api/v1/app/content/pages/contact_service`。

## 2. 接口与数据结构
- 后端允许的 `content_key`：
  - `user_policy`
  - `privacy_policy`
  - `contact_service`
  - `about_us`
- 数据表不变：
  - `app_content_pages.content_key`
  - `app_content_page_i18n.{title, content_markdown, content_html}`

## 3. 关键流程
1. 管理员在管理端选择 APP、语言和“联系客服”。
2. 保存时调用现有 `/api/v1/app_content/pages/contact_service` `PUT` 接口。
3. 发布时调用现有 `/api/v1/app_content/pages/contact_service/publish` `POST` 接口。
4. UniApp 进入“我的 > 联系客服”页面后，请求 `/api/v1/app/content/pages/contact_service?appid=...&lang=...`。
5. 服务端按应用、租户、语言返回已发布内容，UniApp 通过 `rich-text` 渲染 `content_html`。

## 4. 安全与权限
- APP 端读取单页内容无需登录，但仍沿用租户头解析逻辑。
- 管理端接口权限不变，仍由现有内容管理权限控制。
- 不新增执行型客服动作，避免引入额外敏感能力。

## 5. 测试策略
- 后端：执行定向 Go 编译/测试，验证 `contact_service` 不会触发参数校验失败。
- 管理端：执行定向类型检查，验证 `ContentKey` 与单页选项扩展无报错。
- UniApp：静态检查页面逻辑，验证导航标题、空态与内容加载分支。

## 6. 兼容性与迁移
- 不需要 SQL 迁移，历史数据结构可直接承载新 `content_key`。
- 已有 `user_policy` / `privacy_policy` / `about_us` 行为保持不变。
