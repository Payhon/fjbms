# FEAT-0065 版本更新记录后台管理 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-07-08
- related_feature: FEAT-0065
- version: v0.1.0

## 1. 数据模型
新增表：`version_update_records`

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `id` | `varchar(36)` | 主键 |
| `project` | `varchar(32)` | `MOBILE`、`CLOUD_FRONTEND`、`CLOUD_BACKEND` |
| `version_no` | `varchar(64)` | 移动端为 `versionName / versionCode`，云平台为短 commit hash |
| `release_date` | `date` | 移动端取版本区间起始日，云平台取 commit date |
| `update_content` | `text` | 更新内容 |
| `source` | `varchar(32)` | `manual`、`app_update_doc`、`git_log` |
| `source_ref` | `varchar(128)` | 文档路径或 commit hash |
| `created_at` / `updated_at` | `timestamptz` | 审计时间 |

唯一索引：`(project, version_no, release_date)`，用于 seed 幂等导入。

## 2. 后端设计
- 新增模型与 DTO：`VersionUpdateRecord`、`VersionUpdateCreateReq`、`VersionUpdateUpdateReq`、`VersionUpdateListReq`。
- 新增服务：校验项目枚举、日期格式、版本号和更新内容长度；创建时默认 `source=manual`。
- 新增接口：
  - `GET /api/v1/version-updates`
  - `GET /api/v1/version-updates/:id`
  - `POST /api/v1/version-updates`
  - `PUT /api/v1/version-updates/:id`
  - `DELETE /api/v1/version-updates/:id`
- 路由挂在 BMS auth router 下，复用现有 JWT、Casbin、OrgAuthMiddleware。

## 3. 前端设计
- 在 `BMS 管理 > 系统管理` 下新增版本更新记录路由，前端 canonical route key 为 `bms_system_version-updates`。
- 动态菜单兼容初版 SQL 写入的旧 code `bms_system_version_updates`，统一映射到 `/bms/system/version-updates` 和 `view.bms_system_version-updates`。
- 新增页面 `frontend/src/views/bms/system/version-updates/index.vue`。
- 页面包含项目、版本号、日期范围、内容关键词筛选；表格展示项目、版本号、日期、更新内容、来源和操作。
- 新增弹窗表单用于创建和编辑，删除使用二次确认。

## 4. 数据导入
- `backend/sql/62.sql` 创建表、注册菜单并导入历史记录。
- 移动端：从 `docs/APP_UPDATE.md` 导入 13 条。
- 后端：执行 `git -C backend log --reverse --no-merges --since='2025-12-01' --date=short --pretty='%h%x09%ad%x09%s'` 生成 101 条。
- 前端：执行 `git -C frontend log --reverse --no-merges --since='2025-12-01' --date=short --pretty='%h%x09%ad%x09%s'` 生成 65 条。

## 5. 兼容性
- 初始数据通过 SQL seed，不依赖运行环境存在 Git 仓库。
- 表不做租户隔离，版本发布记录作为平台级资料展示。
- `ON CONFLICT` 只更新内容和来源字段，不改变已有主键。
