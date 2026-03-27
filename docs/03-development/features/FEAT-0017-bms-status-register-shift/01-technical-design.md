# FEAT-0017 BMS 状态寄存器地址调整与移动端保护状态卡片 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-03-25
- related_feature: FEAT-0017
- version: v0.1.0

## 1. 设计概览
- 协议主文档以 `doc/oriigin/device_comm_protocol_basic.md` 为依据，将主维护副本中的 `0x12D~0x135` 区间更新为最新定义。
- 后端 `status_parser.go` 将保护状态读取地址改为 `0x12F`，同时增加 `totalDischargeCapacityRaw` 对 `0x12D~0x12E` 的读取。
- Frontend 与 UniApp 共用同一套协议建模思路，Web 端 `status-parser.ts`、`types.ts`、`param-registry.ts` 也同步新增总放容量字段并后移保护状态地址。
- UniApp `status-parser.ts` 与 `types.ts`、`param-registry.ts` 同步新增总放容量字段，并将保护状态读取地址后移。
- 仪表盘页面将保护状态从“激活标签集合”重构为“可折叠卡片 + 全量状态列表”，列表状态由布尔值映射为文本。
- 仪表盘温度区复用 `status.temperature.cellTempsC`，按 `meta.cellTempCount` 对应的数组长度动态渲染 `T1...Tn` 电芯温度行。

## 2. 数据结构调整
- 后端：
  - `backend/internal/bms/status/types.go`
  - `backend/internal/bmsbridge/flatten.go`
- UniApp：
  - `fjbms-uniapp/common/lib/bms-protocol/types.ts`
  - `fjbms-uniapp/common/lib/bms-protocol/param-registry.ts`
- Frontend：
  - `frontend/src/common/lib/bms-protocol/types.ts`
  - `frontend/src/common/lib/bms-protocol/param-registry.ts`
  - `frontend/src/views/device/details/modules/bms-panel/index.vue`

## 3. UI 方案
- 保留仪表盘顶部故障/告警/保护提示入口，用于快速查看当前激活项。
- 移除开关网格中的“保护状态”开关，避免与独立保护卡片重复。
- 新增保护状态卡片：
  - 头部显示标题、激活数量摘要以及展开/收起操作文本。
  - 默认折叠，用户点击头部后再展开详情。
  - 内容区展示所有保护项及其当前文本状态。
  - 激活项使用强调色，未激活项使用次级文案色。
- 温度区域：
  - 保留 `MOS温度` 与 `环境温度` 两个固定行。
  - 从 `cellTempsC[0]` 开始依次渲染为 `T1：电芯温度`、`T2：电芯温度` 等。
  - 不再回退为单一电芯温度文案，避免与实际电芯温度数量不一致。

## 4. 验证策略
- 后端执行定向 `go test`，确保本次修改未破坏编译。
- UniApp 执行 `tsc --noEmit` 进行类型验证。
- Frontend 执行 `pnpm typecheck`，确保 Web 端面板和协议类型改动可编译。
- 手工验收关注：
  - 有保护项激活时的摘要数量和列表状态；
  - 无保护项激活时卡片仍显示且列表状态为关闭；
  - 顶部保护提示入口与卡片展示口径一致。
  - 电芯温度数量为 `0/1/多路` 时温度区行数和标题序号正确。
