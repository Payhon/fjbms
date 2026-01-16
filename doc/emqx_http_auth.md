# EMQX HTTP 认证对接（不直连 DB）

本文档基于本仓库实现的 **EMQX HTTP 认证接口**，用于让 EMQX 通过 HTTP 回调到后端校验设备的 MQTT 用户名/密码（凭证来源仍是 `devices.voucher`），从而避免 EMQX 直接连接数据库。

> 适用范围：EMQX 4.x / 5.x（配置项名称略有差异，下面提供通用配置思路与示例）。

---

## 1. 背景与认证逻辑

- 设备凭证存储在数据库 `devices.voucher` 字段（JSON 字符串）
  - BASIC：`{"username":"...","password":"..."}`
  - ACCESSTOKEN：`{"username":"..."}`（无 password）
- EMQX 连接时携带 `username/password`，EMQX 通过 HTTP 回调到本服务进行校验：
  - 若 DB 中 `password` 为空，则 **仅允许空密码**
  - 否则必须完全匹配

认证逻辑由后端接口完成，EMQX **不需要直接连接 DB**。

---

## 2. 后端 HTTP 认证接口

### 2.1 接口地址

```
POST /api/v1/mqtt/auth
GET  /api/v1/mqtt/auth   (兼容 query 参数)
```

### 2.2 请求参数（EMQX 透传）

后端支持 JSON / x-www-form-urlencoded，两者字段一致：

```json
{
  "clientid": "mqtt_xxx",
  "username": "uuid-username",
  "password": "xxxxxxx",
  "protocol": "mqtt",
  "peername": "1.2.3.4:12345"
}
```

### 2.3 响应

```json
{ "result": "allow", "is_superuser": false }
```

或失败：

```json
{ "result": "deny", "reason": "password mismatch" }
```

> 后端始终返回 HTTP 200，由 `result` 字段决定放行/拒绝。

---

## 3. 后端配置

在 `backend/configs/conf.yml` / `backend/configs/conf-dev.yml` 中新增：

```yaml
mqtt:
  http_auth:
    # EMQX HTTP 认证共享密钥（建议配置；为空则不校验）
    shared_secret: ""
```

### 3.1 共享密钥传递方式

当 `shared_secret` 非空时，后端会校验以下任一头：

- `X-EMQX-API-KEY: <secret>`
- `X-API-KEY: <secret>`
- `Authorization: Bearer <secret>`

建议只保留一种，避免混淆。

---

## 4. EMQX 配置思路（HTTP Auth）

> 由于 EMQX 4.x / 5.x 配置项不同，下面给出通用字段/示例；具体字段请根据版本在 Dashboard 或配置文件中对照设置。

### 4.1 通用配置要点

- **认证方式**：HTTP
- **HTTP Method**：POST
- **URL**：`http://<backend-host>:<port>/api/v1/mqtt/auth`
- **Headers**：
  - `Content-Type: application/json`
  - `X-EMQX-API-KEY: <shared_secret>`（如果启用了共享密钥）
- **Body**：包含 `username/password/clientid` 等字段

### 4.2 参考请求体模板

```
{
  "username": "${username}",
  "password": "${password}",
  "clientid": "${clientid}",
  "protocol": "${protocol}",
  "peername": "${peername}"
}
```

### 4.3 ACL（可选）

本次仅实现认证接口；若需要 ACL 授权控制，请使用 EMQX 自身 ACL 功能或后续扩展 HTTP ACL 接口。

---

## 5. 认证行为说明

- **BASIC 设备**：必须同时匹配 username + password
- **ACCESSTOKEN 设备**：password 为空时允许；若客户端提供了非空 password，会被拒绝
- **设备不存在/凭证异常**：拒绝

---

## 6. 代码位置

- 接口实现：`backend/internal/api/mqtt_http_auth.go`
- 认证服务：`backend/internal/service/mqtt_http_auth.go`
- DB 查询：`backend/internal/dal/devices.go`（`GetDeviceByMQTTUsername`）
- 配置：`backend/configs/conf.yml`、`backend/configs/conf-dev.yml`

---

## 7. 快速自测（可选）

1) 确认设备凭证（DB 中 `devices.voucher`）：

```json
{"username":"u1","password":"p1"}
```

2) 调用接口：

```bash
curl -X POST http://localhost:9999/api/v1/mqtt/auth \
  -H 'Content-Type: application/json' \
  -H 'X-EMQX-API-KEY: <shared_secret>' \
  -d '{"username":"u1","password":"p1","clientid":"mqtt_u1"}'
```

预期返回：

```json
{ "result": "allow", "is_superuser": false }
```

---

如需扩展 ACL 控制、客户端 ID 校验或启用更严格的设备状态判断，请在 `MqttHTTPAuth.Auth` 中追加逻辑。
