# FEAT-0012 BMS 历史数据查询与异步导出通知 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-03-09
- related_feature: FEAT-0012
- version: v0.1.0

## 1. 测试范围
- 后端：属性历史写入、历史查询 long/wide、导出任务状态流转、下载状态更新、越权拦截。
- 前端：页面布局交互、长宽表切换、异步导出提示、WS 通知提醒与下载移除。

## 2. 结果
- [x] `cd backend && go test ./internal/service ./internal/api ./internal/storage ./pkg/global ./router/apps ./initialize ./internal/middleware`
  - 结果：通过（2026-03-09）。
- [ ] `cd backend && go test ./...`
  - 结果：失败（已知环境依赖问题，`backend/test/pg_test.go` 报“未知环境”并触发 DB nil panic，非本功能回归引入）。
- [x] `cd frontend && pnpm typecheck`
  - 结果：通过（2026-03-09）。
- [ ] `cd frontend && pnpm lint`
  - 结果：未执行全量（仓库存在大量历史 lint 存量问题，不作为 FEAT-0012 阻塞项）。
- [x] `cd frontend && pnpm eslint src/views/bms/battery/history/index.vue src/layouts/modules/global-header/components/export-message-center.vue src/hooks/business/use-bms-history-export-notice.ts src/utils/common/ui-permission.ts src/layouts/modules/global-header/index.vue src/service/api/bms.ts src/router/routes/index.ts --max-warnings=0`
  - 结果：通过（2026-03-09）。
- [ ] 手工链路：创建任务 -> 完成通知 -> 消息提醒 -> 下载 -> 列表移除
  - 结果：待联调环境执行。

## 3. 风险记录
- 宽表列数量依赖时间窗口与设备上报维度，建议验收时覆盖高维 key 设备。
- WebSocket 弱网重连需观察稳定性与重复消息处理。
- `go test ./...` 依赖本地数据库与 `run_env` 配置，需在联调环境按测试说明补齐。
