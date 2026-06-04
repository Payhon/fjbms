# FEAT-0057 UniApp 设备详情参数多语言补齐 - 功能规格

- status: done
- owner: payhon
- last_updated: 2026-06-04
- related_feature: FEAT-0057
- version: v0.1.0

## 1. 背景与目标
- 背景：
  - 英文语言环境下，`fjbms-uniapp` 设备详情「Settings」页仍有部分参数名称显示中文。
  - 设备详情参数页会优先读取 `bmsParam.<PARAM_KEY>`，缺失时回退到协议注册表的中文 `label`；System Config 功能开关也直接使用中文常量。
- 目标：
  1. 补齐设备详情参数页所有当前可见参数的中英文翻译。
  2. 同步覆盖协议注册表内后续可能开放展示的参数 key，避免继续回退中文。
  3. 将 System Config 功能开关名称和状态文案接入 i18n。

## 2. 范围
### In Scope
- `fjbms-uniapp/pages/device-battery/components/params-tab.vue` 参数设置页。
- `fjbms-uniapp/lang/zh-CN.ts` 与 `fjbms-uniapp/lang/en-US.ts` 的 `bmsParam.*` 和 `deviceDetail.params.functionConfig.*`。
- 设备详情基础分组、Advanced 弹窗、System Config、编辑弹窗标题的参数名称展示。

### Out of Scope
- 不修改 BMS 协议寄存器、读写逻辑、权限 key 或接口返回。
- 不修改后台设备参数权限树展示。
- 不处理非设备详情参数设置页的其他历史中文文案。

## 3. 验收标准
1. 英文环境下 Settings 页基础分组参数名不再出现中文。
2. Advanced 弹窗内 Advanced Config、Numbering Config、System Config 不再出现中文参数名。
3. System Config 功能开关名称和 On/Off、Allowed/Forbidden 状态均显示英文。
4. 中文环境仍显示中文参数名和状态文案。
5. `bmsParam` 覆盖协议注册表内定义的参数 key，缺失检查为 0。

## 4. 风险与约束
- 协议注册表的中文 `label` 继续保留作为协议说明和兜底，不引入 i18n 依赖。
- 英文翻译沿用既有缩写风格，如 `OV`、`UV`、`OC`、`Pack`、`Cell`。
- 仓库暂无 UniApp UI 自动化测试，本功能以类型检查、静态 key 覆盖检查和真机/小程序人工抽样为主要验证方式。

## 5. 回滚方案
- 回滚 `params-tab.vue` 的功能开关 i18n 渲染改动。
- 回滚 `zh-CN.ts` / `en-US.ts` 中本次新增的参数和功能开关翻译。
- 回滚本功能文档和看板状态。
