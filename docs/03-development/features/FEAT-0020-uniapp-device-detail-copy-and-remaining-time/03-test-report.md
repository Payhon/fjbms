# FEAT-0020 UniApp 设备详情页单体文案与充放电剩余时间调整 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-03-22
- related_feature: FEAT-0020
- version: v0.1.0

## 1. 已执行验证
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit`
- [ ] 手工验收：
  - [ ] 单体设置分组文案已统一带“单体”前缀
  - [ ] 顶部“剩余时间”区域已移除
  - [ ] 充电中显示“充电剩余时间”与正值分钟
  - [ ] 放电中显示“放电剩余时间”与负值分钟
  - [ ] 空闲时显示“充放电剩余时间”与 `-`

## 2. 当前结论
- `cd fjbms-uniapp && pnpm exec tsc --noEmit`
  - 结果：通过。
- 真机或 HBuilderX 手工验收待补充。
