# FEAT-0049 BMS 4G 移动端云端详情链路 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-04-27
- related_feature: FEAT-0049
- version: v0.1.0

## 用户影响
- 4G BMS 设备在移动端详情页将使用 MQTT 上报后的云端当前数据展示，不再因无 BLE 连接而显示离线。
- 如果设备未上报单体电芯明细，电芯 Tab 会明确提示未收到明细数据。

## 发布范围
- 后端 APP 电池接口。
- UniApp 电池详情页。

## 回滚
- 回滚后端当前遥测接口与 UniApp 云端展示分支即可恢复旧逻辑。
