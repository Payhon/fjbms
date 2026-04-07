# FEAT-0033 UniApp 扫描/扫码登录前置校验 - 功能规格

- status: in_progress
- owner: payhon
- last_updated: 2026-04-03
- related_feature: FEAT-0033
- version: v0.1.0

## 1. 背景与目标
- 背景：
  - 当前 `fjbms-uniapp` 的蓝牙扫描页、摄像头扫码入口以及扫码绑定相关页面，未统一要求用户先登录。
  - 未登录用户仍可进入扫描/扫码链路，容易在后续绑定请求时才失败，体验不一致，也增加无效操作。
- 目标：
  1. 为移动端扫描和扫码功能新增统一的登录前置校验。
  2. 未登录用户进入相关入口或页面时，立即跳转到登录页。
  3. 保持已登录用户的现有扫描、扫码和绑定流程不变。

## 2. 范围
### In Scope
- 扫描/扫码入口登录校验：
  - `fjbms-uniapp/common/composables/useAddDeviceActionSheet.ts`
- 扫描/扫码相关页面登录校验：
  - `fjbms-uniapp/pages/device-provision/ble-scan.vue`
  - `fjbms-uniapp/pages/device-provision/provision-wizard.vue`
  - `fjbms-uniapp/pages/device-provision/uuid-bind.vue`
- 仪表临时会话中的二次扫码绑定登录校验：
  - `fjbms-uniapp/pages/device-battery/detail.vue`
- 抽取可复用的登录校验 helper。
- 功能文档、测试报告、发布说明、看板同步回写。

### Out of Scope
- 不改动登录页功能或登录成功后的回跳逻辑。
- 不新增权限体系或后端鉴权接口。
- 不调整扫码分流规则、蓝牙协议流程和设备绑定业务逻辑。

## 3. 用户价值
- 未登录用户在进入扫描/扫码能力前就会得到明确引导，避免走到半路才失败。
- 扫描、扫码和扫码绑定链路的登录要求统一，后续维护成本更低。

## 4. 验收标准
1. 未登录用户点击“蓝牙搜索”或“摄像头扫码”入口时，会提示先登录并跳转登录页。
2. 未登录用户直接打开 `ble-scan`、`provision-wizard`、`uuid-bind` 页面时，会跳转登录页，不继续执行扫描或绑定逻辑。
3. 未登录用户在仪表临时会话详情页触发“继续扫码绑定 BMS”时，会提示先登录并跳转登录页。
4. 已登录用户的扫描/扫码链路行为保持不变。
5. 本次改动不会引入 TypeScript 编译错误。

## 5. 风险与约束
- 入口拦截与页面守卫必须同时存在，否则仍可能通过深链或历史栈路径绕过校验。
- 页面守卫在跳转登录后，必须阻止本页 `onShow` 继续发起扫描或绑定请求。
- 需尽量复用统一 helper，避免后续多页面 toast 文案和登录跳转行为再次分叉。

## 6. 回滚方案
- 回滚扫描/扫码登录校验 helper 与相关页面调用。
- 回滚 FEAT-0033 文档与看板状态。
