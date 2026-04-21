# FEAT-0045 调拨目标收敛与门店上级组织防泄露 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-04-21
- related_feature: FEAT-0045
- version: v0.1.0

## 1. 执行命令
- 已执行：
  - `cd backend && go test ./internal/api ./internal/service`
    - 结果：通过（`internal/api` 无测试文件；`internal/service` 通过）
  - `cd frontend && pnpm exec eslint src/views/bms/battery/list/index.vue src/views/bms/ops/operation_log/index.vue src/views/bms/org/modules/org-modal.vue`
    - 结果：通过
  - `cd frontend && pnpm build`
    - 结果：待补；本轮未拿到可确认的退出结果

## 2. 手工验证点
- 电池调拨
  - 经销商登录仅见门店目标。
  - 门店登录调拨入口不可执行，且无法打开有效弹窗。
  - 门店手工调用 `/battery/transfer` 返回拒绝。
  - 经销商手工提交非门店目标返回拒绝。
- 门店管理
  - 经销商新增门店时，上级组织只读显示当前机构且不拉组织树。
  - 管理员/厂家/PACK 新增门店仍可选择上级组织。
  - 编辑门店上级组织仍不可修改。
  - 经销商伪造 `parent_id` 创建门店被拒绝。

## 3. 风险备注
- 门店管理“防泄露”本次限定在经销商新增门店场景，其他角色仍保留树选择能力。
- 调拨矩阵与 FEAT-0028 旧文档存在历史差异，已在文档中标注被 FEAT-0045 替代。
