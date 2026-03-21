# FEAT-0018 UniApp 温度参数支持负数输入 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-03-20
- related_feature: FEAT-0018
- version: v0.1.0

## 发布内容
- UniApp 电池详情页参数设置中，温度类参数编辑弹窗现在支持输入负数。
- 其它数值型参数继续保持原有数字键盘行为。

## 影响范围
- `fjbms-uniapp/pages/device-battery/components/params-tab.vue`

## 发布与回滚提示
- 发布前建议执行 `pnpm exec tsc --noEmit` 并做一次真机或 HBuilderX 手工验证。
- 如需回滚，恢复温度参数与普通数值参数共用 `digit` 键盘的旧逻辑即可。
