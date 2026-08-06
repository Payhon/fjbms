# FEAT-0071 第三方 MES 批量重新分配 PACK 厂 - 发布说明

- status: review
- owner: payhon
- last_updated: 2026-07-28
- related_feature: FEAT-0071
- version: v0.2.0

## 1. 发布内容

- 新增 MES 批量重新分配 PACK 厂接口：
  - `POST /api/v1/openapi/mes/battery/reassign-pack-factory`
  - 请求仅需电池 SN 列表、目标 PACK 厂名称和可选备注，不需要原 PACK 厂名称。
  - 最多 500 条，按 Trim 后唯一 SN 逐台处理，支持部分成功与安全重试。
- 来源 PACK 始终由后端当前归属解析；成功项同时更新当前持有方与 PACK 组装方。
- 新增 `PACK_FACTORY_REASSIGN` 审计类型，记录来源、目标、MES OpenAPI、API key ID、request ID 和备注。
- 更新 Swagger、MES 主文档、历史副本、第三方接入指南和显式重分配联调模式。

## 2. 影响范围

- 后端 MES OpenAPI、Swagger、第三方接入文档和联调脚本。
- 不涉及数据库迁移、Web 或移动端发布。
- 不改变已有 MES 新增/查询接口及 Web 普通调拨行为。

## 3. 发布前检查

- 使用测试环境专用 MES 密钥验证成功、混合失败、全部失败和超时重试。
- 查询成功项并确认新持有 PACK 回显正确。
- 对曾出现在接入资料中的外部 AppId/SecretKey 执行管理员侧轮换；代码不会自动撤销密钥。
- 完成测试环境验收后再将 FEAT-0071 从 `review` 转为 `done`。

## 4. 回滚

- 回滚 FEAT-0071 新接口和专用服务。
- 已完成的业务转移不自动回退。
- 如需恢复已转移设备，使用既有人工生命周期流程处理，不直接修改数据库归属字段。
