# FEAT-0055 PACK 厂微信小程序配置接入 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-05-29
- related_feature: FEAT-0055
- version: v0.1.0

## 1. 方案概览
- 以 `orgs.org_type = PACK_FACTORY` 的组织为配置主体。
- 新增 `pack_wxmp_configs` 保存 PACK 厂与微信小程序配置的关系。
- `apps` 继续作为 APP/小程序内容页实体；`app_content_pages` 继续承载协议、关于我们等内容。
- 微信登录接口增加可选 `appid`，用于从 PACK 配置中解析微信 AppSecret；缺省时保留租户级配置兜底。
- UniApp 在 `MP-WEIXIN` 下通过 `uni.getAccountInfoSync().miniProgram.appId` 识别当前微信小程序。

## 2. 接口与数据结构
### 数据表
- `pack_wxmp_configs`
  - `id`
  - `tenant_id`
  - `org_id`
  - `app_id`
  - `wx_appid`
  - `app_secret`
  - `status`
  - `home_banner_url`
  - `login_logo_url`
  - `remark`
  - `created_at`
  - `updated_at`
- 唯一约束：
  - `tenant_id + org_id`
  - `tenant_id + wx_appid`

### 后端接口
- `GET /api/v1/org/{org_id}/wxmp-config`
  - 返回 PACK 厂小程序配置，不返回 `app_secret` 明文。
- `PUT /api/v1/org/{org_id}/wxmp-config`
  - 保存 AppID、AppSecret、状态、Banner、备注。
  - AppSecret 为空时保留旧密钥；首次创建必须提供 AppSecret。
- `GET /api/v1/app/wxmp/runtime?appid=...`
  - 公开接口，返回当前小程序运行时配置：状态、Banner、登录 Logo、关联 AppID、来源类型、登录方式控制和 PACK 机构名称。
  - 命中 `pack_wxmp_configs` 时返回 `source_type=PACK`、`login_only=true`。
  - 命中租户级 `wx_mp_apps` 时返回 `source_type=TENANT`、`login_only=false`。
- `GET /api/v1/app_users/source-options`
  - 返回 APP 用户管理左侧来源树，包含 App 端与动态微信小程序端节点。
- `GET /api/v1/app_users`
  - 返回 APP 用户增强列表，支持 `source_type`、`wx_appid`、`keyword`、`status` 筛选。
- `POST /api/v1/app/auth/wxmp/login`
  - 请求体新增可选 `appid`。
- `POST /api/v1/app/auth/wxmp/bind`
  - 请求体新增可选 `appid`。
- `POST /api/v1/app/auth/wxmp/bind_phone`
  - 请求体新增可选 `appid`。

## 3. 关键流程
1. WEB 后台在 PACK 厂列表点击“小程序配置”。
2. 后台读取 `org/{org_id}/wxmp-config`，展示基础接入、Banner、内容协议入口。
3. 保存配置时校验组织属于当前租户且类型为 `PACK_FACTORY`。
4. 保存配置时按 `tenant_id + wx_appid` 查找或创建 `apps` 记录，并写入 `pack_wxmp_configs.app_id`。
5. UniApp 小程序启动或首页加载时读取当前微信 AppID，再请求运行时配置。
6. 登录页按 runtime 判断登录方式：PACK 小程序隐藏账号密码登录，租户级小程序保留账号密码登录和微信登录入口。
7. 微信登录时前端提交 `code + appid`，后端优先用 PACK 配置调用微信 code2session，未命中时回退租户级配置。
8. 我的 > 关于我们页按 runtime 中的 `org_name` 展示 PACK 小程序关联机构名称，并通过当前微信 AppID 读取该小程序配置的关于我们、用户协议和隐私政策内容。
9. 我的 > 联系客服页通过当前微信 AppID 读取该小程序配置的 `contact_service` 内容。
10. 新身份写入 `identifier = wx_appid + ':' + openid`，实现小程序隔离。
11. APP 用户管理按 `user_identities` 判断来源：`PHONE/EMAIL` 归入 App 端，`WXMP_OPENID` 按 `identifier` 解析小程序 AppID。

## 4. 安全与权限
- PACK 小程序配置接口必须登录 WEB 后台。
- 配置接口仅允许当前租户范围内组织。
- `org_id` 必须对应 `PACK_FACTORY`。
- 查询接口不返回 `app_secret`。
- 公开运行时接口只返回前端展示所需字段。
- 微信登录不信任前端 org_id，只按 AppID 在当前租户下查配置。

## 5. 测试策略
- 后端覆盖配置 CRUD、唯一约束、非 PACK 拒绝、公开运行时、微信登录配置选择和身份隔离。
- WEB 覆盖 PACK 厂配置弹窗、保存回显、Banner URL 和关于我们/用户协议/隐私政策/联系客服内容入口。
- UniApp 覆盖 PACK 小程序登录入口隐藏、租户级小程序账号密码登录保留、AppID 透传、Banner/登录 Logo/内容读取、关于我们厂商名和联系客服内容展示。
- APP 用户管理覆盖来源树、来源筛选、增强字段展示、冻结/删除回归。

## 6. 兼容性与迁移
- 新配置仅影响提交了 `appid` 的微信小程序登录。
- 未提交 `appid` 时继续使用现有 `wx_mp_apps` 租户级配置。
- 历史 `WXMP_OPENID` 身份不迁移；旧小程序仍可按旧逻辑登录。
- `apps` 记录已有 `tenant_id + appid` 唯一约束，可复用承载小程序内容。
