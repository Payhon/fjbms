# FEAT-0071 第三方 MES 批量重新分配 PACK 厂 - 实施日志

- status: review
- owner: payhon
- last_updated: 2026-07-28
- related_feature: FEAT-0071
- version: v0.2.0

## 2026-07-28

- 已完成需求确认：请求不包含原 PACK 厂名称，来源以后端当前归属为准。
- 已完成规格与技术设计评审，进入开发阶段。
- 新增 `POST /api/v1/openapi/mes/battery/reassign-pack-factory`，复用现有 MES AppId/SecretKey 鉴权、租户和 API key 上下文。
- 新增专用请求/响应模型与 MES 重分配服务：SN Trim 去重、500 条上限、目标 PACK 批次级精确唯一校验、逐台事务和部分成功汇总。
- 单台事务使用行锁读取当前设备及电池归属，后端解析来源 PACK；校验当前 PACK、激活状态、所有者绑定、流转状态、PACK 信息补全和两个归属字段一致性。
- 成功时原子更新 `owner_org_id`、`pack_factory_org_id`、`updated_at`，并写入 `device_org_transfers` 与 `PACK_FACTORY_REASSIGN` 操作日志。
- 操作日志额外信息统一编码为 JSON，确保来源/目标、OpenAPI key ID、request ID 和备注可落库；审计失败会使当前设备事务回滚。
- 补充请求绑定、目标组织、部分成功、跨租户、未出厂、异常状态、幂等、审计回滚及并发重复请求测试。
- 重新生成 Swagger；由于当前代码中的 `json.RawMessage` 无法被普通 `swag init` 解析，增加 `.swaggo` 类型覆盖后恢复标准生成命令。
- 更新主 MES API 文档、用户指定历史副本、后端第三方接入指南和联调脚本；联调脚本只有显式提供 SN 与目标 PACK 时才执行重分配。
- 接入指南中的 AppId/SecretKey 明文已替换为占位符；未自动撤销或轮换外部密钥。
- 不新增 SQL 迁移，不修改 Web、移动端或既有普通调拨接口。
