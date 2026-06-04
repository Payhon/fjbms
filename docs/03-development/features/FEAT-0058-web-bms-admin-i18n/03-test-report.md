# FEAT-0058 测试报告

## 自动化检查

### `cd frontend && pnpm typecheck`

- 结果：通过
- 时间：2026-06-04

## 静态检查

### 路由翻译覆盖

- 检查项：`zh-cn/route.json` 与 `en-us/route.json` 中 `route.bms*` / `perm.bms*` 差异。
- 期望：缺失数 0。

### 参数翻译覆盖

- 检查项：提取 `frontend/src/common/lib/bms-protocol/param-registry.ts` 中 147 个 `def(BMS_PARAM.*)` key，对比 `zh-cn/en-us bms.param`。
- 期望：中英文缺失数 0。

### 设备详情 BMS 组件中文扫描

- 检查项：
  - `frontend/src/views/bms/dashboard/index.vue`
  - `frontend/src/views/device/details/index.vue`
  - `frontend/src/views/device/details/modules/bms-panel/index.vue`
  - `frontend/src/views/device/details/modules/battery-basic-info.vue`
  - `frontend/src/views/device/details/modules/battery-operation-log.vue`
- 期望：仅注释允许中文；用户可见文案均迁移到 locale。

### BMS 全目录中文扫描

- 检查项：`frontend/src/views/bms/**`
- 结果：除 Dashboard 外，其余管理页仍有既有中文硬编码，后续继续按页面迁移。

## 手动回归建议

- 英文环境查看左侧 BMS 菜单，不出现 `route.bms_*`。
- 英文环境进入 BMS 电池详情，外层 Tab、BMS 面板内 Tab、参数设置表格、Basic Info、Operation Logs 无中文残留。
- 英文环境打开 Advanced Settings，Advanced Config / Numbering Config / System Config / Factory Config 无中文残留。
- 中文环境抽查同路径，确认中文展示仍正常。
