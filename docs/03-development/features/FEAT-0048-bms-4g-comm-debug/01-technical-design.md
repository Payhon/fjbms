# FEAT-0048 BMS 4G 通讯调试管理 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-04-24
- related_feature: FEAT-0048
- version: v0.1.0

## 1. 设计概览
- 采集入口固定为 `backend/internal/bmsbridge/bridge.go`，不扩展到主站其他 MQTT 组件。
- 原始通讯日志单独落表 `bms_bridge_comm_logs`，不复用 Redis diagnostics 或通用 operation logs。
- 实时查看采用独立 SSE 接口，服务端按 `after_id` 增量查询新日志。

## 2. bridge 侧设计
### 2.1 设备筛选
- `device_id` 必须满足：
  - 能关联到 `device_batteries`
  - 且 `imei / iccid / module_sw_version / comm_chip_id` 至少一个非空
- 查询结果按 `device_id` 缓存在 bridge 进程内，避免每条消息都重复查库。

### 2.2 采集点
- `subscribe()`：写入 `uplink_raw`
- `handleIncoming()`：
  - `decodeSocketHex` 成功后写 `uplink_decoded`
  - `ParseFrame` 成功后写 `uplink_parsed`
  - 解码/解析失败写 `uplink_error`
- `publishJSON()`：
  - 发布前写 `downlink_publish`
  - 发布超时或 broker 返回错误写 `downlink_error`

### 2.3 保留期清理
- 在 `cleanupLoop()` 中增加每小时一次的清理逻辑：
  - 删除 `occurred_at < now() - 7d` 的日志

## 3. 后端接口设计
- `GET /api/v1/bms/comm-debug/logs`
  - 入参：`page`、`page_size`、`device_id`、`device_number`、`event_type`、`status`、`start_time`、`end_time`
  - 权限：沿用 BMS 后台 JWT + Casbin + 组织隔离
- `GET /api/v1/bms/comm-debug/logs/stream`
  - 入参：`after_id`、`device_id`、`event_type`
  - 逻辑：每 2 秒增量查询一次新日志，SSE 推送 `comm-debug` 事件

## 4. 前端设计
- 菜单：`BMS管理 > 通讯调试管理`
- 页面：
  - 查询区：设备 ID、设备编号、事件类型、状态、时间范围
  - 列表：时间、设备 ID、设备编号、类型、方向、Topic、状态、摘要
  - 明细：原始 payload + 解析摘要
  - 实时开关：控制 SSE 连接

## 5. 已知边界
- 本期不提供 MQTT 认证 / 连接 / 断开日志；如需补齐，必须通过 Broker WebHook 或等价回调接入。
