# FEAT-0048 BMS 4G 通讯调试管理 - 实现日志

- status: in_progress
- owner: payhon
- last_updated: 2026-04-27
- related_feature: FEAT-0048
- version: v0.1.0

## 2026-04-24
1. 新增 `backend/sql/52.sql`
   - 创建 `bms_bridge_comm_logs`
   - 新增 `bms_ops_comm_debug` 菜单项
2. 在 `backend/internal/bmsbridge/` 新增通讯日志存储逻辑
   - 4G BMS 设备识别
   - 采集上行原始包、解码、解析、下行发布、异常日志
   - 追加 7 天保留期清理
3. 新增后端查询接口与 SSE 实时流
   - `GET /api/v1/bms/comm-debug/logs`
   - `GET /api/v1/bms/comm-debug/logs/stream`
4. 新增前端页面
   - `frontend/src/views/bms/ops/comm_debug/index.vue`
   - 支持筛选、详情抽屉、实时开关
5. 新增前端路由、菜单导入与多语言项

## 2026-04-27
1. 生产环境 4G BMS 通讯链路排障
   - 定位到 `bms-bridge` 之前直接把 MQTT Topic 尾段 `item_uuid` 当作平台 `device_id` 使用，导致主平台遥测/属性主题与通讯调试日志均无法命中 `devices.id`。
   - 已在 `backend/internal/bmsbridge/bridge.go` 增加 4G 设备标识解析，支持从 `devices.id`、`devices.device_number`、`device_batteries.item_uuid`、`comm_chip_id`、`imei`、`iccid` 反查平台设备 UUID。
   - 已补充通讯调试 4G 设备识别逻辑，允许 `bms_comm_type` 为 `2/3` 的设备即使暂未回填 `imei/iccid/comm_chip_id`，也能落库 `bms_bridge_comm_logs`。
2. 4G 主动上报兼容修复
   - 已补充 `0xFF` 功能码兼容，使 bridge 能正确识别设备主动上报帧。
   - 已为 `0x100` 状态段增加短帧兼容解析：当设备只上报前半段寄存器时，bridge 以 `0xFFFF` 补齐缺失尾段后继续走状态解析，避免因长度不足而中断下游发布。
3. 在线状态兜底修复
   - 原实现只有设备存在 `device_config.other_config.heartbeat/online_timeout` 时，收到遥测/属性/事件消息才会自动上线；生产中发现扫码补建设备常缺失 `device_config_id`，导致设备虽持续上报仍长期显示离线。
   - 已调整 `TelemetryUplink`、`AttributeUplink`、`EventUplink`：收到业务数据后始终执行自动上线；若设备未配置显式心跳，则刷新默认保活 TTL（`heartbeat.default_online_ttl_sec`，默认 120 秒），确保“有数据上报即在线”。
4. 主平台 MQTT 适配层 `values` 结构兼容修复
   - 生产日志确认 `devices/telemetry` 与 `devices/attributes/+` 持续报 `Invalid ... payload: cannot unmarshal object into ... []uint8`。
   - 根因为 `backend/internal/adapter/mqttadapter/adapter.go` 将公共 payload 的 `values` 声明为普通 `[]byte`，无法接收 bridge 发布的 JSON 对象。
   - 已改为 `json.RawMessage`，保持 `values` 原始 JSON 结构透传给后续遥测/属性/事件处理链，恢复入库与在线态刷新。

## 待完成
- 本地浏览器运行态回归
- 后台账号菜单可见性确认
- 真实 `bms-bridge` 消息流联调
