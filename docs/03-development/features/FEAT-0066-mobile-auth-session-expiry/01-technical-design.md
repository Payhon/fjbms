# FEAT-0066 技术设计

- status: review
- owner: payhon
- last_updated: 2026-07-09
- related_feature: FEAT-0066
- version: v0.1.0

## 1. 方案概览
新增移动端统一认证失效模块 `common/auth/session-expired.ts`，由全局 API 响应拦截器调用。模块负责识别公开接口、去重同一轮登录过期提示、清理认证态、重置内存用户态，并统一跳转登录页。

## 2. 接口与数据结构
- 新增 `handleSessionExpired()`：处理认证失效提示、认证缓存清理与登录页跳转。
- 新增 `shouldHandleSessionExpiredResponse(response)`：按 HTTP `401/402/403` 和公开接口白名单判断是否需要处理。
- 新增 `isAuthExpiredApiResponse(payload)`：供页面/Store 在收到认证错误体后停止后续请求。

## 3. 关键流程
- 请求层收到 `401/402/403` 后，先检查 URL 与 method 是否属于公开接口；公开接口直接返回响应数据，不弹登录过期。
- 受保护接口认证失效时，模块记录本轮失效 token，后续同 token 或已清空 token 的并发 401 直接忽略。
- 立即移除认证相关 storage，重置用户和 token Pinia store，并通过 `reLaunch`/`redirectTo` 收敛登录页跳转。
- 首页 `user/detail` 若已返回认证失效，立即清空首页列表状态，不再继续请求 `app/device/list`。

## 4. 安全与权限
不改变后端鉴权逻辑，不扩展公开接口。白名单仅用于前端避免误弹登录过期，不绕过服务端权限。

## 5. 测试策略
以 TypeScript 静态校验和关键文件语法校验为主，结合手工场景验证：空 token、无效 token、正常登录、公开接口异常返回。

## 6. 兼容性与迁移
兼容历史 `accessToken`、`refreshToken` storage key 清理；保留语言、服务地址、蓝牙自动连接等非认证偏好。
