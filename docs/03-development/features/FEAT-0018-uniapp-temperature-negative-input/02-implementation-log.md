# FEAT-0018 UniApp 温度参数支持负数输入 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-03-20
- related_feature: FEAT-0018
- version: v0.1.0

## 日志
1. 2026-03-20 问题确认
   - 已确认 UniApp 参数编辑弹窗中，非字符串参数统一使用 `digit` 输入类型，温度参数无法输入负号。
2. 2026-03-20 代码调整
   - `fjbms-uniapp/pages/device-battery/components/params-tab.vue` 已新增 `inputType` 状态。
   - 已在打开弹窗时根据参数单位/键名判断温度项，并将温度项输入框切为 `text`。
3. 2026-03-20 文档回写
   - 已新增 FEAT-0018 文档并同步项目看板。
