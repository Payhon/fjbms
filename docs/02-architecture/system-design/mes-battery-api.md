# MES 电池开放 API（第三方）

- status: approved
- owner: <owner>
- last_updated: 2026-07-28
- source: `doc/第三方MES电池API说明.md`
- version: v1.1.0

## 1. 文档目标与适用范围
- 本文用于说明第三方 MES 对接 FJBMS 的电池开放接口。
- 适用对象：MES 对接开发、后端接口维护人员、联调测试人员。
- 当前覆盖接口：密钥管理、单个电池新增、按序列号查询、批量重新分配 PACK 厂。

## 2. 版本与基础路径
- 接口版本：`v1`
- 基础前缀：`/api/v1`
- 第三方 MES 相关接口前缀：`/api/v1/openapi/mes`

## 3. 鉴权机制
第三方接口采用 Header 鉴权，所有开放接口都需要携带：

- `x-app-id: {app_id}`
- `x-secret-key: {secret_key}`

密钥来源：后台 `系统管理 -> API密钥管理`（管理接口 `POST/GET /api/v1/open/keys`）。

## 4. API 密钥管理（后台）

### 4.1 关键字段
- `app_id`：第三方调用标识（数据库字段 `api_key`）
- `secret_key`：第三方调用密钥
- `remark`：备注
- `expired_at`：有效期截止时间
- `tenant_id`：租户 ID（租户创建时自动初始化一组默认密钥）

### 4.2 创建密钥
- 方法与路径：`POST /api/v1/open/keys`

请求体示例：

```json
{
  "tenant_id": "d616bcbb",
  "remark": "MES生产线A",
  "expired_at": "2027-02-13 23:59:59"
}
```

响应示例：

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

## 5. 新增电池
- 方法与路径：`POST /api/v1/openapi/mes/battery`
- 鉴权：`x-app-id` + `x-secret-key`
- 说明：请求体参数与后台“单个电池新增”保持一致；可选字段 `pack_factory_name` 用于按租户内 `PACK_FACTORY` 机构名称自动出厂。

请求体示例：

```json
{
  "item_uuid": "SN202602130001",
  "batch_number": "BATCH-001",
  "product_spec": "51.2V100Ah",
  "order_number": "MES-PO-20260213",
  "bms_comm_type": 1,
  "battery_model_name": "FJBMS-100A",
  "pack_factory_name": "示例PACK厂家",
  "production_date": "2026-02-13",
  "warranty_expire_date": "2027-02-13"
}
```

## 6. 按序列号查询电池信息
- 方法与路径：`GET /api/v1/openapi/mes/battery/{serial_number}`

请求示例：

```bash
curl -X GET "http://localhost:9999/api/v1/openapi/mes/battery/SN202602130001" \
  -H "x-app-id: app_xxx" \
  -H "x-secret-key: sk_xxx"
```

返回信息包含设备编号、型号、蓝牙 MAC、生产日期、质保到期、激活状态、在线状态等。

## 7. 批量重新分配 PACK 厂

- 方法与路径：`POST /api/v1/openapi/mes/battery/reassign-pack-factory`
- 鉴权：`x-app-id` + `x-secret-key`
- 说明：将尚未投入使用、当前属于 PACK 厂的 BMS 板批量重新分配给目标 PACK 厂。请求不需要原 PACK 厂名称，来源以后端当前归属为准。

请求字段：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `serial_numbers` | string[] | 是 | 电池序列号，1～500 条；Trim 后按首次出现去重 |
| `target_pack_factory_name` | string | 是 | 目标 PACK 厂名称，租户内精确唯一匹配且机构状态正常 |
| `remark` | string | 否 | 操作备注，最大 255 字符 |

请求示例：

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

成功响应示例：

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

处理规则：

- 单台状态为 `REASSIGNED`、`UNCHANGED` 或 `FAILED`。
- 每台设备独立事务，允许部分成功；全部设备级失败时请求仍返回 `code=200`，失败原因在 `results` 中。
- `owner_org_id` 和 `pack_factory_org_id` 已同时属于目标 PACK 时返回 `UNCHANGED`，不会重复写转移日志。
- 已激活、已绑定用户、已进入后续流转或已完成 PACK 信息补全的设备不能重新分配。
- 跨租户设备按不存在处理。

## 8. 响应约定

- 通用格式：`{ code, message, data }`
- 约定：`code = 200` 表示请求成功，非 200 表示请求级失败。
- 批量接口中的单台失败通过 `data.results[].status=FAILED` 表示。

## 9. 维护说明
- 本文是迁移后的主维护文档；旧文档保留在 `doc/` 目录作为历史副本。
- 若接口字段或鉴权流程变更，需同步更新：
  - 本文档
  - `docs/04-project-tracking/board.md`
  - `docs/04-project-tracking/risks-and-blockers.md`（如有风险变化）
