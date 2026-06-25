# FEAT-0026 UniApp 账号注销 - 实施日志

- status: review
- owner: payhon
- last_updated: 2026-06-24
- related_feature: FEAT-0026
- version: v0.1.0

## 1. 实施记录
1. 新建 FEAT-0026 功能文档目录，并在项目看板登记 Backend / UniApp 条目。
2. 为 APP 已登录认证路由新增 `delete_account` 接口，请求体携带当前密码。
3. 在 `AppAuth` 服务中实现终端用户自助注销：校验用户类型、校验密码、事务删除用户及移动端相关数据。
4. 在 `fjbms-uniapp/pages/my/setting/index.vue` 新增“账号注销”入口、风险确认弹窗和密码输入弹窗。
5. 在 `fjbms-uniapp/service/app-auth.ts` 新增账号注销请求封装，并补充中英文文案。
6. 2026-06-24：扩展注销接口请求体，新增可选 `appid` 并将 `password` 改为可选；后端仅在启用中的 PACK 小程序配置和当前用户 `${appid}:openid` 微信身份同时命中时跳过密码校验。
7. 2026-06-24：UniApp 设置页在注销前刷新运行配置；PACK 微信小程序确认不可恢复提示后直接注销，非 PACK 场景继续要求输入当前密码。

## 2. 当前状态
- 代码已完成。
- 后端已完成 PACK 免密注销定向 Go 测试。
- UniApp TypeScript 校验通过，待真机/小程序联调确认交互链路。
