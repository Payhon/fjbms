# FEAT-0021 UniApp 电池仪表盘组件总电压与曲线进度条优化 - 发布说明

- status: review
- owner: payhon
- last_updated: 2026-03-22
- related_feature: FEAT-0021
- version: v0.1.0

## 发布内容
- UniApp 设备详情页顶部仪表盘新增总电压显示。
- 左右 SOC/SOH 进度条已调整为与外层壳体弧度一致的椭圆曲线样式。
- 保持原有进度条渐变色与线宽，不影响现有数值展示和底部状态信息。

## 影响范围
- `fjbms-uniapp/components/dashboard-gauge/dashboard-gauge.vue`
- `fjbms-uniapp/pages/device-battery/components/dashboard-tab.vue`
- `fjbms-uniapp/lang/zh-CN.ts`
- `fjbms-uniapp/lang/en-US.ts`

## 发布与回滚提示
- 发布前建议执行 `pnpm exec tsc --noEmit` 并做一次真机或 HBuilderX 视觉验收。
- 如需回滚，恢复仪表盘组件原折线路径和顶部无总电压的旧结构即可。
