# 4G BMS 直连 OTA 固件版本检测接口说明

## 1. 接口用途

该接口供 4G 类型 BMS 板 MCU 在无需登录的情况下检测 BMS 固件是否需要升级，并获取可直接下载的固件文件 URL。

该接口用于 BMS 板 MCU 固件升级，不用于 4G 模块自身固件升级。4G 模块自身升级仍使用：

```http
GET /api/v1/ota/4g-module/check
```

本接口只返回升级包信息和固件下载地址，不通过 MQTT 转发升级包，不创建 OTA 升级任务，也不要求 APP 或 WebSocket 参与转发。

## 2. 接口地址

```http
GET /api/v1/ota/4g-bms/check
```

示例完整地址：

```text
https://cloud.fjiaenergy.com/api/v1/ota/4g-bms/check?tenant_id=d616bcbb&item_uuid=BMS202606150001&version=1.0.0
```

## 3. 认证与租户参数

该接口无需登录 Token，不需要 `Authorization`。

必须传入租户 ID，可以通过 Query 参数或 Header 传递。推荐 MCU 侧直接使用 Query 参数 `tenant_id`。

优先级：

1. Query 参数 `tenant_id`
2. Header `X-Tenant-ID`
3. 兼容 Header `X-TenantID`

Query 参数：

| 参数 | 必填 | 说明 |
|------|------|------|
| `tenant_id` | 条件必填 | 当前设备所属租户 ID；如果 Header 已传租户 ID，则 Query 可不传 |

Header：

| Header | 必填 | 说明 |
|--------|------|------|
| `X-Tenant-ID` | 条件必填 | 当前设备所属租户 ID；如果 Query 已传 `tenant_id`，则 Header 可不传 |

兼容旧头名：

| Header | 说明 |
|--------|------|
| `X-TenantID` | 当 Query `tenant_id` 和 Header `X-Tenant-ID` 均为空时，后端会尝试读取该兼容头 |

## 4. 请求参数

Query 参数：

| 参数 | 类型 | 必填 | 限制 | 说明 |
|------|------|------|------|------|
| `tenant_id` | string | 条件必填 | 最大 36 字符 | 当前设备所属租户 ID；也可通过 Header 传递 |
| `item_uuid` | string | 是 | 最大 64 字符 | BMS 电池序列号，对应 `device_batteries.item_uuid`，通常也等于 `devices.device_number` |
| `version` | string | 是 | 最大 36 字符 | BMS 板 MCU 当前固件版本号 |
| `imei` | string | 否 | 最大 64 字符 | 4G 模块 IMEI，仅用于现场排查或二次校验说明，不作为主匹配键 |
| `comm_chip_id` | string | 否 | 最大 64 字符 | 4G 通讯卡 ID，仅用于现场排查或二次校验说明，不作为主匹配键 |

请求示例（推荐，租户 ID 通过 Query 传递）：

```bash
curl -X GET \
  'https://cloud.fjiaenergy.com/api/v1/ota/4g-bms/check?tenant_id=d616bcbb&item_uuid=BMS202606150001&version=1.0.0'
```

请求示例（兼容，租户 ID 通过 Header 传递）：

```bash
curl -X GET \
  'https://cloud.fjiaenergy.com/api/v1/ota/4g-bms/check?item_uuid=BMS202606150001&version=1.0.0' \
  -H 'X-Tenant-ID: d616bcbb'
```

请求示例（携带 4G 通讯信息，便于排查）：

```bash
curl -X GET \
  'https://cloud.fjiaenergy.com/api/v1/ota/4g-bms/check?tenant_id=d616bcbb&item_uuid=BMS202606150001&version=1.0.0&imei=860000000000000&comm_chip_id=89860000000000000000'
```

## 5. 响应格式

接口返回项目统一响应结构：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "need_upgrade": true,
    "item_uuid": "BMS202606150001",
    "current_version": "1.0.0",
    "version": "1.0.2",
    "target_version": "1.0.0",
    "firmware_url": "https://cloud.fjiaenergy.com/api/v1/ota/download/files/upgradePackage/20260615/bms.bin",
    "package_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "package_type": 2,
    "signature_type": "SHA256",
    "signature": "8f434346648f6b96df89dda901c5176b10a6d83961dd3c1ac88b59b2dc327aa4",
    "module": "BMS",
    "description": "修复 BMS 采样稳定性",
    "additional_info": "{\"min_soc\":30}",
    "remark": "4G BMS 直连下载升级包"
  }
}
```

`data` 字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| `need_upgrade` | boolean | 是否需要升级 |
| `item_uuid` | string | 本次请求传入的 BMS 电池序列号 |
| `current_version` | string | 本次请求传入的当前版本号 |
| `version` | string | 可升级固件版本号；无升级时可能为空 |
| `target_version` | string | 升级包要求的待升级版本；升级包未限制时可能为空 |
| `firmware_url` | string | 固件下载 URL；仅需要升级且命中升级包时返回 |
| `package_id` | string | 后台升级包 ID；仅命中升级包时返回 |
| `package_type` | number | 升级包类型：`1` 差分包，`2` 整包 |
| `signature_type` | string | 签名或摘要算法，例如 `MD5`、`SHA256` |
| `signature` | string | 固件文件签名或摘要值，MCU 可用于下载后校验 |
| `module` | string | 升级模块名称，例如 `BMS` |
| `description` | string | 升级包说明 |
| `additional_info` | string | 升级包附加信息，通常为 JSON 字符串 |
| `remark` | string | 升级包备注 |

## 6. 判断规则

1. 校验 `version`、`item_uuid` 和租户 ID。
2. 根据 `tenant_id + item_uuid` 确认设备存在且属于当前租户；`item_uuid` 对应 `device_batteries.item_uuid`。
3. 只查询 BMS 固件包，即 `ota_upgrade_packages.device_kind=1`。
4. 允许当前租户升级包和公共升级包，即 `tenant_id = 当前租户 OR tenant_id IS NULL`。
5. 只考虑版本号大于当前 `version` 的升级包。
6. 如果升级包配置了 `target_version`，则 `target_version` 必须等于当前 `version`。
7. 按 BMS OTA 约束字段匹配升级包：`item_uuid`、`battery_model_id`、`batch_number`。
8. 约束优先级沿用现有 BMS OTA 规则：三字段全匹配优先于两字段全匹配；单字段约束按 `item_uuid > battery_model_id > batch_number` 排序；无约束包作为通用兜底。
9. 同等匹配条件下，优先返回版本号更高的升级包；版本号相同时，返回创建时间较新的升级包。
10. 如果没有可升级包，返回 `need_upgrade=false`。
11. `firmware_url` 返回可直接下载的 URL；如果后台保存的包路径已是 `http://` 或 `https://`，则原样返回，否则按现有 OTA 下载地址拼成完整 URL。

## 7. 无升级响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "need_upgrade": false,
    "item_uuid": "BMS202606150001",
    "current_version": "1.0.2"
  }
}
```

常见无升级原因：

- `item_uuid` 在当前租户下不存在。
- 后台没有 BMS 升级包。
- 后台升级包版本不大于请求版本。
- 升级包配置了 `target_version`，但与请求版本不一致。
- 升级包配置了 BMS 型号、批号或单台序列号约束，但当前设备不匹配。

## 8. 错误响应示例

缺少租户 ID：

```json
{
  "code": 100002,
  "message": "tenant_id or X-Tenant-ID is required"
}
```

缺少 `item_uuid`：

```json
{
  "code": 100002,
  "message": "item_uuid is required"
}
```

缺少 `version`：

```json
{
  "code": 100002,
  "message": "version is required"
}
```

## 9. MCU 侧调用流程

推荐 MCU 侧按以下流程处理：

1. 上电或定时任务触发 OTA 检测。
2. MCU 读取本机 BMS 固件版本号和电池序列号 `item_uuid`。
3. MCU 调用 `GET /api/v1/ota/4g-bms/check`。
4. 如果 `need_upgrade=false`，结束本次检测。
5. 如果 `need_upgrade=true`，MCU 使用 `firmware_url` 直接下载固件文件。
6. MCU 根据 `signature_type` 和 `signature` 校验固件文件。
7. 校验通过后，MCU 按 BMS 板本地 OTA 流程写入固件。
8. 升级完成后，设备后续上报新的 BMS 固件版本。

注意事项：

- MCU 不需要订阅 MQTT OTA Topic。
- MCU 不需要等待后台创建 OTA 任务。
- MCU 不需要 APP 保持在线。
- 固件下载建议使用 HTTPS。
- 如果下载或校验失败，MCU 应保留当前固件并在下次检测周期重试。

## 10. 后台配置要求

后台路径：

```text
后台管理 > BMS 管理 > OTA管理 > 升级包管理 > BMS升级包
```

需要配置：

- 升级包名称
- 版本号
- 目标版本号（可选）
- BMS 型号约束（可选）
- 批号约束（可选）
- 单台序列号约束 `item_uuid`（可选）
- 升级包类型：差分包或整包
- 签名算法：`MD5` 或 `SHA256`
- 升级包固件
- 说明
- 备注

后台必须选择 `BMS升级包`，不要选择 `4G模块升级包`。`4G模块升级包` 只用于 4G 通讯模块自身固件升级。

## 11. 与现有 MQTT/APP OTA 的区别

| 项目 | 4G BMS 直连 HTTP OTA | 现有 MQTT/APP OTA |
|------|----------------------|-------------------|
| 发起方 | BMS 板 MCU | APP、后台或 MQTT 任务链路 |
| 固件获取 | MCU 调 HTTP 接口后直接下载 | APP 或后台先获取包信息，再通过现有链路执行 |
| MQTT 转发 | 不使用 | 可能使用 MQTT Socket 或 OTA Topic |
| OTA 任务 | 不创建后台 OTA 任务 | 批量 OTA 会创建任务和任务详情 |
| APP 依赖 | 不依赖 APP 在线 | APP OTA 需要 APP 参与 |
| 升级包类型 | `device_kind=1` 的 BMS 升级包 | BMS、仪表或 4G 模块按各自链路区分 |

该接口的目标是让 4G 类型 BMS 设备在具备 HTTP 下载能力时，由 BMS 板 MCU 自主完成检测、下载、校验和本地升级。
