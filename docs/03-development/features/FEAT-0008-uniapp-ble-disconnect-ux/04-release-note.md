# FEAT-0008 UniApp 蓝牙信号展示与手动断开连接优化 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-03-04
- related_feature: FEAT-0008
- version: v0.1.0

## 1. 发布内容
- 蓝牙扫描列表信号强度改为信号图标显示。
- BMS 设备详情页新增“断开蓝牙连接”按钮。
- 首页设备卡片在连接状态下方新增断开图标按钮。
- 新增 BLE 缓存层立即断开接口，提升断连响应速度。

## 2. 影响范围
- `fjbms-uniapp/pages/device-provision/ble-scan.vue`
- `fjbms-uniapp/pages/device-battery/detail.vue`
- `fjbms-uniapp/pages/device-battery/useBatteryDetail.ts`
- `fjbms-uniapp/components/home/device-card.vue`
- `fjbms-uniapp/pages/home/home.vue`
- `fjbms-uniapp/common/ble/ble-client-cache.ts`

## 3. 升级步骤
1. 发布 UniApp 包（Android/iOS/微信小程序）。
2. 验证蓝牙连接设备在首页与详情页都可手动断开。
3. 验证扫描页信号图标显示正常。

## 4. 回滚步骤
- 回滚 `FEAT-0008` 相关提交，恢复原有 RSSI 文本显示与自动空闲断连。

## 5. 已知问题
- 需真机补充跨平台 BLE 断连行为验证（尤其微信小程序）。
