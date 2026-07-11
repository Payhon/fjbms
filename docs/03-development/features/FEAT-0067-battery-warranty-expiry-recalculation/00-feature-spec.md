# FEAT-0067 BMS 电池质保截止日期补偿任务 - 功能规格

- status: review
- owner: payhon
- last_updated: 2026-07-09
- related_feature: FEAT-0067
- version: v0.1.0

## 1. 背景与目标
- FEAT-0062 已在电池激活链路中按 BMS 型号质保时长生成质保截止日期。
- 存量部分电池激活时关联型号尚未配置质保时长，导致 `device_batteries.warranty_expire_date` 为空。
- 后台后续补齐型号质保时长后，需要自动补偿关联电池的质保截止日期，并允许后台主动扫描空质保截止日期电池。

## 2. 范围
### In Scope
- BMS 型号 `warranty_months` 变更为正数且发生变化后，异步重算当前租户下关联该型号的电池质保截止日期。
- BMS 型号管理页提供“补偿空质保日期”入口，手动触发当前租户全局扫描。
- 任务进度、统计和逐电池日志可查询并在后台弹窗展示。
- SQL 迁移、后端测试、前端定向校验、文档和看板同步。

### Out of Scope
- 跨租户批量运维任务。
- 质保时长按客户、批次、组织类型配置。
- 质保到期提醒、统计报表和售后工单流程。

## 3. 验收标准
1. 修改 BMS 型号质保时长为有效正数时，接口返回 `warranty_recalc_job_id`，后台自动启动补偿任务。
2. 型号变更任务会覆盖同型号电池已有自动截止日期，但不覆盖 `warranty_manual_override=true` 的人工编辑记录。
3. 手动扫描任务只处理 `warranty_expire_date IS NULL` 的电池。
4. 未激活、无激活日期、未关联 BMS 型号、型号无有效质保时长、人工覆盖记录必须跳过并记录日志。
5. 补偿成功时按 `activation_date + warranty_months` 写入 `warranty_start_date`、`warranty_months`、`warranty_expire_date`、`warranty_updated_at/by`。
6. 后台 BMS 型号管理页可触发手动扫描，并展示任务状态、成功/跳过/失败统计和日志。

## 4. 风险与约束
- 补偿任务按当前登录租户执行，不跨租户写入。
- `warranty_months <= 0` 视为未配置，不清空已有截止日期。
- 人工覆盖记录是业务保护边界，自动任务不得覆盖。

## 5. 回滚方案
- 回滚前端 BMS 型号页按钮和任务弹窗。
- 回滚后端新增接口、型号更新触发逻辑和任务服务。
- 数据库新增任务表可保留不使用；如需清理，确认无任务审计依赖后删除 `battery_warranty_recalc_jobs` 与 `battery_warranty_recalc_job_logs`。
