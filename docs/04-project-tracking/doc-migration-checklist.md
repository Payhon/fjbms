# 历史文档迁移清单（`doc/` -> `docs/`）

- 负责人：<owner>
- 关联事项：`FEAT-0002`
- 当前状态：`done`
- 最后更新：2026-02-14

## 迁移规则
1. 先迁移（复制）到 `docs/`，评审后再把 `doc/` 标记为归档，避免信息丢失。
2. 每完成一篇文档迁移，更新本清单与 `board.md`。
3. 跨模块文档优先放在架构层（`docs/02-architecture/`）并在正文声明适用模块。

## 优先级批次
- P0（已完成）：对外接口、系统架构、数据库、部署与测试入口。
- P1（已完成）：开发指导、计划与进度文档。
- P2（已完成）：阶段性报告、历史草案和重复文档归档。

## 迁移明细

| 状态 | 优先级 | 历史文档（源） | 目标路径（新） | 处理策略 |
|---|---|---|---|---|
| [x] | P0 | `doc/第三方MES电池API说明.md` | `docs/02-architecture/system-design/mes-battery-api.md` | 已迁移，补充版本与鉴权章节（2026-02-14） |
| [x] | P0 | `doc/app-auth-api.md` | `docs/02-architecture/system-design/app-auth-api.md` | 已迁移，整理请求头/场景/接口分组（2026-02-14） |
| [x] | P0 | `doc/app-content-api.md` | `docs/02-architecture/system-design/app-content-api.md` | 已迁移，整理 lang/反馈上传/登录态约定（2026-02-14） |
| [x] | P0 | `doc/系统架构文档.md` | `docs/02-architecture/system-design/system-architecture.md` | 已迁移，补充治理元数据（2026-02-14） |
| [x] | P0 | `doc/系统架构图.md` | `docs/02-architecture/system-design/architecture-diagrams.md` | 已迁移，独立维护架构图与流图（2026-02-14） |
| [x] | P0 | `doc/数据库结构文档.md` | `docs/02-architecture/data-model/database-schema.md` | 已迁移，保留表结构主文档（2026-02-14） |
| [x] | P0 | `doc/部署说明.md` | `docs/05-operations/deployment/deployment-guide.md` | 已迁移，新增敏感配置占位提示（2026-02-14） |
| [x] | P0 | `doc/快速测试指南.md` | `docs/05-operations/runbook/quick-test-runbook.md` | 已迁移，归入 runbook（2026-02-14） |
| [x] | P0 | `doc/emqx_http_auth.md` | `docs/02-architecture/security/emqx-http-auth.md` | 已迁移，归入安全文档（2026-02-14） |
| [x] | P0 | `doc/app_ws_and_backend_mqtt_auth.md` | `docs/02-architecture/security/ws-mqtt-auth.md` | 已迁移，归入安全文档（2026-02-14） |
| [x] | P1 | `doc/后端开发指导文档.md` | `docs/03-development/guides/backend-guide.md` | 已迁移，纳入开发指南目录（2026-02-14） |
| [x] | P1 | `doc/前端开发指导文档.md` | `docs/03-development/guides/frontend-guide.md` | 已迁移，纳入开发指南目录（2026-02-14） |
| [x] | P1 | `doc/开发方案.md` | `docs/01-product/requirements/solution-overview.md` | 已迁移，纳入需求目录（2026-02-14） |
| [x] | P1 | `doc/二次开发需求文档.md` | `docs/01-product/requirements/secondary-development-requirements.md` | 已迁移，纳入需求目录（2026-02-14） |
| [x] | P1 | `doc/plan/开发计划.md` | `docs/01-product/roadmap/development-plan.md` | 已迁移，纳入路线图目录（2026-02-14） |
| [x] | P1 | `doc/开发进度.md` | `docs/04-project-tracking/milestones.md` | 已迁移，追加历史进度章节（2026-02-14） |
| [x] | P1 | `doc/orgtree_test_cases.md` | `docs/03-development/test-cases/orgtree-test-cases.md` | 已迁移，纳入测试用例目录（2026-02-14） |
| [x] | P1 | `doc/device_comm_protocol_basic_guide.md` | `docs/02-architecture/system-design/device-comm-basic-guide.md` | 已迁移，补充协议原文索引（2026-02-14） |
| [x] | P1 | `doc/oriigin/device_comm_protocol_basic.md` | `docs/02-architecture/system-design/protocol-source/device-comm-basic.md` | 已迁移为原始资料（2026-02-14） |
| [x] | P1 | `doc/oriigin/device_comm_protocol_socket.md` | `docs/02-architecture/system-design/protocol-source/device-comm-socket.md` | 已迁移为原始资料（2026-02-14） |
| [x] | P1 | `doc/oriigin/device_comm_protocol_write.md` | `docs/02-architecture/system-design/protocol-source/device-comm-write.md` | 已迁移为原始资料（2026-02-14） |
| [x] | P1 | `doc/oriigin/mqtt数据透传说明.md` | `docs/02-architecture/system-design/protocol-source/mqtt-pass-through.md` | 已迁移为原始资料（2026-02-14） |
| [x] | P1 | `doc/oriigin/设备接入MQTT指南.md` | `docs/02-architecture/system-design/protocol-source/device-access-mqtt.md` | 已迁移为原始资料（2026-02-14） |
| [x] | P2 | `doc/模块一完成报告.md` | `docs/04-project-tracking/archive/module1-completion-report.md` | 已归档（2026-02-14） |
| [x] | P2 | `doc/模块二完成报告.md` | `docs/04-project-tracking/archive/module2-completion-report.md` | 已归档（2026-02-14） |
| [x] | P2 | `doc/模块一前端完成报告.md` | `docs/04-project-tracking/archive/module1-frontend-completion.md` | 已归档（2026-02-14） |
| [x] | P2 | `doc/模块一测试环境搭建总结.md` | `docs/04-project-tracking/archive/module1-test-env-summary.md` | 已归档（2026-02-14） |
| [x] | P2 | `doc/模块一测试环境最终报告.md` | `docs/04-project-tracking/archive/module1-test-env-final.md` | 已归档（2026-02-14） |
| [x] | P2 | `doc/模块一测试问题与解决方案.md` | `docs/04-project-tracking/archive/module1-test-issues-and-fixes.md` | 已归档（2026-02-14） |
| [x] | P2 | `doc/README.md` | `docs/README.md` | 已完成新总索引与旧入口说明（2026-02-14） |

## 验收清单
- [x] P0 文档全部迁移并通过评审。
- [x] P1 文档全部迁移并完成链接互相引用。
- [x] P2 文档完成归档，`doc/` 目录增加“历史存档”说明。
