# FEAT-0007 蓝牙 BMS 经 App 上云 + 后台 BMS 实时/历史可视化 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-03-09
- related_feature: FEAT-0007
- version: v0.2.1

## 1. 方案概览
- 数据入口：APP `readAllStatus` 轮询结果 -> `POST /api/v1/app/battery/report`。
- 连接入口：APP 蓝牙连接/断开 -> `POST /api/v1/app/battery/connection-status`。
- 存储：复用 `telemetry_datas`（历史）+ `telemetry_current_datas`（当前）+ `device_batteries`（SOC/SOH 最新值）。
- 实时：后端发布 `ws:device:{device_id}`，前端通过 `/telemetry/datas/current/keys/ws` 接收增量。
- 展示：后台 BMS Tab “云端优先，直连兜底”，并保留参数直连读写能力。
- 命令中继：新增 APP Relay WebSocket，WEB 下发命令实时推送至“当前 BLE owner 会话”执行并回执。
- 在线态联动：BLE-only 设备由 APP 上报/连接态同步驱动 `devices.is_online`（连接置在线、断开置离线）。

## 2. 后端设计
1. 新增 DTO：
   - `AppBatteryReportReq`：`device_id/ts/conn_type/platform/core/snapshot`
   - `AppBatteryReportResp`：`accepted/ignored_reason`
   - `AppBatteryConnectionStatusReq`：`device_id/conn_type/platform/ble_connected/ts`
   - `AppBatteryConnectionStatusResp`：`accepted/status_changed/ignored_reason`
2. 新增接口：
   - 路由：`POST /api/v1/app/battery/report`
   - 路由：`POST /api/v1/app/battery/connection-status`
   - 权限：复用 `GetBatteryDetailForApp` 绑定/组织/租户校验。
3. 数据校验：
   - `core` 仅允许白名单 key；
   - `snapshot` JSON 最大 64KB；
   - 灰度开关：`bms.app_report.enabled`、`bms.app_report.bluetooth_only`。
4. 入库事务：
   - 历史表 `telemetry_datas`：`ON CONFLICT DO NOTHING`
   - 当前表 `telemetry_current_datas`：仅当 `EXCLUDED.ts >= existing.ts` 覆盖
   - 快照按单 key `bms.snapshot` 写入 `string_v`
   - 同步 `device_batteries.soc/soh/ble_mac/updated_at`
5. 实时推送：
   - 检查 `ws:sub:{device_id}`，存在时发布 `ws:device:{device_id}`。
6. 在线状态同步：
   - `report` 成功后（BLE-only）调用 `dal.UpdateDeviceStatus(device_id, 1)`。
   - `connection-status` 在 `ble_connected=true` 时置在线；`ble_connected=false` 时若无 relay owner 则置离线。
   - 同步发布 `device:{device_id}:status`（`is_online: 0/1`）。
   - 维护 `device:{device_id}:heartbeat` TTL，用于异常断开场景离线兜底。
7. BLE Relay 指令通道：
   - APP WS：`GET /api/v1/app/battery/relay/ws`（首包鉴权 + device_id）
   - WEB API：`GET /api/v1/battery/relay/status/:id`、`POST /api/v1/battery/relay/command`
   - Redis 状态：
     - owner: `bms:relay:owner:{device_id}`（TTL）
     - session: `bms:relay:session:{session_id}`（TTL）
     - command: `bms:relay:cmd:{command_id}`（状态机）
   - 指令流：WEB -> Redis Pub/Sub -> APP Relay WS -> BLE 执行 -> APP 回执 -> WEB 查询/同步返回。

## 3. UniApp 设计
1. 上报触发：
   - 核心包：每次轮询成功（5s）
   - 快照包：30s 一次，或告警/保护/指示状态变更时立即上报
2. 去重与容错：
   - 内存队列最多 100 条；
   - 重试退避：3s/10s/30s；
   - 队列满时丢弃最旧条目。
3. 连接策略：
   - BLE 优先；
   - 微信小程序非 BLE 走 `UniMqttSocketBmsTransport`（WS 桥接）；
   - Android/iOS 保持 `UniMqttWsBmsTransport`。
4. 连接状态同步：
   - BLE 建连成功后主动调用 `appBatteryConnectionStatus(..., ble_connected=true)`。
   - BLE 主动断开/页面卸载时调用 `appBatteryConnectionStatus(..., ble_connected=false)`。

## 4. Web BMS Tab 设计
1. 云端实时：
   - 初始：`/telemetry/datas/current/keys`
   - 增量：`/telemetry/datas/current/keys/ws`
   - `bms.snapshot` 解析为 `BmsStatus`，优先渲染仪表/电芯。
2. 历史展示：
   - 核心曲线：`/telemetry/datas/statistic`（SOC/SOH/vPackV/currentA）
   - 快照时间线：`/telemetry/datas/history/page`（key=`bms.snapshot`）
3. 直连能力：
   - 参数设置继续使用现有 MQTT 透传，不受云端展示改造影响。
4. BLE-only 参数设置：
   - 当设备无 4G 通道时，参数读写改走 Relay API（read_param/write_param/write_registers）。
   - 面板显示“APP 蓝牙中继”在线状态并支持手动断开 UI 通道。

## 5. 配置与兼容
- 新增配置：
  - `bms.app_report.enabled`
  - `bms.app_report.bluetooth_only`
  - `bms.app_report.sync_device_online`
  - `bms.app_report.offline_on_ble_disconnect`
  - `bms.app_report.online_ttl_sec`
- 保留历史保留策略 15 天，不变更 `data_policy` 清理机制。
