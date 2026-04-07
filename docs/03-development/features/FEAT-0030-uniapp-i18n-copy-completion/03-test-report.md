# FEAT-0030 UniApp 页面多语言文案补全 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-04-02
- related_feature: FEAT-0030
- version: v0.1.0

## 1. 测试范围
- 首页及首页相关组件多语言切换。
- 设备详情页及子组件多语言切换。
- “我的”、告警、通知详情、机构设备页与通用提示文案多语言切换。

## 2. 已执行
1. 静态校验
   - 命令：`cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
   - 结果：通过。
2. 页面与模块抽查
   - 首页范围：复核 `pages/home/home.vue`、`components/home/device-card.vue`、`components/customNav/customNav.vue`，确认当前用户可见文案已基本通过 `$t/t` 输出，本轮无新增代码修改。
   - 设备详情范围：确认 `pages/device-battery/components/params-tab.vue` 中温度标签、电池类型、更新提示、无权限提示已切换为统一 i18n key；`dashboard-tab.vue` 的剩余时间单位已走 `deviceDetail.unit.minutes`。
   - 通用模块范围：确认 `common/request.ts`、`common/util.ts` 中 token 失效、请求失败、上传失败、网络断开、升级提示等运行时文案已切换为字典读取。
   - 设备添加流程：确认 `pages/device-provision/ble-scan.vue`、`pages/device-provision/provision-wizard.vue`、`pages/device-provision/uuid-bind.vue` 与 `common/composables/useAddDeviceActionSheet.ts` 的可见文案均已收口到 `pages.deviceProvision.*`，并补齐蓝牙适配器不可用提示。

## 3. 风险备注
- 仓库当前缺少覆盖 UniApp UI 的自动化测试，本次仍以静态校验与人工抽样为主。
- 设备详情与“我的”等页面仍建议在中文/英文语言下各做一次真机或小程序抽样，重点关注 toast、升级弹窗与参数页电池类型选择器。
- 设备添加流程建议再重点抽测扫码模式和蓝牙扫描失败兜底，确认错误文案没有 key 原样透出。
