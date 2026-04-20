# FEAT-0042 电池出厂增强与跨页批量选择 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-04-17
- related_feature: FEAT-0042
- version: v0.1.0

## 本次更新
- 第三方 MES 电池建档接口新增 `pack_factory_name`，可按 PACK 厂家名称自动完成出厂。
- 后台 `BMS管理 > 电池列表` 新增“批量出厂”。
- 电池列表勾选支持跨分页保留，批量信息补全、批量出厂、批量分配、批量标签、批量指令、批量 OTA 共用同一套跨页选择能力。

## 注意事项
- `pack_factory_name` 按当前租户下 `PACK_FACTORY` 机构名称精确匹配；未匹配或匹配不唯一时仅跳过自动出厂，不影响建档成功。
- 批量出厂采用部分成功模式，请以返回明细核对失败设备。
