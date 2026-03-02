## 变更概述
- 背景：
- 主要改动：
- 影响模块：`backend` / `frontend` / `fjbms-uniapp` / `docs`

## 关联事项
- FEAT: `FEAT-xxxx`
- Issue/任务链接：

## 测试与验证
- [ ] 已执行并通过相关测试
- [ ] 已补充或更新必要测试用例（如适用）

执行记录（请填写实际命令与结果）：
- Backend: `cd backend && go test ./...`
- Frontend: `cd frontend && pnpm typecheck && pnpm lint`
- UniApp: 手工验证步骤（页面/机型/结果）

## 文档治理检查项（必填）
- [ ] 已新增/更新功能文档：`docs/03-development/features/FEAT-xxxx-<slug>/`
- [ ] `00-feature-spec.md` 已评审通过后再进入开发
- [ ] `02-implementation-log.md` 已回写本次关键变更
- [ ] `03-test-report.md` 与实际测试结果一致
- [ ] `04-release-note.md` 已更新影响范围与回滚策略
- [ ] `docs/04-project-tracking/board.md` 状态已同步
- [ ] `docs/04-project-tracking/risks-and-blockers.md` 已更新（如适用）

## 风险与回滚
- 风险点：
- 回滚步骤：

## UI/接口变更补充
- [ ] 无 UI 变更
- [ ] 有 UI 变更（附截图/GIF）
- [ ] 有接口/协议变更（附字段兼容性说明）

## 自检清单
- [ ] 未提交密钥、密码或敏感配置
- [ ] 命名与目录符合文档治理规范
- [ ] 代码与文档描述一致
