# FEAT-0027 后台删除终端用户后账号身份残留修复 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-03-26
- related_feature: FEAT-0027
- version: v0.1.0

## 1. 测试范围
- 后台删除用户的级联清理逻辑。
- `user_identities` 孤儿身份自修复逻辑。
- SQL 补丁可用性检查。

## 2. 测试环境
- 本地开发环境
- 日期：2026-03-26

## 3. 用例结果
- `backend`
  - 命令：`cd backend && go test ./internal/dal ./internal/api ./internal/service`
  - 结果：通过
  - 备注：存在 `github.com/shirou/gopsutil/disk` 的 macOS 弃用告警，不影响本次修复
- `backend/sql/46.sql`
  - 静态检查：已完成语句审阅
  - 数据库执行：待测试/生产环境按发布流程执行

## 4. 缺陷与风险
- 若线上已经存在大量历史孤儿记录，必须执行 `46.sql` 才能一次性修复；仅部署代码无法立刻清掉所有非 `user_identities` 孤儿表。
- 全量 `go test ./...` 仍存在仓库内既有失败项，本次只验证了受影响包。

## 5. 结论
- 本次修复已覆盖“新问题阻断 + 历史数据修复脚本”两部分，可进入环境执行与联调验收。
