# FEAT-0020 UniApp 设备详情页单体文案与充放电剩余时间调整 - 发布说明

- status: review
- owner: payhon
- last_updated: 2026-03-22
- related_feature: FEAT-0020
- version: v0.1.0

## 发布内容
- UniApp 设备详情页参数设置中，单体设置分组文案已统一补齐“单体”前缀，避免与总压参数混淆。
- 仪表盘已移除顶部独立“剩余时间”区域。
- 仪表盘时间卡片改为按状态动态显示“充电剩余时间”“放电剩余时间”或默认“充放电剩余时间”。

## 影响范围
- `fjbms-uniapp/pages/device-battery/components/params-tab.vue`
- `fjbms-uniapp/pages/device-battery/components/dashboard-tab.vue`
- `fjbms-uniapp/lang/zh-CN.ts`
- `fjbms-uniapp/lang/en-US.ts`

## 发布与回滚提示
- 发布前建议执行 `pnpm exec tsc --noEmit` 并完成一次真机或 HBuilderX 设备详情页回归。
- 如需回滚，恢复仪表盘旧的顶部剩余时间区域与固定“充电时间”卡片，并移除单体分组展示层前缀补齐逻辑即可。
