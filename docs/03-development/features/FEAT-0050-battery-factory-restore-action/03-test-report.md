# FEAT-0050 电池列表新增“恢复出厂”操作 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-04-28
- related_feature: FEAT-0050
- version: v0.1.0

## 1. 建议执行命令
- `cd backend && go test ./internal/api ./internal/service`
- `cd frontend && pnpm exec eslint src/views/bms/battery/list/index.vue src/views/bms/ops/operation_log/index.vue`
- `cd frontend && pnpm build`

## 2. 重点回归
- 厂家账号恢复出厂：
  - 当前归属 `PACK/DEALER/STORE` 成功恢复。
  - 当前已在厂家库存被拒绝。
- 租户管理员显示口径：
  - `TENANT_ADMIN / SYS_ADMIN` 登录时，在 `owner_org_id` 非空的电池行可见“恢复出厂”入口。
- 权限校验：
  - 非厂家账号调用接口被拒绝。
- 落账一致性：
  - `owner_org_id` 置空；
  - `device_org_transfers` 新增 `to_org_id=NULL`；
  - `battery_operation_logs` 新增 `FACTORY_RESTORE`。
- 前端交互：
  - 生命周期入口显示正确；
  - 弹窗信息正确；
  - 成功后列表刷新；
  - 运营日志筛选可见 `FACTORY_RESTORE`。
