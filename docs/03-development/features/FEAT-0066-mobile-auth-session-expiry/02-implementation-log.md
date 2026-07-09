# FEAT-0066 实现记录

- status: review
- owner: payhon
- last_updated: 2026-07-09
- related_feature: FEAT-0066
- version: v0.1.0

## 1. 变更摘要
- 新增统一认证失效处理模块，支持公开接口白名单、弹窗去重、认证缓存清理和登录页跳转收敛。
- 全局 `apiRequest` 响应拦截器改为调用统一认证失效处理，不再每个 401 独立弹窗。
- 移除 app 创建阶段绑定设备缓存抢跑请求，避免过期 token 冷启动立即多打一条受保护接口。
- 首页 `ensureUserInfo()` 返回认证状态，认证失效时停止后续设备列表请求。
- 绑定设备缓存刷新遇到认证失效时只清空本地快照并退出。

## 2. 关键文件
- `fjbms-uniapp/common/auth/session-expired.ts`
- `fjbms-uniapp/API/index.js`
- `fjbms-uniapp/main.ts`
- `fjbms-uniapp/pages/home/home.vue`
- `fjbms-uniapp/store/bound-devices.ts`

## 3. 实现备注
本次没有接入 token 自动续期。当前后端刷新接口仍依赖有效 JWT claims，过期 token 的正确处理是清理认证态并重新登录。
