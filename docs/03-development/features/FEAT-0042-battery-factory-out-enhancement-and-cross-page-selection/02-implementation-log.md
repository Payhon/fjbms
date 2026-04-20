# FEAT-0042 电池出厂增强与跨页批量选择 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-04-17
- related_feature: FEAT-0042
- version: v0.1.0

## 2026-04-17
- 后端：
  - `BatteryCreateReq` 新增 `pack_factory_name`。
  - `CreateSingleBattery` 新增 PACK 厂家名称解析与自动出厂逻辑；未唯一匹配时跳过自动出厂并写入运营日志。
  - 抽取单条出厂复用逻辑，新增 `BatchFactoryOutBattery` 及接口路由。
  - 新增批量出厂响应结构。
- 前端：
  - 电池列表新增跨页勾选缓存 `selectedRowsMap`。
  - 批量操作菜单新增“批量出厂”。
  - 批量信息补全、批量分配、批量标签、批量指令、批量 OTA 统一改为使用跨页勾选集合。
- 配套：
  - 新增权限 SQL `49.sql` 与中英文本地化。
  - 更新第三方接入文档与项目看板。
