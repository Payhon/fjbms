# FEAT-0044 电池列表回退操作 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-04-23
- related_feature: FEAT-0044
- version: v0.1.0

## 1. 已执行
- 已执行：
  - `cd backend && go test ./internal/api ./internal/service`
    - 结果：通过（`internal/api` 无测试文件；`internal/service` 通过）
  - `cd frontend && pnpm exec eslint src/views/bms/battery/list/index.vue src/views/bms/ops/operation_log/index.vue`
    - 结果：通过
  - `cd frontend && pnpm build`
    - 结果：通过（构建成功，输出 `dist`）

## 2. 需重点回归
- 经销商账号：
  - 经历 `PACK -> DEALER -> STORE -> DEALER` 后，经销商回退是否仍命中上级 PACK。
  - 即使最近一次入库来自门店，只要存在“来自上级 PACK”的历史入库记录，是否可正确回退到 PACK。
- 门店账号：
  - 上级为经销商时，能否正确回退到该经销商。
  - 上级为 PACK 时，能否正确回退到该 PACK。
- 非法场景：
  - 当前账号不是持有机构。
  - 当前机构无 `parent_id`。
  - 找不到“来自 parent_id 上级”的入库记录。
  - 上级类型非法或不在合法上级链路。
- 日志：
  - 回退成功后运营日志是否新增 `ROLLBACK`。

## 3. 风险备注
- 当前仓库缺少现成的电池生命周期自动化测试基建，本次主要依赖定向编译/静态检查和环境回归。
- 真实组织树与历史转移数据需要在联调环境进一步验证。
