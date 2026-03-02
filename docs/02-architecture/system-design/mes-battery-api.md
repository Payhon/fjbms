# MES 电池开放 API（第三方）

- status: approved
- owner: <owner>
- last_updated: 2026-02-14
- source: `doc/第三方MES电池API说明.md`
- version: v1.0.0

## 1. 文档目标与适用范围
- 本文用于说明第三方 MES 对接 FJBMS 的电池开放接口。
- 适用对象：MES 对接开发、后端接口维护人员、联调测试人员。
- 当前覆盖接口：密钥管理、单个电池新增、按序列号查询。

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
- 说明：请求体参数与后台“单个电池新增”保持一致。

请求体示例：

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

## 6. 按序列号查询电池信息
- 方法与路径：`GET /api/v1/openapi/mes/battery/{serial_number}`

请求示例：

```bash
curl -X GET "http://localhost:9999/api/v1/openapi/mes/battery/SN202602130001" \
  -H "x-app-id: app_xxx" \
  -H "x-secret-key: sk_xxx"
```

返回信息包含设备编号、型号、蓝牙 MAC、生产日期、质保到期、激活状态、在线状态等。

## 7. 响应约定
- 通用格式：`{ code, message, data }`
- 约定：`code = 0` 表示成功，非 0 表示失败。

## 8. 维护说明
- 本文是迁移后的主维护文档；旧文档保留在 `doc/` 目录作为历史副本。
- 若接口字段或鉴权流程变更，需同步更新：
  - 本文档
  - `docs/04-project-tracking/board.md`
  - `docs/04-project-tracking/risks-and-blockers.md`（如有风险变化）
