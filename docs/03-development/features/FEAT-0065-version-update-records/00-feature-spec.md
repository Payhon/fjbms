# FEAT-0065 版本更新记录后台管理 - 功能规格

- status: review
- owner: payhon
- last_updated: 2026-07-08
- related_feature: FEAT-0065
- version: v0.1.0

## 1. 背景与目标
- 移动端已有 `docs/APP_UPDATE.md` 汇总版本更新，但后台管理没有统一维护入口。
- 云平台 Web 前端和后端也需要基于 Git 提交历史形成可查询的更新记录。
- 目标是在 Web 后台“系统管理”下新增“版本更新记录”，支持平台版本资料的新增、查询、编辑和删除，并通过 SQL 初始导入移动端、前端、后端历史记录。

## 2. 范围
### In Scope
- 后端新增 `version_update_records` 表和 CRUD API。
- Web 后台新增“系统管理 > 版本更新记录”菜单与 CRUD 页面。
- 从 `docs/APP_UPDATE.md` 导入移动端 13 条版本记录。
- 从 `backend`、`frontend` 当前分支非 merge Git log 导入云平台记录。
- FEAT-0065 文档与看板同步。

### Out of Scope
- 不新增运行态“导入按钮”。
- 不改移动端业务代码。
- 不改应用商店发布流程或版本检查接口。
- 不按租户隔离版本记录。

## 3. 用户价值
- 管理员可以在后台统一查看移动端和云平台更新历史。
- 后续发布记录可直接通过后台维护，不再只依赖 Markdown 文档。
- 历史导入保留来源，便于从后台记录追溯到文档或 Git 提交。

## 4. 验收标准
1. “系统管理”菜单下出现“版本更新记录”。
2. 列表支持按项目、版本号、日期范围和更新内容关键词筛选。
3. 新增、编辑、删除后刷新列表结果一致。
4. 数据库中存在移动端、云平台-WEB前端、云平台-后端三类记录。
5. `backend/sql/62.sql` 可重复执行，不产生重复记录。
6. 初始导入记录来源可区分 `app_update_doc`、`git_log` 和 `manual`。

## 5. 风险与约束
- 云平台没有独立 manifest 版本号，历史记录按非 merge commit 粒度导入。
- `docs/APP_UPDATE.md` 的移动端区间日期是范围，数据库单日期字段取区间起始日期，完整范围写入更新内容。
- 云平台导入范围从 2025-12-01 起，覆盖当前 BMS/FJBMS 开发阶段。

## 6. 回滚方案
- 回滚前端菜单、路由、API 封装和页面文件。
- 回滚后端 model/service/api/router 注册。
- 如已执行 SQL，删除 `bms_system_version-updates` 菜单记录；若目标库曾执行初版 SQL，也同步删除兼容旧 code `bms_system_version_updates`，并按环境要求删除或保留 `version_update_records` 表。
- 同步回退 FEAT-0065 文档和看板状态。
