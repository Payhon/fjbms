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
- 新增 `frontend/src/views/bms/_shared/i18n.ts`，统一封装 BMS 管理页 `bt()` 翻译入口，避免各页面重复拼接 `bms.*` key。
- 将 `frontend/src/views/bms/**` 下用户可见中文迁移到 `frontend/src/locales/langs/{zh-cn,en-us}/bms.json`：
  - 组织、经销商、门店、终端用户、后台账号、维保。
  - 电池列表、历史数据、型号、电芯品牌、标签、转移、离线指令、OTA 包、OTA 任务和任务详情。
  - 运营日志、激活日志、通讯调试。
  - 表单 label/placeholder、表格列、按钮、Tab、弹窗标题、确认文案、校验提示、toast、空状态、状态枚举和批量操作结果文案。
- 对带动态值的文案新增参数化 key，例如选中电池数量、导入进度、任务 ID、组织类型标题、批量操作结果、失败/拒绝明细等；设备编号、MAC、版本号、日志 payload、后端错误详情等动态业务数据仍原样展示。
- 将组织类型、授权模板、OTA 状态、离线指令状态、激活方式、维保状态等前端固定状态映射改为通过 locale 输出。
- 清理英文词包自动占位值，确保 `bms.json` 中英文 key 集合一致，英文侧无中文字符和 `Text <hash>` 占位。

### 待继续 / 手动确认

- 仍需在真实英文环境逐个打开 BMS 管理菜单，抽查页面、弹窗、批量操作、删除确认、状态标签和错误提示展示效果。
- 仍需在中文环境抽查同路径，确认既有业务流程和中文显示不变。

### 未改动

- 后端 API、权限 key、路由 name、协议寄存器、MQTT/BLE/中继读写逻辑均未改动。
- FEAT-0057 UniApp 未提交改动保持原状。
