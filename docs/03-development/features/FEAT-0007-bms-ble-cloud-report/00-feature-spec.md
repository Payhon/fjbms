# FEAT-0007 蓝牙 BMS 经 App 上云 + 后台 BMS 实时/历史可视化 - 功能规格

- status: in_progress
- owner: payhon
- last_updated: 2026-03-04
- related_feature: FEAT-0007
- version: v0.2.0

## 1. 背景与目标
- 背景：BLE 直连场景下，BMS 状态只在手机侧可见，后台缺少同源实时数据与历史轨迹。
- 目标：APP 在 BLE 连接时将 BMS 读数上报云端，后台设备详情页 BMS Tab 显示与手机一致的实时数据并支持历史追溯。

## 2. 范围
### In Scope
- 新增 `POST /api/v1/app/battery/report`，将 APP 上报写入 `telemetry_datas` 与 `telemetry_current_datas`。
- APP 增加双层上报（核心 5s、快照 30s+状态变化）。
- 后台 BMS Tab 增加云端优先展示与历史记录（曲线+快照时间线）。
- 兼容微信小程序（MQTT 不可用时走 WS 桥接）、Android、iOS。
- 新增 BLE Relay 通道：WEB 端可通过“APP 蓝牙在线会话”实时下发参数读写命令（不依赖上报周期）。

### Out of Scope
- 不新增业务表，沿用现有 telemetry 表结构。
- 不改动现有 BMS 参数读写协议与寄存器定义。

## 3. 验收标准
1. BLE 连接后，5 秒内后台 BMS Tab 可见最新 SOC/SOH/电压/电流等核心数据。
2. 后台可查询最近 1 小时曲线与最近快照时间线，并可持续写入历史。
3. 微信小程序在非 BLE 场景仍可通过 WS 桥接读取状态，不依赖 MQTT 协议。
4. 仅允许有设备权限的用户上报；跨租户/未绑定用户上报被拒绝。
5. 数据保留周期沿用 15 天策略，不新增清理任务。
6. BLE-only 设备在 WEB 参数设置页可通过 APP 中继执行读写；APP 断开蓝牙后中继状态及时失效。

## 4. 风险与约束
- 风险：手机端与设备直传链路并发写入导致重复数据。
- 风险：快照包体过大影响接口吞吐与 DB 写入。
- 约束：默认仅 BLE 场景上报（`bms.app_report.bluetooth_only=true`）。

## 5. 回滚方案
- 后端关闭 `bms.app_report.enabled=false`，APP 上报自动忽略，后台回退直连视图仍可用。
