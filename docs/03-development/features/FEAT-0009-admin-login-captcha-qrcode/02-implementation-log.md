# FEAT-0009 管理端登录验证码与二维码配置展示 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-03-07
- related_feature: FEAT-0009
- version: v0.1.0

## 日志
1. 新建 FEAT-0009 文档集（规格/设计/实施/测试/发布）并登记看板。
2. 后端登录验证码能力落地：
   - `backend/internal/service/login_captcha.go`
   - 新增验证码生成（SVG + Redis TTL）与一次性校验消费逻辑。
   - `backend/internal/api/sys_user.go`：登录前增加验证码校验，新增 `GetLoginCaptcha` API。
   - `backend/router/router_init.go`：新增 `GET /api/v1/login/captcha` 路由。
3. 后端主题配置字段扩展：
   - `backend/internal/model/users.http.go`：登录请求增加 `captcha_id/captcha_code`。
   - `backend/internal/model/logo.gen.go`、`backend/internal/model/logo.http.go`、`backend/internal/query/logo.gen.go`：新增 `wxmp_qrcode/app_download_qrcode` 字段映射。
   - `backend/sql/38.sql`：新增 `logo` 表二维码字段迁移脚本。
4. 前端登录验证码与二维码展示实现：
   - `frontend/src/views/_builtin/login/modules/pwd-login.vue`：新增验证码输入、图片展示与刷新、提交携带验证码参数。
   - `frontend/src/service/api/auth.ts`、`frontend/src/store/modules/auth/index.ts`：新增验证码获取接口并扩展登录请求参数。
   - `frontend/src/views/_builtin/login/index.vue`：登录表单下方新增二维码展示区域。
5. 前端系统设置主题 Tab 扩展：
   - `frontend/src/views/management/setting/components/theme-setting.vue`：新增微信小程序二维码、App 下载页二维码上传项。
   - `frontend/src/store/modules/sys-setting/index.ts`、`frontend/src/typings/api.d.ts`：新增字段与 URL 归一化处理。
   - `frontend/src/locales/langs/zh-cn/page.json`、`frontend/src/locales/langs/en-us/page.json`：补充文案。
6. 联调反馈修复（2026-03-07）：
   - `backend/internal/dal/logo.go`、`backend/internal/service/logo.go`：主题设置保存前自动补齐 `logo` 二维码字段（兼容未执行迁移脚本场景）。
   - `backend/router/router_init.go`：新增 `/api/v1/files/*filepath` 文件访问别名路由，兼容仅暴露 `/api/v1` 的网关配置。
   - `frontend/src/utils/common/tool.ts`：`resolveFileUrl` 对 `./files/*` 统一映射到 `/api/v1/files/*`。
   - `frontend/src/views/management/setting/components/upload-image.vue`：预览地址改为 `resolveFileUrl` 生成，修复破图。
   - `frontend/src/views/management/setting/components/theme-setting.vue`：表单 `label-width` 由 `120` 调整为 `180`，避免标签换行。
7. 登录页视觉优化（2026-03-07）：
   - `frontend/src/views/_builtin/login/modules/pwd-login.vue`：当“其他登录方式”都关闭时隐藏 “or” 分割线与下方按钮区。
   - `frontend/src/views/_builtin/login/index.vue`：二维码外层卡片去掉边框线。
   - `frontend/src/views/_builtin/login/index.vue`：默认背景动效替换为“电路板电流流动粒子效果”。
8. 登录页卡在加载态修复（2026-03-07）：
   - 根因：`setupLoading()` 在运行期被再次调用时会重写 `#app`，导致登录页被 loading DOM 覆盖且无报错。
   - `frontend/src/plugins/loading.ts`：新增 `lockLoadingScreen()` 与 `loadingLocked`，并基于 `data-app-mounted` 防止挂载后再次写入 loading。
   - `frontend/src/main.ts`：启动时仅调用一次 `setupLoading()`，移除 `system_name` 监听中的再次调用；挂载前 `lockLoadingScreen()`，挂载后写入 `data-app-mounted` 标记。
