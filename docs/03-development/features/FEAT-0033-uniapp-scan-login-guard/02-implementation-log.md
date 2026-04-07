# FEAT-0033 UniApp 扫描/扫码登录前置校验 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-04-03 01:58
- related_feature: FEAT-0033
- version: v0.1.0

## 1. 实施记录
1. 新建 FEAT-0033 功能文档目录，补齐规格、设计、实施、测试、发布五件套。
2. 梳理扫描/扫码链路，确认主要入口与页面落点包括：
   - `useAddDeviceActionSheet.ts`
   - `pages/device-provision/ble-scan.vue`
   - `pages/device-provision/provision-wizard.vue`
   - `pages/device-provision/uuid-bind.vue`
   - `pages/device-battery/detail.vue` 仪表临时会话二次扫码
3. 确认项目已有 `isLoginType()` 可直接复用为登录态判断来源。
4. 已新增统一 helper `common/auth/ensure-login.ts`：
   - 统一封装登录态判断、未登录 toast 和跳转登录页逻辑。
   - 支持 `navigateTo` / `redirectTo` / `reLaunch` 三种跳转方式。
5. 已完成入口层拦截：
   - `useAddDeviceActionSheet.ts` 在展示“蓝牙搜索 / 摄像头扫码”操作表前先校验登录态。
   - 未登录时先回到基础 tab，再跳登录页，避免占位页留在返回栈中。
6. 已完成页面层守卫：
   - `ble-scan.vue`、`provision-wizard.vue`、`uuid-bind.vue` 在 `onLoad` 中拦截未登录访问。
   - 被拦截页面通过本地标记阻断 `onShow` 继续发起扫描或绑定逻辑。
7. 已补充仪表临时会话二次扫码登录校验：
   - `pages/device-battery/detail.vue` 在调用 `uni.scanCode()` 前先校验登录态。

## 2. 待执行项
- APP / 小程序运行态验收。
- 根据验收结果决定是否进入 `review`。

## 3. 当前状态
- 文档已进入 `in_progress`。
- 代码实现与 TypeScript 静态校验已完成，当前待运行态验收。
