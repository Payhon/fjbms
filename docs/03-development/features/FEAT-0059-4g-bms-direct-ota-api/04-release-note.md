# FEAT-0059 4G BMS 直连 OTA HTTP 接口 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-06-15
- related_feature: FEAT-0059
- version: v0.1.0

## 1. 变更摘要
- 新增 4G BMS 板 MCU 直连 OTA 检测接口：`GET /api/v1/ota/4g-bms/check`。
- 接口返回 BMS 固件升级包下载地址和校验信息，由 MCU 自行下载并执行本地升级。
- 该接口不通过 MQTT 转发，不创建 OTA 任务，不依赖 APP 在线。

## 2. 发布影响
- 需要后端发布后嵌入式侧才能调用新接口。
- 后台需配置 `BMS升级包`，不是 `4G模块升级包`。
- 既有 APP BMS OTA、4G 模块 OTA 和后台批量 OTA 行为不变。

## 3. 回滚说明
- 回滚后端接口实现即可关闭该能力。
- 无数据库变更，无需执行数据回滚。
