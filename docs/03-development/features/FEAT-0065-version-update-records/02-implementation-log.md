# FEAT-0065 版本更新记录后台管理 - 实现日志

- status: review
- owner: payhon
- last_updated: 2026-07-08
- related_feature: FEAT-0065
- version: v0.1.0

## 2026-07-08
- 新增后端 `version_update_records` 模型、HTTP DTO、服务、API 控制器和路由注册。
- 新增服务层测试，覆盖创建、列表筛选、更新、删除、重复记录和参数校验。
- 新增 `backend/sql/62.sql`，包含表结构、系统菜单和历史记录 seed。
- 新增前端版本更新记录页面，支持项目、版本号、日期范围和内容关键词筛选，以及新增、编辑、删除。
- 新增前端 API 封装、路由、view import、route 类型声明和中英文路由文案。
- 新增 FEAT-0065 文档包并同步看板。
- 修复后台点击“系统管理 > 版本更新记录”无法打开：初版菜单 code `bms_system_version_updates` 与 elegant-router 由目录名生成的 `bms_system_version-updates` 不一致，导致动态路由组件解析为空；已在动态菜单 adapter 增加兼容映射，并将本地自定义路由统一到 canonical key。

## 关键决策
- 云平台版本记录按非 merge commit 导入，版本号使用短 commit hash。
- 移动端重复 `1.0.0` 按 `版本号 / versionCode` 存储，避免合并不同历史阶段。
- 发布记录作为平台级资料，不按租户隔离。
- 初始导入通过 SQL 完成，不新增后台导入按钮。
- `backend/sql/62.sql` 新环境写入 canonical `bms_system_version-updates`；已存在旧 `bms_system_version_updates` 的库保持旧 code，由前端 adapter 兼容映射。

## 待回归
- 开发库执行 `backend/sql/62.sql` 后核对记录数量。
- 后台账号回归菜单可见性、页面可打开和 CRUD。
