# FEAT-0029 UniApp 首页设备标识展示切换 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-06-12
- related_feature: FEAT-0029
- version: v0.1.0

## 2026-03-27
1. 新建 FEAT-0029 文档目录，并在项目看板登记 Backend / UniApp 条目。
2. 扩展后端首页设备列表返回结构，新增 `iccid` 字段并兼容 `comm_chip_id` 历史数据。
3. 调整 UniApp 首页设备卡片模型，新增显式 `identifierText` 字段。
4. 在首页 `toHomeModel()` 中按通讯类型生成 MAC / ICCID 展示值，并保留旧值回退。

## 2026-06-12
1. 修正移动端首页 4G BMS 设备卡片标识口径
   - 后端 `/api/v1/app/device/list` 响应新增 `imei` 字段，三个视图分支均从 `device_batteries.imei` 透出。
   - UniApp 首页 `DeviceListItem` 与 `HomeDeviceCardModel` 增加 `imei` 字段。
   - `formatDeviceIdentifier()` 调整为 `bms_comm_type=2/3` 时优先显示 IMEI，IMEI 为空再回退 ICCID/历史 `comm_chip_id` 兼容值。
   - 蓝牙设备 MAC 展示、在线状态、蓝牙自动连接和卡片交互逻辑不变。

## 2. 当前状态
- 代码已完成。
- 已完成后端定向 Go 校验与 UniApp TypeScript 静态校验。
- 待真机/小程序联调确认 4G 与双模 BMS 设备首页展示 IMEI。
