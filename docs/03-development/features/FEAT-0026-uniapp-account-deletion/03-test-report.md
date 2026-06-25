# FEAT-0026 UniApp 账号注销 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-06-24
- related_feature: FEAT-0026
- version: v0.1.0

## 1. 测试范围
- 后端账号注销接口的权限、密码校验和删除流程。
- PACK 微信小程序免密码注销的后端可信判定。
- UniApp 设置页注销入口、确认提示、PACK 免密路径、非 PACK 密码输入和成功退出登录。

## 2. 测试环境
- 本地开发环境
- 日期：2026-06-24

## 3. 用例结果
- `backend`
  - 命令：`cd backend && go test ./internal/service -run 'TestAppAuthDeleteAccount|TestWxmpIdentityIdentifier|TestGetPackWxMpConfigMissingReturnsEmptyConfig'`
  - 结果：通过
  - 备注：出现 `github.com/shirou/gopsutil/disk` 的 macOS 弃用告警，不影响本次功能
- `fjbms-uniapp`
  - 命令：`cd fjbms-uniapp && pnpm exec tsc -p tsconfig.json --noEmit`
  - 结果：通过
  - 静态自检：已完成受影响页面与服务封装检查
  - 真机/小程序联调：待执行

## 4. 缺陷与风险
- 若线上存在未纳入本次清理范围的用户关联表，可能残留历史痕迹数据，需要后续补充。
- 当前删除成功后主要依赖客户端清空本地 token；若旧 token 被长期缓存，需等待其自然过期。
- PACK 免密路径依赖微信小程序 AppID 与 `WXMP_OPENID` scoped 身份一致；历史未 scoped 的微信身份不会触发免密。

## 5. 结论
- 后端定向测试与 UniApp TypeScript 校验通过，代码可进入联调验收。
- UniApp 仍需补一次真机或小程序路径回归，重点验证 PACK “风险确认 -> 直接注销”和非 PACK “风险确认 -> 输入密码 -> 注销成功跳转登录页”链路。
