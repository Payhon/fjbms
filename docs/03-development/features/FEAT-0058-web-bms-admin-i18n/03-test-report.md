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
- 命令：`rg -n "[\p{Han}]" frontend/src/views/bms --glob '*.{vue,ts}'`
- 结果：通过。命中项仅剩注释、接口/枚举说明或开发说明，未发现用户可见固定中文文案。

### BMS 词包一致性

- 检查项：对比 `frontend/src/locales/langs/zh-cn/bms.json` 与 `frontend/src/locales/langs/en-us/bms.json` 展平后的 key 集合，并扫描英文词包中文字符和自动占位值。
- 结果：
  - `missingEn`: 0
  - `missingZh`: 0
  - `enHan`: 0
  - `fallback`: 0

## 手动回归建议

- 英文环境查看左侧 BMS 菜单，不出现 `route.bms_*`。
- 英文环境进入 BMS 电池详情，外层 Tab、BMS 面板内 Tab、参数设置表格、Basic Info、Operation Logs 无中文残留。
- 英文环境打开 Advanced Settings，Advanced Config / Numbering Config / System Config / Factory Config 无中文残留。
- 英文环境逐个进入 BMS 管理子菜单，检查组织/经销商/门店/终端用户、电池列表/历史/型号/电芯品牌/标签/转移/离线指令/OTA、运营日志/通讯调试、后台账号、维保页面及弹窗、批量操作、删除确认、状态标签和错误提示无中文残留。
- 中文环境抽查同路径，确认中文展示仍正常。
