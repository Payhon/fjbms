# FEAT-0026 UniApp 账号注销 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-03-26
- related_feature: FEAT-0026
- version: v0.1.0

## 1. 实施记录
1. 新建 FEAT-0026 功能文档目录，并在项目看板登记 Backend / UniApp 条目。
2. 为 APP 已登录认证路由新增 `delete_account` 接口，请求体携带当前密码。
3. 在 `AppAuth` 服务中实现终端用户自助注销：校验用户类型、校验密码、事务删除用户及移动端相关数据。
4. 在 `fjbms-uniapp/pages/my/setting/index.vue` 新增“账号注销”入口、风险确认弹窗和密码输入弹窗。
5. 在 `fjbms-uniapp/service/app-auth.ts` 新增账号注销请求封装，并补充中英文文案。

## 2. 当前状态
- 代码已完成。
- 后端已完成定向 Go 测试。
- UniApp 待真机/小程序联调确认交互链路。
