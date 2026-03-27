# FEAT-0021 UniApp 电池仪表盘组件总电压与曲线进度条优化 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-03-22
- related_feature: FEAT-0021
- version: v0.1.0

## 1. 总电压显示
- 在 `dashboard-gauge.vue` 中新增：
  - `totalVoltageText`
  - `totalVoltageLabel`
- 非微信平台通过 overlay 绝对定位到顶部中间区域显示。
- 微信小程序平台在 canvas 内同步绘制同样的标题和值，保证多端一致。

## 2. 曲线进度条
- 原方案使用离散折线点数组绘制左右轨道。
- 新方案改为左右各两段三次贝塞尔曲线：
  - 从底部内侧向中部外扩；
  - 再从中部向顶部内收；
  - 整体形态与外壳左右圆角收边方向一致。
- 为复用现有“按百分比截断路径”逻辑，先对贝塞尔曲线做离散采样，再沿采样点累计长度绘制部分路径。

## 3. 数据来源
- 总电压继续使用现有状态模型中的 `status.electrical.vPackV`。
- `dashboard-tab.vue` 负责格式化为 `xx.xV` 文本后传给组件。

## 4. 验证策略
- 执行 `cd fjbms-uniapp && pnpm exec tsc --noEmit`。
- 手工验证不同 SOC/SOH 百分比下的曲线走势与顶部总电压显示位置。
