# FEAT-0031 App 上架准备与公共页面完善 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-04-15 09:40
- related_feature: FEAT-0031
- version: v0.1.0

## 1. 测试范围
- 公开隐私政策页、用户政策页和下载页的可访问性与内容正确性。
- App 管理表单与升级中心表单的数据保存与回显。
- UniApp 登录 / 注册 / 关于页协议入口跳转与升级检测链路。
- App Store 审核相关的 iOS 权限文案完整性、扫码入口稳定性与送审前 `ipa` 自检脚本。
- App 名称国际化配置与不同系统语言下的显示名称正确性。

## 2. 测试环境
- 本地开发环境。
- 生产联调环境：`https://cloud.fjiaenergy.com`。
- 目标平台：Android、iOS、桌面浏览器。

## 3. 用例结果
- 已执行：
  - `cd backend && go test ./internal/api ./internal/service ./internal/model ./router ./router/apps`
    - 结果：通过。
  - `cd backend && go test ./internal/api ./internal/service`
    - 结果：通过。
  - `cd frontend && pnpm typecheck`
    - 结果：通过。
  - `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
    - 结果：通过。
  - `cd fjbms-uniapp && bash scripts/check_ios_ipa.sh ../release/1.0.2/fjbms_1.0.5.ipa`
    - 结果：失败，脚本已正确识别旧包缺少 `Assets.car` / 图标元数据，可用于送审前拦截无效构建。
  - 扫码入口静态代码校验：
    - `common/composables/useAddDeviceActionSheet.ts` 已补 `onlyFromCamera: true`。
    - `pages/device-battery/detail.vue` 已保持 `onlyFromCamera: true`。
    - 结果：主扫码入口与仪表扫码绑定入口现已统一为仅摄像头。
  - iOS 权限文案静态配置校验：
    - `manifest.json` 已显式设置中文 `privacyDescription`，并新增 `app-plus.locales.en.ios.privacyDescription`。
    - 结果：相机、蓝牙及相册权限文案已替换为用途明确、包含示例的描述；其中相机文案已同步覆盖“扫码绑定设备 + 拍摄头像照片”两个场景，待下一版 `ipa` 解包验证最终写入结果。
  - App 名称国际化静态配置校验：
    - `manifest.json` 的 `name` 已改为 `%app.name%`。
    - `locale/en.json`、`locale/zh-Hans.json`、`locale/zh-Hant.json` 已补齐 `app.name`。
    - 结果：源码层已满足“简体中文 / 繁体中文显示 `富嘉BMS`，其他已覆盖语言显示 `FUJIA BMS`”的打包配置要求，待新 `ipa` 在不同系统语言下验证最终显示结果。
  - UniApp 登录页环境显隐校验：
    - 微信小程序：保留“其他登录方式”标题与微信登录按钮。
    - 非微信小程序：不显示“其他登录方式”标题与底部空白区域。
    - 结果：规则已在模板层按环境条件收敛，待真机 / 小程序运行态验收。
  - 升级检测日志校验：
    - `call-check-version.ts` 已在请求前打印 payload，请求后打印 response，异常时打印 error。
    - 结果：静态代码检查通过，待 APP 运行态查看控制台输出。
  - `cd frontend && pnpm build`
    - 结果：通过；生产构建产物已用于后续发布。
  - `make update-frontend-prod`
    - 结果：成功，生产前端目录 `/www/fjia/fjbms/frontend` 已替换。
  - `make update-backend-prod`
    - 结果：成功，`fjbms-backend.service` 重启后保持 `active (running)`。
  - 线上 URL 验证：
    - `https://cloud.fjiaenergy.com/public/app/privacy`
    - `https://cloud.fjiaenergy.com/public/app/user-policy`
    - `https://cloud.fjiaenergy.com/public/app/download?appid=__UNI__40EADE1`
    - 结果：均返回 `HTTP 200`。
  - 线上公开接口验证：
    - `GET /api/v1/app/content/pages/privacy_policy?lang=zh-CN`
    - `GET /api/v1/app/content/pages/privacy_policy?lang=en-US`
    - `GET /api/v1/app/content/pages/user_policy?lang=en-US`
    - `GET /api/v1/app/public/info?appid=__UNI__40EADE1`
    - 结果：均返回 `code=200`；英文参数在缺少英文配置时已回退 `zh-CN`。
  - 生产数据补录验证：
    - `_ui/appstore/export/iphone-65/*.png` 已通过后端上传接口上传，`app_public_info.screenshot` 已返回 5 张生产图片地址。
    - `GET /api/v1/app/public/info?appid=__UNI__40EADE1`
    - 结果：`description`、`introduction`、`app_android`、`app_ios`、`app_harmony`、`h5` 均已返回，下载页已有完整内容源数据。
  - 英文协议发布验证：
    - `GET /api/v1/app/content/pages/privacy_policy?appid=__UNI__40EADE1&lang=en-US`
    - `GET /api/v1/app/content/pages/user_policy?appid=__UNI__40EADE1&lang=en-US`
    - 结果：标题分别返回 `Privacy Policy`、`User Agreement`，语言为 `en-US`。
  - 生产升级接口链路验证：
    - `POST /api/v1/app/upgrade/check`，请求 `appid=__UNI__40EADE1`、`appVersion=1.0.0`、`X-TenantID=d616bcbb`
    - 结果：返回 `code=0`、`message=no update`，说明生产升级接口已可达且请求格式正确，但当前无可用升级版本。
- 待执行：
  - 重新打包新 `ipa`，并使用 `bash fjbms-uniapp/scripts/check_ios_ipa.sh <ipa-path>` 校验相机/蓝牙权限文案、追踪声明与图标资源。
  - 在简体中文、繁体中文、英文系统语言下安装新包，验证桌面 App 名称分别显示为 `富嘉BMS`、`富嘉BMS`、`FUJIA BMS`。
  - iPhone / iPad 真机验证主扫码入口不再出现“相册”分支，且扫码取消 / 成功 / 失败路径无 H5+ 异常。
  - 下载页 UA 分流与平台按钮展示的浏览器实机检查。
  - 升级中心下载地址输入与文件选择器联动的后台人工验收。
  - UniApp 协议 H5 跳转参数透传真机检查。
  - UniApp 真机升级检测与 iOS / Android 下载跳转。
  - UniApp 登录页“其他登录方式”区域在微信小程序与非微信环境下的运行态显示确认。
  - UniApp 升级检测接口控制台日志在 APP 运行态的实际输出确认。

## 4. 缺陷与风险
- `go test ./...` 未全绿，失败来自仓库既有环境依赖测试：
  - `project/initialize/test.TestSetDevice`
  - `project/test.TestDatebase`
  - 与 FEAT-0031 改动无直接关联。
- 若 `appid` 与后台应用记录不一致，公开页和下载页将无法正确命中内容。
- 生产应用 `appid=__UNI__40EADE1` 当前下载地址为占位值。
  - 下载页展示与跳转逻辑已可验证，但仍需业务侧在后台替换为正式 APK / App Store / Harmony 链接。
- iOS 权限文案最终是否写入 `Info.plist` 依赖 HBuilderX / DCloud 打包链。
  - 已在源码层补齐配置，但仍需以新 `.ipa` 解包结果为准，不能只依赖 `manifest.json` 文本。
- App 名称国际化同样依赖 HBuilderX / DCloud 云打包链。
  - 源码已按官方 `%app.name%` 方案配置，但仍需通过新 `ipa` 在不同系统语言下安装验证。
- 生产环境当前未发布 `stable_publish=true` 的真实升级记录。
  - 自动升级接口已联通，但在后台升级中心发布真实版本前，APP 侧只会得到 `no update`。
- 若 UniApp 运行时租户头未正确回退，公共内容页可能读取到错误租户的数据。

## 5. 结论
- 本地静态检查、生产发布、公开页数据补录和英文协议发布均已完成，本次已补充送审所需的 iOS 权限文案与扫码入口策略修正。
- 当前主要剩余风险来自新 `ipa` 仍需重新打包验证权限文案 / 图标资源 / App 名称国际化，以及下载地址仍为占位值、升级中心尚未发布真实升级版本。
