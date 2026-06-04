# FEAT-0058 实现日志

## 2026-06-04

### 已完成

- 补齐 `frontend/src/locales/langs/en-us/route.json` 中 BMS 路由 key，覆盖左侧菜单、页签和面包屑常见 `route.bms_*` 缺失。
- 新增 `frontend/src/locales/langs/zh-cn/bms.json` 与 `frontend/src/locales/langs/en-us/bms.json`。
- `bms.json` 覆盖：
  - BMS Dashboard 入口页。
  - 设备详情 BMS 面板 Tab、状态、按钮、提示、弹窗、表格列名。
  - Basic Info 与 Operation Logs 字段名、空状态和错误提示。
  - 147 个 Web BMS 协议参数 label。
  - 温度显示别名、功能配置、工厂命令、电池类型和保护/告警/故障状态。
- `device/details/index.vue` 的 BMS 专用外层 Tab 改为 `$t('bms.detail.tabs.*')`。
- `bms-panel/index.vue` 改为：
  - `labelOf()` 优先读取 `bms.param.<KEY>`。
  - 连接状态、云端状态、参数通道状态、历史图表、保护状态、参数表格、高级弹窗、功能配置、工厂命令均接入 i18n。
  - 保留协议注册表中文 label 作为最后兜底，不修改协议定义。
- `battery-basic-info.vue`、`battery-operation-log.vue` 字段名和空态接入 i18n。
- `bms/dashboard/index.vue` KPI、告警概览、在线趋势、快捷入口接入 i18n。

### 待继续

- `frontend/src/views/bms/**` 其余管理页仍需逐页迁移用户可见中文，避免一次性大批量改动影响列表、弹窗和批量操作逻辑。

### 未改动

- 后端 API、权限 key、路由 name、协议寄存器、MQTT/BLE/中继读写逻辑均未改动。
- FEAT-0057 UniApp 未提交改动保持原状。
