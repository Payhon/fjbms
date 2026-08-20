# FEAT-0055 PACK 厂微信小程序配置接入 - 实现日志

- status: review
- owner: payhon
- last_updated: 2026-08-15
- related_feature: FEAT-0055
- version: v0.1.0

## 2026-05-26
1. 创建功能文档并同步开发计划。
2. 后端新增 `pack_wxmp_configs` 表和 SQL 迁移，支持租户内按 PACK 厂配置微信小程序 AppID、AppSecret、启停状态、首页 Banner URL 和备注。
3. 后端新增 PACK 厂小程序配置接口：`GET/PUT /api/v1/org/:id/wxmp-config`，保存配置时自动创建/复用 `apps` 记录作为内容页承载。
4. 后端新增公开运行配置接口：`GET /api/v1/app/wxmp/runtime`，小程序端可按当前微信 AppID 获取 Banner 和关联 App 信息。
5. 微信小程序登录、微信绑定、手机号绑定接口支持传入 `appid`，优先使用 PACK 厂小程序配置；用户身份标识按 `wx_appid:openid` 隔离，保留旧租户级 `wx_mp_apps` 兼容回退。
6. WEB 后台在组织管理 PACK 厂行增加“小程序配置”入口，支持配置小程序接入信息，并维护该小程序独立的关于我们、隐私协议、用户政策。
7. APP 内容管理补充 `about_us` 单页配置入口，供 PACK 小程序独立内容复用。
8. UniApp 微信小程序端登录页隐藏手机号/邮箱登录、注册、找回密码入口，仅展示微信登录；注册和找回密码页面在微信小程序构建下重定向回登录页。
9. UniApp 首页 Banner 在微信小程序构建下优先读取 PACK 小程序运行配置；关于我们、隐私协议、用户政策按真实微信小程序 AppID 读取。
10. 进入联调/验收阶段，待微信开发者工具或真机小程序回归。

## 2026-05-27
1. 修复测试环境 PACK 厂“小程序配置”弹窗首次打开报“未知错误”的问题。
2. 问题原因：未配置过小程序的 PACK 厂查询 `pack_wxmp_configs` 无记录时，后端返回 `CodeNotFound(100404)`；同时消息配置缺少 `100404` 文案，导致前端展示“未知错误”。
3. 修复方式：`GET /api/v1/org/:id/wxmp-config` 在 PACK 厂未配置时返回成功空配置，并默认 `status=OPEN`，用于支撑前端首次配置表单初始化。
4. 补充 `100404` 中英文消息配置，避免其他资源不存在场景继续显示通用未知错误。
5. 补充后端回归测试覆盖“PACK 厂存在但小程序配置不存在”的空配置返回场景。
6. 调整 WEB PACK 厂小程序配置弹框，首页 Banner 字段由 URL 文本输入改为共享图片上传组件，上传成功后继续写入 `home_banner_url`。
7. 调整 WEB PACK 厂小程序配置弹框布局为 TAB 页，分为“小程序基本信息”和“文案内容”；文案内容正文复用 APP 管理内容管理的 Markdown 编辑器。
8. 调整首页 Banner 字段为共享文件选择组件，可上传新图片，也可从已上传图片列表选择，保存字段仍为 `home_banner_url`。

## 2026-05-28
1. `pack_wxmp_configs` 增加 `login_logo_url` 字段，PACK 小程序配置接口和公开 runtime 接口同步返回登录 Logo。
2. WEB PACK 厂小程序配置弹框新增“登录 Logo”配置，复用文件选择组件，可上传或选择已上传图片。
3. UniApp 微信小程序登录页在 `MP-WEIXIN` 环境读取 runtime 配置，优先展示小程序关联登录 Logo，未配置时保留默认 Logo。
4. 后台 APP 管理 > 用户管理改为左侧来源树、右侧增强列表；来源树动态读取 PACK 小程序配置，不写死品牌。
5. 新增 `GET /api/v1/app_users/source-options` 和 `GET /api/v1/app_users`，按 `user_identities` 识别 App 端与微信小程序端用户来源，并补充身份、绑定设备、最近访问等字段。

## 2026-05-29
1. 优化共享 `FilePicker` 图片类文件回显体验，新增 `displayMode`、`previewWidth`、`previewHeight` 属性；图片业务默认以缩略图卡片回显，非图片文件保持原文件名输入框回显。
2. PACK 厂小程序配置弹框的首页 Banner 和登录 Logo 使用图片缩略图回显，保存字段仍分别为 `home_banner_url`、`login_logo_url`。
3. 调整小程序登录方式判断：runtime 接口新增 `source_type` 和 `login_only`，命中 PACK 配置时才隐藏账号密码登录；命中租户级 `wx_mp_apps` 时保留账号密码登录、注册和找回密码流程。
4. UniApp 登录、注册、找回密码页面统一通过当前微信 AppID 拉取 runtime 配置，只在 PACK 小程序下执行微信-only 限制。
5. UniApp 我的 > 设置页同步接入 runtime 判断，PACK 小程序下隐藏账号、修改密码、手机号绑定和 Email 绑定入口，租户级小程序和 APP/H5 保持原有账号安全能力。
6. UniApp 我的页取消头像外层矩形边框，保留头像组件自身圆形展示。
7. WEB PACK 厂小程序配置弹框的“文案内容”新增“联系客服”配置项，复用现有 `contact_service` 内容 Key，可按小程序独立保存和发布。
8. runtime 接口为 PACK 小程序补充 `org_name`，UniApp 我的 > 关于我们页优先展示小程序关联 PACK 厂机构名称。
9. UniApp 关于我们页的用户协议、隐私政策和联系客服页继续按当前微信 AppID 读取关联小程序内容，确保 PACK 小程序显示独立文案配置。

## 2026-08-15
1. 定位默认租户微信小程序协议页失败：UniApp 会传真实微信 AppID，而 APP 内容接口只按 `apps.appid` 查询；默认政策内容挂在 UniApp 主应用 ID 下，导致返回 `100404`。PACK 小程序保存配置时会创建同微信 AppID 的 `apps` 记录，因此未受影响。
2. 后端新增统一运行时 AppID 解析：优先直接命中 `apps.appid`；若未命中且 AppID 属于当前租户 `wx_mp_apps`，则复用租户默认应用；未知 AppID 继续返回不存在。
3. 将兼容解析应用到单页内容、FAQ、反馈创建和反馈列表过滤，避免默认小程序其他内容入口出现相同问题。
4. 新增定向测试，覆盖主应用 ID、PACK 微信 AppID、租户级微信 AppID、空 AppID 公开页回退和未知 AppID 拒绝。
5. 本次不修改 UniApp 代码，不需要重新提交微信小程序版本；生产发布仅更新后端二进制。
