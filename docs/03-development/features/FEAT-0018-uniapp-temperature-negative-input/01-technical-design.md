# FEAT-0018 UniApp 温度参数支持负数输入 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-03-20
- related_feature: FEAT-0018
- version: v0.1.0

## 1. 方案
- 在参数编辑弹窗状态中新增 `inputType`。
- 打开编辑弹窗时，根据参数 `unit` 和 `key` 判断是否为温度类参数：
  - 单位为 `℃` / `°C`
  - 或参数键名以 `_C` 结尾
- 命中后将输入框 `type` 从 `digit` 切为 `text`，以允许输入负号。

## 2. 校验策略
- 不新增额外提交协议。
- 继续复用 `confirmEdit()` 中的 `Number(raw)` 校验，确保非数值不会被写入。

## 3. 验证策略
- 执行 `cd fjbms-uniapp && pnpm exec tsc --noEmit`。
- 手工验证温度参数与非温度参数的键盘行为差异。
