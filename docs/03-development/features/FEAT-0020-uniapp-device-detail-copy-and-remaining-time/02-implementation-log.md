# FEAT-0020 UniApp 设备详情页单体文案与充放电剩余时间调整 - 实施日志

- status: review
- owner: payhon
- last_updated: 2026-03-22
- related_feature: FEAT-0020
- version: v0.1.0

## 日志
1. 2026-03-22 需求确认
   - 已确认修改范围仅针对 `fjbms-uniapp` 设备详情页，包含参数设置单体文案和仪表盘剩余时间展示。
2. 2026-03-22 现状核对
   - 已确认 `params-tab.vue` 负责参数设置分组展示。
   - 已确认 `dashboard-tab.vue` 仍存在顶部“剩余时间”区域和固定“充电时间”卡片。
   - 已确认状态解析已包含 `0x111/0x112` 到 `timing.dischargeRemainingMin/chargeRemainingMin`，无需新增协议读取链路。
3. 2026-03-22 代码调整
   - `fjbms-uniapp/pages/device-battery/components/params-tab.vue` 已对单体分组展示文案统一补齐“单体”前缀。
   - `fjbms-uniapp/pages/device-battery/components/dashboard-tab.vue` 已移除顶部剩余时间区域，并将时间卡片改为动态“充电剩余时间/放电剩余时间/充放电剩余时间”。
   - `fjbms-uniapp/lang/zh-CN.ts`、`fjbms-uniapp/lang/en-US.ts` 已补充仪表盘动态标题文案。
4. 2026-03-22 文档回写
   - 已新增 FEAT-0020 文档并同步项目看板。
