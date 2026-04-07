# FEAT-0031 App 上架准备与公共页面完善 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-04-03 02:10
- related_feature: FEAT-0031
- version: v0.1.0

## 1. 实施记录
1. 新建 FEAT-0031 功能文档目录，按功能规格、技术设计、实施日志、测试报告、发布说明五件套组织。
2. 梳理现有后台 App 管理、内容管理和升级中心能力，确认复用范围以现有 `apps`、`app_versions`、`app_content_pages` 为主。
3. 确认公开页面按生产租户 `d616bcbb` 实现，下载页依赖 `appid`，隐私政策与用户政策页支持缺省回退。
4. 确认 UniApp 协议入口采用混合方案：登录/注册跳公网 H5，关于页保留原生内容页。
5. 确认升级链路继续使用 `uni_modules/fjbms-upgrade`，仅修正配置一致性与请求租户来源，不改弹窗流程。
6. Backend 已完成：
   - 公开内容页 `appid` 改为可选，并在租户内回退首个应用。
   - 新增 `GET /api/v1/app/public/info` 公开接口，返回下载页所需 App 基础信息。
   - 在无登录分组挂载 `app/public/info` 路由，沿用 `X-TenantID` 头约束。
7. Frontend 已完成：
   - 新增 `/public/app/privacy`、`/public/app/user-policy`、`/public/app/download` 三个公开页视图。
   - 在自定义常量路由中加入 `public/app/*` 免登录路由，并补最小路由类型与视图映射。
   - App 管理表单补齐 `introduction`，并将图标 / Android / Harmony / 升级包 URL 改为按场景使用 `FilePicker`。
8. UniApp 已完成：
   - 新增公共 H5 协议页跳转辅助。
   - 登录页、注册设密页切换为公网 H5 协议入口。
   - 请求租户优先读取运行时 `tenant_id`，基础 URL 统一走 `serverAddress -> resolveBaseUrl()`。
9. 生产环境已执行：
   - 通过 `make update-frontend-prod` 发布 `frontend`，远端目录 `/www/fjia/fjbms/frontend` 已替换。
   - 通过 `make update-backend-prod` 发布 `backend`，`fjbms-backend.service` 已重启并恢复 `active (running)`。
10. 联调修正：
   - 发现生产租户 `d616bcbb` 仅配置了 `zh-CN` 协议内容，`lang=en-US` 请求会返回 `100404`。
   - 已修正后端单页内容语言回退顺序：优先请求语言，缺失时回退 `zh-CN`，最后回退 `en-US`。
11. 生产数据补录已完成：
   - 通过后端上传接口 `/api/v1/file/up` 上传 `_ui/appstore/export/iphone-65` 下 5 张 App Store 截图，并写回当前应用 `appid=__UNI__40EADE1` 的 `screenshot` 字段。
   - 在生产后台应用记录中补齐 `description`、`introduction`、`app_android`、`app_ios`、`app_harmony`、`h5` 字段。
   - 当前下载地址先使用占位链接，后续由业务侧在后台直接替换为正式安装包 / App Store 地址。
12. 公开下载页增强已完成：
   - 下载页新增应用简介、平台下载卡片和协议入口，不再只依赖单个主按钮和截图区域。
   - 后台 App 管理截图字段改为多文件 `FilePicker`，支持上传多张宣传图。
13. 英文协议内容已补录并发布：
   - `privacy_policy` 已新增 `en-US` 版本并发布。
   - `user_policy` 已新增 `en-US` 版本并发布。
14. 登录页底部“其他登录方式”区域已改为按当前运行环境动态显隐：
   - 微信小程序环境保留标题与微信登录按钮。
   - 非微信小程序环境不再显示空标题，避免底部出现无操作项占位。
15. 升级检测调试日志已补充：
   - `uni_modules/fjbms-upgrade/utils/call-check-version.ts` 现会在控制台打印 `/api/v1/app/upgrade/check` 的请求参数、接口响应和异常信息。
   - 仅针对升级检测接口定向打印，不扩大全局网络请求日志范围。

## 2. 待执行项
- UniApp 真机回归与升级包下载验证。
- 在后台 `APP 升级中心` 发布真实稳定版安装包 / 商店地址，用于触发生产自动升级提示。
- 根据最终验收结果确认是否切换文档状态到 `review` / `done`。

## 3. 当前状态
- 文档已进入 `in_progress` 阶段。
- 代码实现与生产发布已完成，生产公开数据和英文协议内容已补齐。
- 当前剩余事项主要是真机验收，以及将占位下载地址替换为正式地址并在升级中心发布真实版本。
