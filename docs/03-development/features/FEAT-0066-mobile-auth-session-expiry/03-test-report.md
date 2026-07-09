# FEAT-0066 测试报告

- status: review
- owner: payhon
- last_updated: 2026-07-09
- related_feature: FEAT-0066
- version: v0.1.0

## 1. 测试范围
覆盖 UniApp 认证失效处理模块、全局 API 拦截器、首页启动加载链路和绑定设备缓存刷新链路。

## 2. 测试环境
- 本地代码静态校验
- 工作目录：`/Users/payhon/work2025/project/fjbms/fjbms-uniapp`

## 3. 用例结果
- 通过：`pnpm exec tsc --noEmit --pretty false`
- 通过：`git -C /Users/payhon/work2025/project/fjbms/fjbms-uniapp diff --check`
- 通过：`git -C /Users/payhon/work2025/project/fjbms diff --check -- docs/04-project-tracking/board.md docs/03-development/features/FEAT-0066-mobile-auth-session-expiry`
- 待回归：真机或微信开发者工具验证空 token、无效 token、正常登录场景。

## 4. 缺陷与风险
暂未执行真机或微信开发者工具回归。无效 token 冷启动需在目标运行环境观察弹窗次数和页面栈。

## 5. 结论
静态校验通过，代码可进入运行态回归。仍需在 APP 或微信开发者工具中确认无效 token 冷启动只弹一次登录过期提示。
