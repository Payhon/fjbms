# FEAT-0073 设备详情 UUID 复制与 4G IMEI 展示 - 发布说明

- status: review
- owner: payhon
- last_updated: 2026-08-30
- related_feature: FEAT-0073
- version: v0.1.0

## 1. 发布内容

- 设备详情仪表盘页新增完整 UUID 展示与点击复制。
- 4G/双模设备通过非蓝牙链路查看时，仪表盘设备标识改为 IMEI。
- IMEI 缺失时明确显示横杠，避免把 MAC 或通讯卡号误认为 IMEI。

## 2. 影响范围

- 后端 APP 电池详情接口。
- UniApp 设备详情仪表盘、通用仪表组件和中英文文案。

## 3. 升级步骤

- 生产后端已于 2026-08-30 发布，详情接口已提供可空 IMEI。
- 再发布对应 UniApp/微信小程序版本。
- 使用 4G、双模和蓝牙设备各验证一条详情链路。

## 4. 回滚步骤

- 后端可使用 `/www/fjia/backups/fjbms/backend/backend_20260830_175322_pre_feat0073.bin` 恢复旧二进制并重启 `fjbms-backend`。
- UniApp 可回滚详情接口 IMEI 字段类型和仪表标识展示改动。
- 无数据库变更或数据回滚步骤。

## 5. 已知问题

- 生产后端、健康检查、运行中 Swagger 和目标生产数据已验证；375px 微信小程序、Android/iOS 真机与真实 4G/双模/蓝牙设备验收完成前，功能保持 `review` 状态。
