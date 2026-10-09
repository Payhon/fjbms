# FEAT-0075 发布说明

- status: review
- owner: payhon
- last_updated: 2026-09-28
- related_feature: FEAT-0075
- version: v0.1.0

## 1. 发布内容与影响

后台“系统管理 → 权限管理 → 移动端权限”新增“BMS保护状态”。微信小程序、Android/iOS App 与 Web 共用 `app_device_detail_protection_status`，控制仪表盘保护状态卡片的标题、摘要、展开/收起和全部 ON/OFF 行。

未授权、加载中和请求失败时隐藏，已有账号不自动授权。顶部故障、告警、保护提示和历史记录权限保持原行为。

## 2. 升级步骤

1. 发布前备份目标数据库权限节点与机构类型授权配置。
2. 先执行幂等 `backend/sql/67.sql`，确认新节点位于已有移动端权限根下且没有自动修改授权。
3. 再更新 Web、微信小程序与 Android/iOS 客户端。
4. 管理员在需要的机构类型或 `APP_USER` 页签中勾选并保存；重新进入设备详情或刷新 Web 后生效。
5. 分别完成授权/取消、机构类型隔离、历史记录回归与各端验收后决定完成状态。

实现阶段仅交付本地代码、迁移与记录。2026-09-28 用户追加授权生产与测试环境 SQL、后台前后端更新；移动端发布、提交及推送仍不在范围内，部署结果在下节记录。

## 3. 回滚

回退本次客户端代码恢复原展示。权限节点可保留；如需清理，先备份，再仅删除新节点及配置中的该编码，保留共用根节点、历史记录和其他授权。

## 4. 已知限制

不提供运行中权限热更新；保存后需重新进入或刷新。本地行为、SQL、UniApp 类型/SFC/微信编译和 Web ESLint/构建通过；Web 显式全量类型检查仍有 1781 条既有诊断，修改前后按位置及错误编码比较无新增。真实后台及微信小程序、Android/iOS 真机验收待完成，保持 `review`。构建结果与验收结果详见 `03-test-report.md`。

## 5. 2026-09-28 部署范围与预检

- 先测试、后生产；备份权限相关表、旧 Web 产物及后端二进制，SQL 必须先于应用更新。
- 生产只执行 SQL 67；现有 `custom_name` 列与后端绑定名称修复已于 2026-09-24 部署。测试缺少该列，需先补已上线依赖 SQL 66，再执行 SQL 67。
- 本地后端 Linux/amd64 构建 SHA-256 与当前生产二进制完全一致：`a27e66e1afc2baec59f0c9dd441b03c70dc5df10c422f678358ae2881238a664`。测试使用此产物更新，生产按一致性校验决定是否需要替换。
- 测试发布前后端进程存在但未监听 9999，`/health` 无响应；需要在更新后确认恢复。生产发布前 `fjbms-backend` 为 active/running、`/health` 为 200。
- Web 类型既有错误已向用户报告；本次授权后按无新增诊断、受影响文件 ESLint、行为检查及成功构建作为局部发布依据，全量类型门禁保持未通过。

## 6. 2026-09-28 实际部署结果

- 生产 `https://cloud.fjiaenergy.com`：SQL 67 和 Web 更新完成，后端二进制与发布产物一致，保留原 PID 649159；健康接口 200，匿名权限接口 401，公网首页与权限代码文件校验一致，浏览器登录页正常。
- 测试 `https://fjbms.yz6688.cn`：先执行 SQL 66，再执行 SQL 67，后端已替换并重启，Web 更新完成；公网静态产物校验一致。测试运行验收未通过：既有 MQTT 认证失败使 HTTP 未启动，API 仍为 502，等待确认 fjbms 测试专用 MQTT 配置。
- 两环境的新节点唯一，原有机构类型授权及设备绑定数据均保持不变；没有自动添加保护状态授权。
- 微信小程序、Android/iOS 本次未发布，已上线旧客户端的展示行为需在移动端更新后才遵循新开关。后台实际授权/取消及移动端真机验收尚待完成，状态保持 `review`；未提交或推送。

| 备份 | 生产 | 测试 |
| --- | --- | --- |
| 权限表数据库备份 | `/www/fjia/backups/fjbms/backend/feat0075-20260928_141309/permissions.dump` | `/panel/project/fjiacloud/backup/backend/feat0075-20260928_141309/permissions.dump`（包含测试 SQL 66 涉及的绑定表） |
| 旧二进制 | 同目录 `fjbms.before-update` | 同目录 `fjbms.before-update` |
| 旧 Web | `/www/fjia/backups/fjbms/frontend/frontend_20260928_141309.tar.gz` | `/panel/project/fjiacloud/backup/frontend/frontend_20260928_141309.tar.gz` |

全部备份已验证可读取，校验和和发布产物记录在 [deployment-verification.json](/Users/payhon/work2025/project/fjbms/docs/03-development/features/FEAT-0075-bms-protection-status-permission/evidence/deployment-verification.json)。回滚时使用对应环境的 Web 归档；测试如需回退后端，使用旧二进制，保留运行配置。SQL 66 为已上线后端依赖，不因本功能回滚删除列；SQL 67 节点可保留，删除仅按第 3 节执行，不覆盖生产现有授权配置。
