# FEAT-0065 版本更新记录后台管理 - 发布说明

- status: review
- owner: payhon
- last_updated: 2026-07-08
- related_feature: FEAT-0065
- version: v0.1.0

## 1. 发布内容
- 后台“系统管理”新增“版本更新记录”菜单。
- 新增版本更新记录 CRUD，支持移动端、云平台-WEB前端、云平台-后端三类项目。
- 新增 `backend/sql/62.sql`，创建版本记录表并导入历史记录。
- 初始导入记录包含移动端 13 条、后端 101 条、前端 65 条。

## 2. 发布步骤
1. 发布后端代码。
2. 在目标数据库执行 `backend/sql/62.sql`。
3. 发布前端代码。
4. 使用后台账号确认“系统管理 > 版本更新记录”菜单可见。
5. 核对三类项目记录数量并抽查新增、编辑、删除。

## 3. 回滚步骤
1. 回滚前端发布版本。
2. 回滚后端发布版本。
3. 如需回滚数据库变更，删除 `bms_system_version-updates` 菜单记录；若目标库曾执行初版 SQL，也同步删除旧 code `bms_system_version_updates`，并按目标环境策略保留或删除 `version_update_records` 表。

## 4. 验收关注
- 菜单权限：`TENANT_ADMIN` 和 `SYS_ADMIN` 可见。
- SQL 可重复执行且不重复插入 seed 记录。
- 移动端重复版本号不会被合并，版本号包含 `versionCode`。

## 5. 生产执行记录
- 2026-07-08：已在生产库执行 `backend/sql/62.sql`，校验 `version_update_records` 总计 179 条，其中移动端 13、后端 101、前端 65。
- 2026-07-08：已部署生产前端到 `cloud.fjiaenergy.com` 对应目录，线上入口 hash 与本地 `frontend/dist/index.html` 一致，入口 JS 包含 `bms_system_version-updates`、`/bms/system/version-updates` 和 `view.bms_system_version-updates`。
- 2026-07-08：`fjbms.yz6688.cn` 返回另一套 OpenResty 站点入口，不属于本次 `make update-frontend-prod` 的实际服务目录；本次后台生产验证以 `cloud.fjiaenergy.com` 为准。
