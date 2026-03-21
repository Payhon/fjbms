# FEAT-0018 UniApp 温度参数支持负数输入 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-03-20
- related_feature: FEAT-0018
- version: v0.1.0

## 1. 已执行验证
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit`
- [ ] 手工验收：
  - [ ] 温度参数弹窗可输入 `-`
  - [ ] 非温度参数仍使用数字键盘
  - [ ] 非法文本不会提交

## 2. 当前结论
- `cd fjbms-uniapp && pnpm exec tsc --noEmit`
  - 结果：通过。
- 真机或 HBuilderX 手工验收待补充。
