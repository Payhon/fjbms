# FEAT-0047 BMS 分页修复与电池详情操作记录 Tab - 实现记录

- status: in_progress
- owner: payhon
- last_updated: 2026-04-22
- related_feature: FEAT-0047
- version: v0.1.0

## 2026-04-22
1. 后端 `battery_operation_logs` 查询接口新增 `device_id` 可选过滤，并保持租户/组织数据隔离。
2. 前端以下服务端分页页面显式启用 `NDataTable remote`，修复页码按当前页长度计算的问题：
   - 运营管理 > 操作记录
   - 运营管理 > 激活日志
   - BMS 型号管理
   - API Key 列表
   - APP 用户选择弹窗
3. 新增电池详情 `battery-operation-log.vue` 组件，用于在 BMS 详情模式下分页展示当前电池的运营日志。
4. 详情页 BMS 模式 Tab 调整为 `BMS面板 / 基本信息 / 操作记录 / 连接`，并在 Tab 装配前接入 UI 权限加载。
5. 新增页面元素权限 `bms_battery_detail_operation_log`，同步：
   - `backend/sql/51.sql`
   - `backend/sql/1.sql`
   - 中英文 locale 文案
6. 默认权限策略：
   - 厂家账号走管理员放行；
   - `PACK_FACTORY`、`DEALER` 自动补齐该权限；
   - `STORE` 不自动补齐。
