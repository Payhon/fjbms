# FEAT-0071 第三方 MES 批量重新分配 PACK 厂 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-07-28
- related_feature: FEAT-0071
- version: v0.2.0

## 1. 方案概览

- 在现有 `/api/v1/openapi/mes` 鉴权路由组中增加批量重分配接口。
- 使用独立 MES 服务实现，不调用或改变 Web 普通调拨入口，避免扩大现有角色矩阵的影响范围。
- 目标 PACK 批次级校验；设备按 SN 顺序逐台事务处理并使用数据库行锁。

## 2. 接口与数据结构

### 2.1 请求

```json
{
  "serial_numbers": ["SN001", "SN002"],
  "target_pack_factory_name": "新PACK厂家",
  "remark": "原PACK厂未启用，重新分配"
}
```

- `serial_numbers`：`required,min=1,max=500,dive,required,max=64`。
- `target_pack_factory_name`：`required,max=100`。
- `remark`：`omitempty,max=255`。

### 2.2 响应

```json
{
  "request_id": "request-id",
  "target_pack_factory_name": "新PACK厂家",
  "total": 2,
  "success": 1,
  "unchanged": 0,
  "failed": 1,
  "results": [
    {
      "serial_number": "SN001",
      "status": "REASSIGNED",
      "from_pack_factory_name": "原PACK厂家",
      "to_pack_factory_name": "新PACK厂家"
    },
    {
      "serial_number": "SN002",
      "status": "FAILED",
      "message": "设备已激活或激活状态异常，不能重新分配PACK厂"
    }
  ]
}
```

- `total` 按 Trim、去重后的唯一 SN 数量计算。
- 请求级成功使用统一 `code=200`；设备级失败仅体现在结果数组。

## 3. 关键流程

1. OpenAPI 中间件校验 AppId/SecretKey，并注入租户、操作人和 API key ID。
2. 控制器绑定请求、取得 request ID，并调用专用 MES 服务。
3. 服务按租户、名称、类型、正常状态查询目标 PACK；零条或多条均作为请求级参数错误。
4. SN Trim 后按首次出现去重并保留顺序。
5. 每台设备启动独立事务：
   - 按租户和精确 SN 查询设备；
   - 使用 `FOR UPDATE` 锁定 `device_batteries`；
   - 查询当前持有组织并确认是 PACK 厂；
   - 若两个 PACK 字段均为目标，返回 `UNCHANGED`；
   - 校验 PACK 字段一致性、激活、用户绑定、流转状态和信息补全状态；
   - 更新 `owner_org_id`、`pack_factory_org_id`、`updated_at`；
   - 写入 `device_org_transfers`；
   - 写入 `battery_operation_logs`，操作类型为 `PACK_FACTORY_REASSIGN`。
6. 单台事务错误转换为 `FAILED` 明细，继续处理后续 SN。

## 4. 安全与审计

- 设备和组织查询均带 `tenant_id`；跨租户设备返回“电池不存在”。
- 目标 PACK 必须为 `status=N`；来源 PACK 可以是禁用状态，以支持从停用机构迁出库存。
- 当前 `pack_factory_org_id` 非空且与当前持有 PACK 不一致时拒绝自动修复。
- 运营日志 `extra` 记录来源/目标组织、`source=openapi_mes`、`open_api_key_id`、`request_id` 和备注，不记录 SecretKey。
- 更新、组织转移日志和运营日志任一失败即回滚该台设备。

## 5. 并发与兼容

- 每个 SN 串行处理，避免单请求并发放大数据库压力。
- 行锁保证同一设备并发重分配只能基于最新归属判断。
- 重试时完整目标归属返回 `UNCHANGED`，不重复写日志。
- 不改变现有 MES 新增/查询接口，不改变 Web 单台/批量调拨。
- 不涉及数据库结构迁移。

## 6. 测试策略

- 服务层使用独立测试数据库覆盖目标解析、资格校验、事务、幂等、部分成功和审计。
- API 层覆盖请求绑定、上下文元数据传递和统一响应。
- 执行 Swagger 重新生成、定向 Go 测试、`go test ./...` 与 `git diff --check`。
- 联调脚本仅在显式传入重分配参数时调用高影响接口。
