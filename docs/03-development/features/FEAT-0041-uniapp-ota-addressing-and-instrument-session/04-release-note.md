# FEAT-0041 UniApp OTA 地址口径统一与仪表会话升级支持 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-04-15
- related_feature: FEAT-0041
- version: v0.1.0

## 发布内容
- OTA Boot 查询与升级对仪表固定使用 `0xFC`，对 BMS 固定使用 `0x01`。
- 启用仪表临时会话下的 OTA 入口。
- 后端 OTA 检查支持无 `device_id` 的模型匹配。

## 影响范围
- `fjbms-uniapp/pages/device-battery/detail.vue`
- `fjbms-uniapp/pages/device-battery/components/params-tab.vue`
- `fjbms-uniapp/service/app-battery.ts`
- `backend/internal/model/app_battery.http.go`
- `backend/internal/service/app_battery.go`
