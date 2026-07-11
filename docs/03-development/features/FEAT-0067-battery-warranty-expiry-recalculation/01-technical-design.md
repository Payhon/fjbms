# FEAT-0067 BMS 电池质保截止日期补偿任务 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-07-09
- related_feature: FEAT-0067
- version: v0.1.0

## 1. 方案概览
- 新增 `battery_warranty_recalc_jobs` 和 `battery_warranty_recalc_job_logs`，复用电池导入任务的异步执行、状态轮询和日志展示模式。
- BMS 型号更新接口在保存 `warranty_months` 后创建 `MODEL_CHANGE` 任务，事务提交后启动 goroutine。
- 后台手动入口创建 `MANUAL_SCAN` 任务，扫描当前租户下空质保截止日期电池。
- 任务服务逐条处理候选电池，成功、跳过、失败均写入任务日志。

## 2. 数据结构
- `battery_warranty_recalc_jobs`
  - `source`: `MODEL_CHANGE` / `MANUAL_SCAN`
  - `scope_model_id`: 型号变更任务的 BMS 型号 ID，手动扫描为空
  - `status`: `PENDING` / `RUNNING` / `SUCCESS` / `FAILED`
  - `total_rows`、`processed_rows`、`success_rows`、`skipped_rows`、`failed_rows`
  - `started_at`、`finished_at`、`created_at`、`updated_at`
- `battery_warranty_recalc_job_logs`
  - `job_id`、`tenant_id`、`level`
  - `device_id`、`device_number`、`battery_model_id`
  - `message`、`created_at`

## 3. 接口
- `PUT /api/v1/battery/bms-model/:id`
  - 响应增加可选 `warranty_recalc_job_id`。
- `POST /api/v1/battery/warranty/recalculate-jobs`
  - 创建当前租户手动扫描任务。
- `GET /api/v1/battery/warranty/recalculate-jobs/:id`
  - 查询任务状态。
- `GET /api/v1/battery/warranty/recalculate-jobs/:id/logs?after_id=&limit=`
  - 增量查询任务日志。

## 4. 关键规则
1. 型号变更任务只在 `warranty_months` 变为正数且相对旧值发生变化时创建。
2. 所有任务均按 `devices.tenant_id` 限定当前租户。
3. 型号变更任务候选集为关联该 BMS 型号的所有电池；手动扫描候选集为 `warranty_expire_date IS NULL` 的电池。
4. 自动任务跳过 `warranty_manual_override=true`、未激活、无激活日期、无型号、型号质保时长无效的记录。
5. 更新时再次带上人工覆盖保护条件，避免并发人工编辑被自动任务覆盖。

## 5. 前端
- BMS 型号管理页新增“补偿空质保日期”按钮。
- 新增任务弹窗，展示任务 ID、状态、进度条、成功/跳过/失败统计和日志表格。
- 型号编辑保存后如返回 `warranty_recalc_job_id`，自动打开任务弹窗。

## 6. 测试策略
- 后端定向单测覆盖型号变更触发、自动值覆盖、人工覆盖保护、手动扫描空值、跳过规则、任务状态/日志和跨租户不可见。
- 前端执行受影响文件 ESLint 和类型检查。
