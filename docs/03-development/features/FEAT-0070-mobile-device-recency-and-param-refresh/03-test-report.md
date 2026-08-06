# FEAT-0070 移动端设备最近连接排序与参数刷新 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-07-25
- related_feature: FEAT-0070
- version: v0.1.0

## 1. 测试范围
- BLE/4G 最近成功通讯时间写入。
- 三种 APP 首页视图排序与稳定分页。
- 4G 离线角标隐藏和标题空间。
- 参数分组强制刷新、空响应、失败保留和重复请求保护。

## 2. 自动化结果
- 通过：`go test ./internal/service ./internal/api`。
- 通过：最近连接时间定向测试，覆盖服务端时间写入、空/不存在设备、BLE 成功连接、4G 真实交互，以及三种视图的已连接优先、空时间回退和同时间稳定排序。
- 通过：`go test ./internal/api -run TestShouldIgnoreSocketUplink -v`，retained 回包在进入在线/连接时间更新前被忽略。
- 通过：`pnpm exec tsc --noEmit --project tsconfig.json`。
- 通过：将定向策略文件临时编译为 CommonJS 后使用 Node 执行：
  - 4G 在线/离线及非 4G 状态角标策略；
  - 参数有效值、失败保留旧值、部分值提交和 `force` 缓存旁路；
  - 既有详情轮询策略与数据仲裁回归。
- 通过：`git diff --check`（`backend/`、`fjbms-uniapp/`）。
- 全量 `go test ./...` 未全绿，失败为仓库既有环境型用例：
  - `initialize/test.TestSetDevice` 因告警缓存依赖未初始化触发 nil pointer；
  - `project/test.TestDatebase` 因未设置 `run_env` 报“未知环境”，随后数据库为 nil。
- 除上述两个环境包外，本次全量输出中的其他包（含 `internal/service`、`internal/api`）通过。

## 3. 运行态验收
- 待微信小程序、iOS、Android 真机验证：
  - 4G 在线角标、4G 离线无角标及标题空间；
  - 四个分组刷新热区、旋转态、重复点击、失败保留与不折叠；
  - BLE/4G 真实通讯后的列表排序和跨分页稳定性。
- 待真实 PostgreSQL 环境执行 `sql/65.sql` 并验证三种首页视图。

## 4. 结论
- 代码与本地自动化验证通过，功能进入 `review`；真机和真实数据库验收完成前不标记 `done`。
