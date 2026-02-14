# 第三方 MES 电池 API 说明

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
