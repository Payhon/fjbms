# FEAT-0017 BMS 状态寄存器地址调整与移动端保护状态卡片 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-03-25
- related_feature: FEAT-0017
- version: v0.1.0

## 日志
1. 2026-03-20 协议差异确认
   - 已对照 `doc/oriigin/device_comm_protocol_basic.md` 确认最新状态区间定义：
     - `0x12D~0x12E`：总放容量
     - `0x12F~0x130`：保护状态
     - `0x131`：失效状态
     - `0x132~0x133`：指示状态
     - `0x134~0x135`：告警状态
2. 2026-03-20 后端与协议层同步
   - `backend/internal/bms/status/status_parser.go` 已将保护状态读取地址改为 `0x12F`。
   - `backend/internal/bms/status/types.go`、`backend/internal/bmsbridge/flatten.go` 已新增总放容量字段。
   - `backend/cmd/bms-sim/main.go` 已同步模拟器状态寄存器布局。
3. 2026-03-20 UniApp 同步
   - `fjbms-uniapp/common/lib/bms-protocol/status-parser.ts` 已将保护状态地址改为 `0x12F`，并新增总放容量读取。
   - `fjbms-uniapp/common/lib/bms-protocol/types.ts`、`param-registry.ts` 已补充 `totalDischargeCapacityRaw`。
4. 2026-03-20 Frontend Web 同步
   - `frontend/src/common/lib/bms-protocol/status-parser.ts` 已将保护状态地址改为 `0x12F`，并新增总放容量读取。
   - `frontend/src/common/lib/bms-protocol/types.ts`、`param-registry.ts` 已补充 `totalDischargeCapacityRaw`。
   - `frontend/src/views/device/details/modules/bms-panel/index.vue` 已将 BMS 面板中的保护状态改为独立可展开列表，不再只显示激活标签。
5. 2026-03-20 仪表盘改版
   - `fjbms-uniapp/pages/device-battery/components/dashboard-tab.vue` 已将保护状态改为独立可折叠卡片，内部展示全量保护项开关文本。
   - `fjbms-uniapp/lang/zh-CN.ts`、`lang/en-US.ts` 已补齐展开/收起与开关状态文案。
6. 2026-03-20 文档回写
   - 已更新主维护协议文档 `docs/02-architecture/system-design/protocol-source/device-comm-basic.md`。
   - 已新增 FEAT-0017 文档并同步项目看板。
7. 2026-03-25 UniApp 仪表盘温度与折叠默认态修正
   - `fjbms-uniapp/pages/device-battery/components/dashboard-tab.vue` 已改为根据 `status.temperature.cellTempsC` 动态渲染多个电芯温度，文案按 `T{n}` 从 1 开始编号；环境温度独立展示，不再占用 `T1` 序号。
   - 同文件中 `BMS保护状态` 卡片默认态已改为收起，仅在用户点击头部时展开。
   - `fjbms-uniapp/lang/zh-CN.ts`、`lang/en-US.ts` 已补充动态 `T{n}` 温度标题文案。
8. 2026-03-25 UniApp 仪表盘温度区排版微调
   - `fjbms-uniapp/pages/device-battery/components/dashboard-tab.vue` 已将温度区改为横向网格布局，每行最多展示 4 个温度项，单项内部保持“标题在上、数值在下”的展示方式。
9. 2026-03-25 UniApp 仪表盘温度项文案与对齐调整
   - 温度网格项的标题和值已改为水平居中展示。
   - 电芯温度标题由 `T{n}：电芯温度` 简化为仅显示 `T{n}`，例如 `T1`、`T2`。
