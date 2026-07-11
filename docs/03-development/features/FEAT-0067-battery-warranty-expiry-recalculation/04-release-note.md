# FEAT-0067 BMS 电池质保截止日期补偿任务 - 发布说明

- status: review
- owner: payhon
- last_updated: 2026-07-09
- related_feature: FEAT-0067
- version: v0.1.0

## 变更内容
- BMS 型号质保时长变更后，后台自动异步补偿关联电池的质保截止日期。
- BMS 型号管理页新增“补偿空质保日期”按钮，可主动扫描当前租户下空质保截止日期电池。
- 任务弹窗展示补偿进度、成功/跳过/失败统计和逐电池日志。

## 发布步骤
1. 执行 `backend/sql/63.sql`。
2. 发布后端服务。
3. 发布前端 Web。
4. 使用后台账号修改 BMS 型号质保时长并确认任务弹窗展示。
5. 手动触发“补偿空质保日期”，确认空质保截止日期电池按规则更新。

## 实际发布记录
- 2026-07-09 测试环境：已执行 `make import-sql ENV=test SQL=backend/sql/63.sql`、`make update-backend-test`、`make update-frontend-test`。SQL 与前端发布完成；后端二进制已替换并启动进程，但测试机 MQTT 认证返回 `not Authorized`，HTTP `:9999` 未监听，需先修复测试环境 MQTT 凭据后继续联调。
- 2026-07-09 生产环境：已执行 `make import-sql ENV=prod SQL=backend/sql/63.sql`、`make update-backend-prod`、`make update-frontend-prod`。`fjbms-backend` 为 `active`，`/health` 返回 200，新任务接口匿名访问返回 401，`cloud.fjiaenergy.com` 首页返回 200。

## 回滚说明
- 可回滚前后端代码后停止新任务创建。
- 已创建的任务记录只用于审计，不影响电池主数据读取。
- 如确需回滚数据表，先确认不再需要任务审计记录，再删除新增两张任务表。
