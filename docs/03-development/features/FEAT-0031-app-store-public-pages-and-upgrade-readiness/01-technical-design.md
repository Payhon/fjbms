# FEAT-0031 App 上架准备与公共页面完善 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-04-02
- related_feature: FEAT-0031
- version: v0.1.0

## 1. 方案概览
本次改造分为四层：
- Backend：补充公开 App 信息接口，并微调现有公开内容读取口径。
- Frontend：新增三个免认证公共页面，承载隐私政策、用户政策和发行下载页。
- UniApp：将审核相关协议入口切换到公网 H5，并修正升级请求与租户/域名配置一致性。
- 文档与验收：同步功能文档、测试报告和发布说明，便于上架前检查。

## 2. 接口与数据结构
- 公开内容页接口：
  - 复用 `GET /api/v1/app/content/pages/{content_key}`
  - `appid` 保持可选
  - 无 `appid` 时在租户 `d616bcbb` 内回退到首个应用
  - `lang` 默认 `zh-CN`
- 公开 App 信息接口：
  - 新增 `GET /api/v1/app/public/info`
  - 入参：`appid`
  - 响应字段：
    - `appid`
    - `name`
    - `description`
    - `introduction`
    - `icon_url`
    - `screenshot`
    - `app_android`
    - `app_ios`
    - `app_harmony`
    - `h5`
- 现有后台数据结构不变：
  - `apps`
  - `app_versions`
  - `app_content_pages`
  - `app_content_page_i18n`

## 3. 关键流程
1. 用户访问公共页时，前端路由进入 `/public/app/privacy`、`/public/app/user-policy` 或 `/public/app/download`。
2. 公共页读取查询参数 `appid` 与 `lang`，未传 `lang` 时默认中文。
3. 隐私政策与用户政策页调用公开内容接口并渲染 Markdown / HTML 内容。
4. 下载页调用公开 App 信息接口，获取图标、简介、截图与平台下载地址。
5. 下载页根据 UA 判断当前设备环境，优先展示对应平台入口。
6. UniApp 登录、注册页通过 `web-view` 打开公网 H5 协议页，并把 `appid` 与 `lang` 透传到 URL。
7. App 启动时按现有升级模块检查版本，后端返回稳定版信息后进入下载或弹窗流程。

## 4. 安全与权限
- 公共页仅面向已发布内容，不暴露后台草稿内容。
- 公开 App 信息接口仍限制在生产租户 `d616bcbb` 下读取，避免跨租户数据泄露。
- UniApp 打开的公网 H5 链接不携带敏感 token，协议页仅展示公开文本内容。
- 升级检查接口继续使用现有业务响应结构，不改动弹窗交互和安装行为。

## 5. 测试策略
- 后端：
  - 验证公开内容页缺省 `appid` 时的默认应用回退逻辑。
  - 验证公开 App 信息接口在 `appid` 缺失、无效和正常场景下的响应。
  - 验证升级检查接口在 Android / iOS / Harmony 场景下返回结果一致性。
- 前端：
  - 验证三个公共页的路由可直接访问。
  - 验证下载页在移动端与桌面端的按钮展示规则。
  - 验证管理端表单在保存与编辑时数据结构不变。
- UniApp：
  - 验证登录、注册设密页协议跳转参数正确。
  - 验证关于页仍保持原生内容页。
  - 验证启动升级检测不影响首次启动与登录流程。

## 6. 兼容性与迁移
- 不新增 SQL 迁移。
- 不改变现有 App 内容管理的数据模型。
- 公共页先按单租户实现，后续如需复用到其他租户，再单独立项做多租户公共页方案。

