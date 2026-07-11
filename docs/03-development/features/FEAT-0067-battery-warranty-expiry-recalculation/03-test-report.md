# FEAT-0067 BMS 电池质保截止日期补偿任务 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-07-09
- related_feature: FEAT-0067
- version: v0.1.0

## 测试结果
| 类型 | 结果 | 说明 |
| --- | --- | --- |
| 后端定向测试 | 通过 | `go test ./internal/service -run 'Test(UpdateBatteryBmsModelStartsWarrantyRecalcJob\|BatteryWarrantyRecalc\|ApplyBatteryWarrantyActivationTx\|AppWarrantyProfile)' -count=1` |
| 后端编译级测试 | 通过 | `go test ./internal/api ./router/apps ./internal/service -run 'Test(UpdateBatteryBmsModelStartsWarrantyRecalcJob\|BatteryWarrantyRecalc\|ApplyBatteryWarrantyActivationTx\|AppWarrantyProfile)' -count=1` |
| 前端受影响文件 ESLint | 通过 | `pnpm exec eslint src/service/api/bms.ts src/views/bms/battery/bms-model/index.vue src/views/bms/battery/modules/warranty-recalc-job-modal.vue` |
| 文案 JSON 校验 | 通过 | `zh-cn/bms.json` 与 `en-us/bms.json` 可被 `JSON.parse` 正常解析 |
| 前端全量类型检查 | 未通过（既有问题） | `pnpm exec vue-tsc --noEmit --skipLibCheck --pretty false` 输出 2284 行既有类型错误；筛选本次触及路径无命中 |
| 空白检查 | 通过 | root、backend、frontend 均执行 `git diff --check` |
| 测试环境 SQL | 通过 | `make import-sql ENV=test SQL=backend/sql/63.sql`，两张任务表与索引创建成功 |
| 测试环境后端发布 | 部分通过（环境阻塞） | `make update-backend-test` 已替换二进制并启动进程；HTTP `:9999` 未监听，日志持续 `MQTT Adapter connection failed: not Authorized`，为测试机 MQTT 认证配置问题 |
| 测试环境前端发布 | 通过 | `make update-frontend-test` 构建通过并替换 `fjbms.yz6688.cn` 站点目录；公网首页返回 200 |
| 生产环境 SQL | 通过 | `make import-sql ENV=prod SQL=backend/sql/63.sql`，两张任务表与索引创建成功 |
| 生产环境后端发布 | 通过 | `make update-backend-prod` 后 `fjbms-backend` 为 `active`，`/health` 返回 200，新任务接口匿名访问返回 401 鉴权错误 |
| 生产环境前端发布 | 通过 | `make update-frontend-prod` 构建通过并替换 `cloud.fjiaenergy.com` 站点目录；公网首页返回 200 |

## 后端覆盖场景
1. BMS 型号质保时长从空变为有效月数后，返回并启动补偿任务。
2. 同型号已激活电池的自动质保截止日期按新月数重算。
3. `warranty_manual_override=true` 的人工编辑记录不被覆盖。
4. 手动扫描只处理质保截止日期为空的电池。
5. 未激活、无激活日期、无型号、型号质保月数无效的电池被跳过并写日志。
6. 任务状态和日志按租户隔离查询。

## 环境验证备注
- 生产环境完成 SQL、后端、前端全链路发布和基础健康检查。
- 测试环境 SQL 与前端发布完成；后端二进制已更新，但启动流程阻塞在 MQTT 认证，未进入 HTTP 监听阶段。该问题与本功能代码无直接关联，需要修复测试机 EMQX 内置认证或后端 MQTT 凭据后再做后台页面联调。
