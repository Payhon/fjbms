# FEAT-0044 电池列表回退操作 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-04-21
- related_feature: FEAT-0044
- version: v0.1.0

## 1. 已执行
- 待补充本次定向命令执行结果：
  - `cd backend && go test ./internal/api ./internal/service`
  - `cd frontend && pnpm exec eslint src/views/bms/battery/list/index.vue src/views/bms/ops/operation_log/index.vue`
  - `cd frontend && pnpm build`

## 2. 需重点回归
- 经销商账号：
  - 自有库存来源为 PACK 时，能否正确显示并回退。
- 门店账号：
  - 自有库存来源为经销商时，能否正确显示并回退。
- 非法场景：
  - 当前账号不是持有机构。
  - 历史记录中找不到最近一次入库来源。
  - 来源机构已删除或不在合法上级链路。
- 日志：
  - 回退成功后运营日志是否新增 `ROLLBACK`。

## 3. 风险备注
- 当前仓库缺少现成的电池生命周期自动化测试基建，本次主要依赖定向编译/静态检查和环境回归。
- 真实组织树与历史转移数据需要在联调环境进一步验证。
