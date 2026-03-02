# FEAT-0002 历史文档迁移与分层重构 - 实施日志

- status: done
- owner: <owner>
- last_updated: 2026-02-14
- related_feature: FEAT-0002
- version: v0.1.0

## 日志
1. 建立迁移清单文档：`docs/04-project-tracking/doc-migration-checklist.md`。
2. 更新项目看板，新增 FEAT-0002 并标记为 `in_progress`。
3. 增加 PR 模板中的文档治理检查项，确保后续迁移流程可执行。
4. 完成 P0 首篇迁移：`doc/第三方MES电池API说明.md` -> `docs/02-architecture/system-design/mes-battery-api.md`。
5. 在历史源文档中加入迁移提示，避免双份文档并行维护。
6. 完成 P0 批次迁移：`doc/app-auth-api.md` -> `docs/02-architecture/system-design/app-auth-api.md`。
7. 完成 P0 批次迁移：`doc/app-content-api.md` -> `docs/02-architecture/system-design/app-content-api.md`。
8. 完成 P0 批次迁移：`doc/系统架构文档.md` -> `docs/02-architecture/system-design/system-architecture.md`。
9. 完成 P0 批次迁移：`doc/系统架构图.md` -> `docs/02-architecture/system-design/architecture-diagrams.md`。
10. 完成 P0 批次迁移：`doc/数据库结构文档.md` -> `docs/02-architecture/data-model/database-schema.md`。
11. 完成 P0 批次迁移：`doc/部署说明.md` -> `docs/05-operations/deployment/deployment-guide.md`。
12. 完成 P0 批次迁移：`doc/快速测试指南.md` -> `docs/05-operations/runbook/quick-test-runbook.md`。
13. 完成 P0 批次迁移：`doc/emqx_http_auth.md` -> `docs/02-architecture/security/emqx-http-auth.md`。
14. 完成 P0 批次迁移：`doc/app_ws_and_backend_mqtt_auth.md` -> `docs/02-architecture/security/ws-mqtt-auth.md`。
15. 完成 P1 批次迁移：开发指南/需求方案/路线图（`backend-guide.md`、`frontend-guide.md`、`solution-overview.md`、`secondary-development-requirements.md`、`development-plan.md`）。
16. 完成 P1 批次迁移：`doc/开发进度.md` 合并入 `docs/04-project-tracking/milestones.md` 历史进度章节。
17. 完成 P1 批次迁移：测试用例与协议文档（`orgtree-test-cases.md`、`device-comm-basic-guide.md`、`protocol-source/*`）。
18. 完成 P2 批次归档：阶段性报告迁移到 `docs/04-project-tracking/archive/`。
19. 完成 P2 批次归档：`doc/README.md` 增加“历史存档说明”，`docs/README.md` 更新迁移状态。
20. FEAT-0002 看板状态更新为 `done`，迁移清单 P0/P1/P2 全部勾选完成。
