# FEAT-0050 电池列表新增“恢复出厂”操作 - 功能规格

- status: in_progress
- owner: payhon
- last_updated: 2026-04-28
- related_feature: FEAT-0050
- version: v0.1.0

## 1. 背景与目标
- 厂家在出厂或调拨时可能误下发到错误机构，需要把电池恢复回厂家库存后重新处理。
- 目标：
  1. 在 `后台管理 > BMS 管理 > 电池列表` 新增独立“恢复出厂”操作。
  2. 仅厂家按出厂权限口径可执行。
  3. 恢复后库存回到厂家库存语义（`owner_org_id = NULL`），并记录完整日志。

## 2. 范围
### In Scope
- 后端新增 `POST /api/v1/battery/factory_restore`。
- 仅支持单台电池恢复出厂。
- 写入 `device_org_transfers`（`from_org_id=原持有方, to_org_id=NULL`）。
- 电池操作日志新增 `FACTORY_RESTORE`。
- 前端新增生命周期“恢复出厂”入口与确认弹窗。
- 同步权限 SQL、多语言、看板与测试报告。

### Out of Scope
- 不新增批量恢复出厂。
- 不改造回退/调拨现有规则。

## 3. 验收标准
1. 厂家可将当前归属为 `PACK/DEALER/STORE` 的电池恢复出厂。
2. 已在厂家库存（`owner_org_id` 为空）时恢复出厂被拒绝。
3. 非厂家权限账号调用恢复出厂被拒绝。
4. 恢复成功后 `owner_org_id`、`device_org_transfers`、`battery_operation_logs` 三处一致。
5. 运营日志可筛选并展示 `FACTORY_RESTORE`。

## 4. 风险与约束
- “仅厂家”以后端校验为准，前端显隐仅提升体验。
- 本次沿用厂家库存空值语义，不回写固定厂家组织 ID。

## 5. 回滚方案
- 回滚前后端“恢复出厂”入口与接口实现。
- 回滚新增权限 SQL 与多语言键。
- 历史转移记录和操作日志保留，不做数据回退。
