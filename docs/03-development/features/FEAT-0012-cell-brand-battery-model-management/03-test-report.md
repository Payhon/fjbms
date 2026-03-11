# FEAT-0012 电芯品牌与电池型号管理（租户维度）- 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-03-10
- related_feature: FEAT-0012
- version: v0.1.0

## 1. 测试范围
- 电芯品牌 CRUD（租户隔离、唯一性、序号范围、名称长度）。
- 电池型号 CRUD（机构隔离、唯一性、序号范围）。
- BMS 型号 CRUD（`battery_bms_models`，租户维度）。
- 前端单页行内操作体验（无分页/无弹窗）。
- 电池列表按钮文案更新（新增BMS）。

## 2. 测试结果
- `backend`: `go test ./internal/... ./router/... ./router/apps/...`
  - 结果：通过（含 `internal/service`、`router/apps` 编译与测试通过）。
- `backend`: `go test ./...`
  - 结果：**部分通过**，`project/test` 因本地环境未配置（`未知环境`）失败，其余包通过。
- `frontend`: `pnpm typecheck`
  - 结果：通过。
- `frontend`: `pnpm exec eslint src/views/bms/battery/bms-model/index.vue src/views/bms/battery/modules/battery-model-modal.vue src/service/api/bms.ts src/router/elegant/routes.ts src/router/elegant/imports.ts src/router/elegant/transform.ts src/router/routes/index.ts`
  - 结果：无 error / warning。
- `backend`: `go test ./internal/model ./internal/api`
  - 结果：通过（覆盖本次 `/api/v1/org` 请求结构调整后的编译校验）。
- `backend`: `go test ./internal/service`
  - 结果：通过（覆盖“新增 BMS”按 BMS 型号解析的服务层编译校验）。
- `frontend`: `pnpm typecheck`
  - 结果：通过（覆盖“新增 BMS”弹窗型号下拉改为 `battery_bms_models` 后的模板/类型校验）。

## 3. 问题清单
- `backend/test` 依赖本地数据库环境配置，当前未在本机配置完成，导致全量测试无法全绿。
