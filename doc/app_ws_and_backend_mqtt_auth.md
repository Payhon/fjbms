# APP WebSocket 认证与后端 MQTT 客户端认证说明

本文档说明 APP 端 WebSocket 认证方式，以及后端作为 MQTT 客户端连接 Broker 时使用的认证信息来源。

---

## 1. APP 端 WebSocket 认证

### 1.1 适用接口

当前 APP 端会通过 WebSocket 与后端建立连接，主要用于：

- **电池设备 MQTT 透传**（WebSocket 桥接到后端 MQTT 客户端）
  - `GET /api/v1/app/battery/socket/ws`
- **设备遥测/在线状态 WS**（实时数据）
  - `GET /api/v1/telemetry/datas/current/ws`
  - `GET /api/v1/device/online/status/ws`
  - `GET /api/v1/telemetry/datas/current/keys/ws`

### 1.2 认证方式

后端统一使用 `token` 或 `x-api-key` 两种方式认证：

- **优先使用 token**（APP 登录后获取）
- **如果 token 校验失败，尝试 x-api-key**
- 两者都失败则认证失败

认证校验逻辑在：
- `backend/internal/api/telemetry_data.go` → `validateAuth`

### 1.3 WebSocket 首条消息格式

WebSocket 建立后，**客户端必须发送首条 JSON**：

```json
{
  "device_id": "<设备ID>",
  "token": "<APP 登录 token>"
}
```

或使用 API Key：

```json
{
  "device_id": "<设备ID>",
  "x-api-key": "<OpenAPI key>"
}
```

### 1.4 APP 端电池透传（WS → MQTT）

接口：`/api/v1/app/battery/socket/ws`

认证通过后：
- 后端会以 **自己的 MQTT 账号**连接 Broker
- 设备透传 Topic：
  - 订阅：`device/socket/tx/{device_id}`
  - 发布：`device/socket/rx/{device_id}`

逻辑实现：
- `backend/internal/api/app_battery.go`

APP 端实现参考：
- `fjbms-uniapp/pages/device-battery/detail.vue`
- `frontend/src/common/lib/bms-protocol/web-mqtt-socket-transport.ts`

---

## 2. 后端 MQTT 客户端认证信息

后端以 MQTT 客户端连接 Broker，主要用于：

1) MQTT Adapter（核心 MQTT 服务）
2) APP WS 透传桥接 MQTT
3) BMS Bridge（如启用）

这些客户端 **使用统一的配置账号**，配置项如下：

```yaml
mqtt:
  broker: 127.0.0.1:1883
  user: root
  pass: root
  client_id: thingspanel-adapter-1
```

配置文件位置：
- `backend/configs/conf.yml`
- `backend/configs/conf-dev.yml`

实际使用位置：
- MQTT Adapter：`backend/internal/app/mqtt_service.go`
- MQTT 客户端创建：`backend/internal/adapter/mqttadapter/client.go`
- APP WS 透传桥接：`backend/internal/api/app_battery.go`
- BMS Bridge：`backend/internal/bmsbridge/config.go`

---

## 3. 常见问题与注意事项

1) **APP 端不直连 Broker**
   - APP 通过 WebSocket 连接后端，由后端代为 MQTT publish/subscribe。

2) **MQTT 账号和设备账号不同**
   - 设备连接 Broker 使用 `devices.voucher` 中的 username/password。
   - 后端连接 Broker 使用 `mqtt.user` / `mqtt.pass`。

3) **token/API key 仅用于 WS 认证**
   - 仅校验 WS 请求是否来自合法用户，不影响 MQTT 账号。

---

如需扩展更多安全策略（如限制 WS 透传权限、校验 device_id 与用户绑定关系），可在 `AppBatteryApi.ServeBatterySocketByWS` 中扩展。
