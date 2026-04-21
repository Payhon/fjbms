# FEAT-0045 调拨目标收敛与门店上级组织防泄露 - 实施日志

- status: in_progress
- owner: payhon
- last_updated: 2026-04-21
- related_feature: FEAT-0045
- version: v0.1.0

## 2026-04-21
1. `frontend/src/views/bms/battery/list/index.vue`
   - 调整调拨目标类型：经销商仅门店，门店无目标类型。
   - 门店账号调拨入口保留但禁用，点击给出“无可调拨下级机构”提示。
   - 打开调拨弹窗前增加空目标类型阻断。
2. `backend/internal/service/battery_lifecycle.go`
   - `TransferBattery` 删除经销商到 PACK 分支。
   - 门店分支改为直接拒绝调拨。
3. `frontend/src/views/bms/org/modules/org-modal.vue`
   - 新增经销商新增门店场景判定与默认 `parent_id` 注入。
   - 上级组织改为只读展示，且该场景不再请求组织树。
4. `backend/internal/service/org.go`
   - `CreateOrg` 增加经销商创建门店时 `parent_id == claims.OrgID` 强校验。
5. 新建 FEAT-0045 文档目录并同步看板。
6. 更新 FEAT-0028 文档，标注旧调拨矩阵已被 FEAT-0045 收口替代。
7. 完成定向校验：
   - `cd backend && go test ./internal/api ./internal/service`（通过）
   - `cd frontend && pnpm exec eslint src/views/bms/battery/list/index.vue src/views/bms/ops/operation_log/index.vue src/views/bms/org/modules/org-modal.vue`（通过）
   - `cd frontend && pnpm build`（本轮未拿到可确认的退出结果，待补）
