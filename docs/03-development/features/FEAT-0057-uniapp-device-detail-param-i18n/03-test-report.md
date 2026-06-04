# FEAT-0057 UniApp 设备详情参数多语言补齐 - 测试报告

- status: done
- owner: payhon
- last_updated: 2026-06-04
- related_feature: FEAT-0057
- version: v0.1.0

## 1. 测试范围
- 设备详情参数设置页基础分组：Single Cell、Voltage、Current、Temperature。
- Advanced 弹窗：Advanced Config、Numbering Config、System Config。
- System Config 功能开关名称和状态文案。
- `bmsParam` 中英文 key 覆盖情况。

## 2. 已执行
1. 当前页面参数 key 覆盖检查
   - 命令：提取 `params-tab.vue` 的 `SINGLE_KEYS`、`VOLTAGE_KEYS`、`CURRENT_KEYS`、`TEMP_KEYS`，检查 `zh-CN.ts` / `en-US.ts` 是否存在对应 `bmsParam`。
   - 结果：通过，91 个可见参数 key 缺失数为 0。
2. 协议注册表参数 key 覆盖检查
   - 命令：提取 `param-registry.ts` 中 `def(BMS_PARAM.<KEY>...)`，检查 `zh-CN.ts` / `en-US.ts` 是否存在对应 `bmsParam`。
   - 结果：通过，157 个参数定义缺失数为 0。
3. TypeScript 校验
   - 命令：`cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
   - 结果：通过。
4. 空白检查
   - 命令：`git diff --check`
   - 结果：通过。
5. 子仓空白检查
   - 命令：`git -C fjbms-uniapp diff --check`
   - 结果：通过。

## 3. 人工回归建议
- 英文环境进入设备详情 Settings 页，展开 Single Cell / Voltage / Current / Temperature，确认参数名无中文残留。
- 打开 Advanced 弹窗，确认 Advanced Config / Numbering Config / System Config 内参数名无中文残留。
- 切换 System Config 功能开关，确认状态显示为 `On/Off` 或 `Allowed/Forbidden`。
- 切回中文环境，确认参数名和功能开关仍显示中文。
