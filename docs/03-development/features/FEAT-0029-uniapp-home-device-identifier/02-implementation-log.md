# FEAT-0029 UniApp 首页设备标识展示切换 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-03-27
- related_feature: FEAT-0029
- version: v0.1.0

## 1. 实施记录
1. 新建 FEAT-0029 文档目录，并在项目看板登记 Backend / UniApp 条目。
2. 扩展后端首页设备列表返回结构，新增 `iccid` 字段并兼容 `comm_chip_id` 历史数据。
3. 调整 UniApp 首页设备卡片模型，新增显式 `identifierText` 字段。
4. 在首页 `toHomeModel()` 中按通讯类型生成 MAC / ICCID 展示值，并保留旧值回退。

## 2. 当前状态
- 代码已完成。
- 已完成后端定向 Go 校验与 UniApp TypeScript 静态校验。
- 待真机/小程序联调确认蓝牙、4G、双模设备首页展示。
