# FEAT-0069 Web 电池列表状态记忆与批量调拨 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-07-24
- related_feature: FEAT-0069
- version: v0.1.0

## 1. 测试范围
- 后端批量调拨接口、去重、部分成功和角色/组织权限。
- 前端查询状态恢复、跨分页选择和批量调拨结果处理。
- 权限 SQL、中英文文案和兼容性。

## 2. 测试环境
- macOS，Go 本地工具链，后端内存 SQLite 定向测试。
- Frontend pnpm workspace，Vue TypeScript 类型检查与 Vite 生产构建。

## 3. 用例结果
- 通过：`go test ./internal/service ./internal/api ./router/apps -run 'TestBatchTransfer' -count=1`。
  - 请求空设备数组、缺少目标机构、空设备 ID。
  - 重复设备 ID 去重、全部成功、部分成功、全部失败和失败设备编号。
  - 厂家、PACK、经销商、门店合法/非法目标矩阵。
  - 跨租户目标、组织树外电池、未出厂电池。
- 通过：定向 Frontend ESLint；仅 `src/store/modules/auth/index.ts` 有 7 条本次修改前已存在的未使用变量 warning，无 error。
- 通过：`pnpm typecheck`。
- 通过：`pnpm build`；存在仓库既有的视觉编辑器 `eval` 与 UnoCSS 图标加载 warning，最终输出 `Build successful`。
- 通过：中英文 BMS/route JSON 解析与三个工作区 `git diff --check`。
- 待现场：查询状态切页/刷新/退出/账号切换、跨页选择以及四类组织账号的批量调拨浏览器回归。

## 4. 缺陷与风险
- `go test ./...` 未全绿，但失败不在本功能包：
  - `project/initialize/test.TestSetDevice` 因未初始化告警缓存依赖发生空指针。
  - `project/test.TestDatebase` 因未提供 `run_env`/数据库配置先报“未知环境”，随后空指针。
- 本次新增的 `project/internal/service` 测试在该全量命令中通过。
- 权限 SQL 尚未在目标 PostgreSQL 数据库实际执行，发布前需按升级步骤应用并核查。

## 5. 结论
- 代码级与自动化门禁达到评审条件，状态为 `review`。
- 在浏览器多角色验收和目标数据库权限迁移核查完成前，不标记 `done`。
