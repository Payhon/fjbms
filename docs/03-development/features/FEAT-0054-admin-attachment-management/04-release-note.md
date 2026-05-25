# FEAT-0054 后台附件管理 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-05-19
- related_feature: FEAT-0054
- version: v0.1.0

## 1. 发布内容
- 后台系统管理新增“附件管理”菜单。
- 支持查看、搜索、筛选、预览、下载和删除当前租户附件。
- 删除附件时同步删除本地或云存储文件对象。

## 2. 数据库变更
- 新增 SQL：`backend/sql/56.sql`
- 新增菜单：`management_attachment`
- 不变更业务表结构。

## 3. 运维注意
- 发布后需执行 `backend/sql/56.sql`。
- 云存储附件删除依赖系统设置中的阿里云/七牛配置。
- 删除不检查业务引用，请谨慎授权附件删除权限。

## 4. 回滚
- 回滚前后端代码。
- 删除 `sys_ui_elements` 中 `element_code='management_attachment'` 的菜单记录。
