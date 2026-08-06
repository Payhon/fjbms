# FEAT-0041 UniApp OTA 地址口径统一与仪表会话升级支持 - 发布说明

- status: review
- owner: payhon
- last_updated: 2026-07-25
- related_feature: FEAT-0041
- version: v0.4.0

## 发布内容
- OTA Boot 查询与升级对仪表固定使用 `0xFC`，对 BMS 固定使用 `0x01`。
- 启用仪表临时会话下的 OTA 入口。
- 后端 OTA 检查支持无 `device_id` 的模型匹配。
- 仪表临时会话读取下级 BMS 的等待时间统一为 10 秒；到期后返回主面板并展示继续扫码入口。

## 影响范围
- `fjbms-uniapp/pages/device-battery/detail.vue`
- `fjbms-uniapp/pages/device-battery/useBatteryDetail.ts`
- `fjbms-uniapp/pages/device-battery/instrument-passthrough-policy.ts`
- `fjbms-uniapp/pages/device-battery/components/params-tab.vue`
- `fjbms-uniapp/service/app-battery.ts`
- `backend/internal/model/app_battery.http.go`
- `backend/internal/service/app_battery.go`

## 兼容说明
- 不修改后端接口、数据库、通用 BLE 请求超时和普通 BMS/MQTT 实时读取。
- 仪表蓝牙连接保持不变，手动重新读取或重新连接会重新开始 10 秒等待。

## 发布前验收
- 微信小程序、iOS、Android 真机验证 10 秒等待、成功回包、临界/迟到回包和人工重试。
