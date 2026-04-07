# FEAT-0033 UniApp 扫描/扫码登录前置校验 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-04-03
- related_feature: FEAT-0033
- version: v0.1.0

## 1. 方案概览
- 新增统一登录校验 helper：
  - 复用现有 `isLoginType()` 判断当前登录态。
  - 在未登录时统一 toast `pages.pleaseLogin`，并导航到 `/pages/login/login`。
- 入口层拦截：
  - 在 `useAddDeviceActionSheet.ts` 弹出操作表前先做登录校验，未登录则不再进入扫描/扫码选择。
- 页面层守卫：
  - `ble-scan.vue`、`provision-wizard.vue`、`uuid-bind.vue` 在 `onLoad` 阶段先校验登录态。
  - 若未登录则立即跳转登录页，并设置页面级阻断标记，防止 `onShow` 继续执行扫描/绑定逻辑。
- 特殊链路补漏：
  - 仪表临时会话详情页 `scanAndBindBms()` 在实际调用 `uni.scanCode()` 前增加登录校验。

## 2. 接口与数据结构
- 本次不新增后端接口。
- 新增前端 helper：
  - `isUserLoggedIn(): boolean`
  - `ensureLoggedIn(options): boolean`

## 3. 关键流程
1. 用户触发“添加设备”操作时，先执行统一登录校验。
2. 未登录时：
   - toast 提示“请先登录”；
   - 导航到登录页；
   - 当前扫描/扫码动作终止。
3. 用户若直接访问扫描/扫码绑定页面，页面在 `onLoad` 阶段执行同样的校验。
4. 页面被登录守卫拦截后，不再在 `onShow` 中继续启动蓝牙扫描或绑定流程。

## 4. 安全与权限
- 本次仅做前端交互层登录前置校验，不替代后端鉴权。
- 所有绑定请求仍由现有后端接口鉴权兜底。

## 5. 测试策略
- `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
- 手动验证未登录场景：
  - 点击蓝牙搜索；
  - 点击摄像头扫码；
  - 直接访问扫描页和绑定页；
  - 仪表会话二次扫码绑定。
- 手动验证已登录场景：
  - 原有扫描、扫码和绑定流程不受影响。

## 6. 兼容性与迁移
- 不涉及数据库、接口协议或已有业务数据迁移。
- 继续沿用当前登录页 `/pages/login/login` 作为统一登录入口。
