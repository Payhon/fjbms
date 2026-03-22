# FEAT-0020 UniApp 设备详情页单体文案与充放电剩余时间调整 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-03-22
- related_feature: FEAT-0020
- version: v0.1.0

## 1. 参数设置文案
- 在 `params-tab.vue` 中为单体分组建立键集合。
- 生成参数项时，如果参数属于单体分组且文案未包含“单体”，则在展示层统一补齐前缀。
- 该策略只作用于“单体设置”分组，不改动总压、温度、电流等其它分组。

## 2. 仪表盘剩余时间
- 在 `dashboard-tab.vue` 中移除顶部独立 `remain` 区域。
- 时间卡片改为计算属性驱动：
  - `charging=true` 时，标题使用“充电剩余时间”，数值读取 `status.timing.chargeRemainingMin`，格式为 `${n}min`。
  - `discharging=true` 时，标题使用“放电剩余时间”，数值读取 `status.timing.dischargeRemainingMin`，格式为 `-${n}min`。
  - 其它状态时，标题使用“充放电剩余时间”，数值显示 `-`。

## 3. 协议口径
- 剩余时间继续复用现有状态寄存器整块读取。
- 数据来源：
  - `0x111`：放电剩余时间，2 字节，单位 `min`
  - `0x112`：充电剩余时间，2 字节，单位 `min`
- 现有 `status-parser.ts` 已将这两个寄存器映射为：
  - `timing.dischargeRemainingMin`
  - `timing.chargeRemainingMin`

## 4. 验证策略
- 执行 `cd fjbms-uniapp && pnpm exec tsc --noEmit`。
- 手工验证单体分组文案、充电/放电/空闲三种状态下的时间标题和值。
