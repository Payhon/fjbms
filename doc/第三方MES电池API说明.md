# 第三方 MES 电池 API 说明

> ⚠️ 本文为历史副本。当前维护版本：`docs/02-architecture/system-design/mes-battery-api.md`。

## 1. API 密钥管理（后台）

- 菜单位置：`系统管理 -> API密钥管理`
- 管理接口：`/api/v1/open/keys`
- 核心字段：
  - `app_id`：第三方调用标识（数据库字段 `api_key`）
  - `secret_key`：第三方调用密钥
  - `remark`：备注
  - `expired_at`：有效期截止时间
  - `tenant_id`：租户 ID（租户创建时自动初始化一组默认密钥）

### 1.1 创建密钥

- `POST /api/v1/open/keys`
- 请求体示例：

```json
{
  "tenant_id": "d616bcbb",
  "remark": "MES生产线A",
  "expired_at": "2027-02-13 23:59:59"
}
```

- 响应示例：

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": "4e084f0d-7f59-4ca4-acd8-8a61643d803e",
    "tenant_id": "d616bcbb",
    "app_id": "app_4be0a5de2a67ac8ee6c2d7ef",
    "secret_key": "sk_************************",
    "remark": "MES生产线A",
    "expired_at": "2027-02-13T15:59:59Z",
    "status": 1
  }
}
```

## 2. 第三方认证方式

第三方接口使用 Header 认证：

- `x-app-id: {app_id}`
- `x-secret-key: {secret_key}`

## 3. 第三方新增电池

- `POST /api/v1/openapi/mes/battery`
- 鉴权：`x-app-id` + `x-secret-key`
- 请求体（与后台单个电池新增参数一致）：

```json
{
  "item_uuid": "SN202602130001",
  "batch_number": "BATCH-001",
  "product_spec": "51.2V100Ah",
  "order_number": "MES-PO-20260213",
  "bms_comm_type": 1,
  "battery_model_name": "FJBMS-100A",
  "production_date": "2026-02-13",
  "warranty_expire_date": "2027-02-13"
}
```

## 4. 根据序列号查询电池信息

- `GET /api/v1/openapi/mes/battery/{serial_number}`
- 示例：

```bash
curl -X GET "http://localhost:9999/api/v1/openapi/mes/battery/SN202602130001" \
  -H "x-app-id: app_xxx" \
  -H "x-secret-key: sk_xxx"
```

返回字段包含设备编号、型号、蓝牙 MAC、生产日期、质保到期、激活状态、在线状态等信息。

## 5. 批量重新分配 PACK 厂

> 主维护说明见：`docs/02-architecture/system-design/mes-battery-api.md`。

- `POST /api/v1/openapi/mes/battery/reassign-pack-factory`
- 鉴权：`x-app-id` + `x-secret-key`
- 用途：将尚未投入使用、当前属于 PACK 厂的 BMS 板重新分配给目标 PACK 厂。
- 请求不需要原 PACK 厂名称，来源以后端当前归属为准。

### 5.1 请求字段

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `serial_numbers` | string[] | 是 | 电池 SN，1～500 条；每项 Trim 后按首次出现去重，查询保持大小写敏感 |
| `target_pack_factory_name` | string | 是 | 目标 PACK 厂名称，在密钥所属租户内精确唯一匹配且机构状态正常 |
| `remark` | string | 否 | 操作备注，最大 255 字符 |

请求不包含原 PACK 厂字段，客户端不能指定或覆盖来源机构。

### 5.2 curl 示例

```bash
curl -X POST "https://example.com/api/v1/openapi/mes/battery/reassign-pack-factory" \
  -H "Content-Type: application/json" \
  -H "x-app-id: app_xxx" \
  -H "x-secret-key: sk_xxx" \
  -d '{
    "serial_numbers": ["SN202602130001", "SN202602130002"],
    "target_pack_factory_name": "新PACK厂家",
    "remark": "原PACK厂未启用，重新分配"
  }'
```

### 5.3 响应示例

```json
{
  "code": 200,
  "message": "Success",
  "data": {
    "request_id": "request-id",
    "target_pack_factory_name": "新PACK厂家",
    "total": 2,
    "success": 1,
    "unchanged": 0,
    "failed": 1,
    "results": [
      {
        "serial_number": "SN202602130001",
        "status": "REASSIGNED",
        "from_pack_factory_name": "原PACK厂家",
        "to_pack_factory_name": "新PACK厂家"
      },
      {
        "serial_number": "SN202602130002",
        "status": "FAILED",
        "to_pack_factory_name": "新PACK厂家",
        "message": "设备已激活或激活状态异常，不能重新分配PACK厂"
      }
    ]
  }
}
```

### 5.4 处理与幂等规则

- `total` 按 Trim、去重后的唯一 SN 数量计算，结果保持首次输入顺序。
- 逐台状态固定为 `REASSIGNED`、`UNCHANGED`、`FAILED`。
- 每台设备使用独立事务，单台失败不会回滚其他已成功设备；即使全部逐台失败，请求仍返回成功受理汇总。
- `owner_org_id` 与 `pack_factory_org_id` 已同时等于目标 PACK 时返回 `UNCHANGED`，不会重复更新或写转移日志，适合超时后重试。
- 跨租户 SN 按不存在处理，不返回其他租户的设备或组织信息。
- 目标 PACK 不存在、重名、禁用、类型不符，或请求字段不合法时属于请求级错误。
- 仅允许当前持有方为 PACK 厂、未激活、未绑定当前所有者、流转状态为空或 `FACTORY`，且尚未补全 PACK 电芯品牌/电池型号信息的设备。
- `owner_org_id` 与非空 `pack_factory_org_id` 指向不同 PACK 厂时拒绝处理，不自动修复脏数据。

成功时平台同时更新当前持有方和 PACK 组装方，并记录组织转移日志及 `PACK_FACTORY_REASSIGN` 电池操作审计。来源 PACK 名称由后端解析并通过 `from_pack_factory_name` 返回。
