# FEAT-0044 电池列表回退操作 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-04-23
- related_feature: FEAT-0044
- version: v0.1.0

## 2026-04-21
1. 在 `backend/internal/model/battery_ops.http.go` 新增回退预览/执行请求响应模型。
2. 在 `backend/router/apps/battery.go` 与 `backend/internal/api/battery.go` 新增：
   - `GET /api/v1/battery/rollback/preview`
   - `POST /api/v1/battery/rollback`
3. 在 `backend/internal/service/battery_lifecycle.go` 新增共享回退解析逻辑，统一服务于预览与正式执行。
4. 回退执行事务内补写 `device_org_transfers` 与 `battery_operation_logs`，并新增日志类型 `ROLLBACK`。
5. 前端 `frontend/src/views/bms/battery/list/index.vue` 新增：
   - 生命周期“回退”菜单项
   - 回退预览调用
   - 独立确认弹窗
6. `frontend/src/views/bms/ops/operation_log/index.vue` 新增 `ROLLBACK` 筛选项。
7. 补充权限与多语言：
   - `backend/sql/50.sql`
   - `backend/sql/40.sql`
   - `backend/sql/1.sql`
   - `frontend/src/locales/langs/zh-cn/route.json`
   - `frontend/src/locales/langs/en-us/route.json`
8. 新增 FEAT-0044 文档目录并更新项目看板。

## 2026-04-23
1. 修正回退目标解析逻辑：由“最近来源”改为“直系上级（parent_id）+ 来自该上级的最近入库记录”。
2. 放开门店上级类型校验：门店回退目标上级支持 `DEALER` 或 `PACK_FACTORY`。
3. 更新回退失败提示文案：
   - `未配置上级机构，无法回退`
   - `未找到来自上级机构的可回退记录`
   - `门店仅支持回退到上级经销商或PACK厂`
