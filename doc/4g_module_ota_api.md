# 4G 模块 OTA 固件版本检测接口说明

## 1. 接口用途

该接口供 4G 模块或设备侧服务在无需登录的情况下检测 4G 模块固件是否需要升级。

接口会根据调用方上报的当前固件版本号、IMEI 或 4G 通讯卡 ID 和租户 ID，查找后台 `4G模块升级包` 中可用的升级包，并返回是否需要升级以及固件下载 URL。

## 2. 接口地址

```http
GET /api/v1/ota/4g-module/check
```

示例完整地址：

```text
https://cloud.fjiaenergy.com/api/v1/ota/4g-module/check?tenant_id=d616bcbb&version=1.0.0&imei=860000000000000
```

## 3. 认证与租户参数

该接口无需登录 Token，不需要 `Authorization`。

必须传入租户 ID，可以通过 Query 参数或 Header 传递。推荐 4G 模块侧直接使用 Query 参数 `tenant_id`。

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
| `version` | string | 是 | 最大 36 字符 | 4G 模块当前固件版本号 |
| `imei` | string | 是 | 最大 64 字符 | 4G 模块 IMEI 或 4G 通讯卡 ID。后端会匹配 `device_batteries.comm_chip_id` 或 `device_batteries.imei`，任一字段命中即可 |

请求示例（推荐，租户 ID 通过 Query 传递）：

```bash
curl -X GET \
  'https://cloud.fjiaenergy.com/api/v1/ota/4g-module/check?tenant_id=d616bcbb&version=1.0.0&imei=860000000000000'
```

请求示例（兼容，租户 ID 通过 Header 传递）：

```bash
curl -X GET \
  'https://cloud.fjiaenergy.com/api/v1/ota/4g-module/check?version=1.0.0&imei=860000000000000' \
  -H 'X-Tenant-ID: d616bcbb'
```

## 5. 响应格式

接口返回项目统一响应结构：

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "need_upgrade": true,
    "current_version": "1.0.0",
    "version": "1.0.2",
    "firmware_url": "https://example.com/api/v1/ota/download/files/upgradePackage/20260507/module.bin",
    "package_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
    "name": "4G模块固件",
    "description": "修复通信稳定性",
    "is_latest": true,
    "imei": "860000000000000"
  }
}
```

`data` 字段说明：

| 字段 | 类型 | 说明 |
|------|------|------|
| `need_upgrade` | boolean | 是否需要升级 |
| `current_version` | string | 本次请求传入的当前版本号 |
| `version` | string | 可升级固件版本号；无升级时可能为空 |
| `firmware_url` | string | 固件下载 URL；仅需要升级且命中升级包时返回 |
| `package_id` | string | 后台升级包 ID；仅命中升级包时返回 |
| `name` | string | 升级包名称 |
| `description` | string | 升级包说明 |
| `is_latest` | boolean | 返回的升级包是否标记为最新固件 |
| `imei` | string | 本次请求传入的 IMEI |

## 6. 判断规则

1. 校验 `version`、`imei` 和租户 ID。
2. 根据租户 ID 与 `imei` 确认该 4G 模块属于当前租户，后端匹配 `device_batteries.comm_chip_id` 或 `device_batteries.imei` 字段，任一字段命中即可。
3. 查询当前租户或公共升级包中 `device_kind=3` 的 4G 模块升级包。
4. 只考虑版本号大于当前 `version` 的升级包。
5. 如果没有可升级包，返回 `need_upgrade=false`。
6. 如果只有一个更高版本升级包，返回该升级包。
7. 如果有多个更高版本升级包，只返回标记为 `is_latest=true` 的升级包。
8. 如果有多个更高版本升级包但没有任何一个标记为最新固件，返回 `need_upgrade=false`。

## 7. 无升级响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "need_upgrade": false,
    "current_version": "1.0.2",
    "is_latest": false,
    "imei": "860000000000000"
  }
}
```

常见无升级原因：

- `imei` 参数值在当前租户下的 `device_batteries.comm_chip_id` 和 `device_batteries.imei` 均不存在。
- 后台没有 4G 模块升级包。
- 后台升级包版本不大于请求版本。
- 存在多个更高版本升级包，但未标记 `是否最新固件`。

## 8. 错误响应示例

缺少租户 ID：

```json
{
  "code": 100002,
  "message": "tenant_id or X-Tenant-ID is required"
}
```

缺少参数：

```json
{
  "code": 100002,
  "message": "Key: 'GetOTA4GModuleUpgradeCheckReq.Version' Error:Field validation for 'Version' failed on the 'required' tag"
}
```

## 9. 后台配置要求

后台路径：

```text
后台管理 > BMS 管理 > OTA管理 > 升级包管理 > 4G模块升级包
```

需要配置：

- 升级包名称
- 版本号
- 升级包固件
- 说明
- 是否最新固件

当同一租户下某个 4G 模块升级包保存为 `是否最新固件=是` 时，其他 4G 模块升级包会自动取消最新标记。
