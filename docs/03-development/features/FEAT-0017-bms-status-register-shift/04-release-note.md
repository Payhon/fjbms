# FEAT-0017 BMS 状态寄存器地址调整与移动端保护状态卡片 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-03-20
- related_feature: FEAT-0017
- version: v0.1.0

## 发布内容
- 同步最新 BMS 协议中 `0x12D~0x135` 状态寄存器定义。
- 修正保护状态寄存器读取地址为 `0x12F~0x130`。
- 新增总放容量状态字段 `totalDischargeCapacityRaw`。
- Web 端 BMS 面板的保护状态改为可展开全量列表，并以文本显示各保护项开关状态。
- 移动端设备详情仪表盘新增独立保护状态折叠卡片，并以文本显示各保护项开关状态。

## 影响范围
- `backend/` BMS 状态解析与桥接状态输出。
- `frontend/` Web BMS 协议解析与设备详情 BMS 面板展示。
- `fjbms-uniapp/` 蓝牙/MQTT 状态解析与设备详情仪表盘展示。
- `docs/` 协议主维护文档与项目看板。

## 发布与回滚提示
- 发布前建议执行后端定向 `go test` 与 UniApp `tsc --noEmit`。
- 如需回滚，需同时回滚协议解析地址、状态模型字段和 UniApp 仪表盘展示，保持协议口径一致。
