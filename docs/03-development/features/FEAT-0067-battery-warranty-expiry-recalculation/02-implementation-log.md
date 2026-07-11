# FEAT-0067 BMS 电池质保截止日期补偿任务 - 实施日志

- status: review
- owner: payhon
- last_updated: 2026-07-09
- related_feature: FEAT-0067
- version: v0.1.0

## 2026-07-09
1. 新增 `backend/sql/63.sql`，创建质保补偿任务表和任务日志表。
2. 后端新增质保补偿任务服务，支持 `MODEL_CHANGE` 和 `MANUAL_SCAN` 两类任务。
3. BMS 型号更新接口在质保时长变更为有效正数后创建补偿任务，并在响应中返回 `warranty_recalc_job_id`。
4. 新增后台手动扫描接口、任务状态接口和任务日志接口。
5. Web BMS 型号管理页新增“补偿空质保日期”按钮和任务进度弹窗。
6. 补齐中英文文案、FEAT 文档和看板记录。
