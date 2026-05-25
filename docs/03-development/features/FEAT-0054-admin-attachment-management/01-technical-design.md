# FEAT-0054 后台附件管理 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-05-19
- related_feature: FEAT-0054
- version: v0.1.0

## 1. 方案概览
- 复用现有 `files` 表和 `GET /api/v1/file/list` 分页查询。
- 新增管理侧删除与下载接口，所有操作按 JWT 中的 `tenant_id` 限定当前租户。
- 前端新增 `management_attachment` 路由页面，挂在系统管理菜单下。

## 2. 接口与数据结构
- `GET /api/v1/file/list`
  - 继续支持 `keyword`、`biz_type`、`storage_location`、`start_time`、`end_time`。
  - 附件管理不传 `mine=true`，因此返回当前租户全部附件。
- `DELETE /api/v1/file/:id`
  - 先按 `id + tenant_id` 查询 `files`。
  - 删除存储对象成功后删除数据库记录。
- `GET /api/v1/file/:id/download`
  - 本地文件返回附件下载。
  - 云存储文件重定向到 `files.full_url`。
- 新增菜单：
  - `element_code=management_attachment`
  - `param1=/management/attachment`
  - `route_path=view.management_attachment`

## 3. 关键流程
- 列表：
  1. 页面提交筛选条件。
  2. 后端按当前租户查询 `files`。
  3. 前端以服务端分页表格展示。
- 删除：
  1. 前端展示强确认。
  2. 后端按租户读取文件记录。
  3. `local` 校验并删除 `./files/` 下文件。
  4. `aliyun` / `qiniu` 使用当前存储配置删除 object key。
  5. 存储删除成功后删除 `files` 记录。
- 下载：
  - 本地文件通过鉴权接口下载，云文件直接打开现有 URL。

## 4. 安全与权限
- 后端所有管理接口走 JWT 和现有 Casbin 中间件。
- 删除和下载二次校验 `tenant_id`，防止跨租户访问。
- 菜单种子纳入 `sys_ui_elements`，可通过菜单管理和角色权限配置控制。
- 本地路径通过 `filepath.Abs + filepath.Rel` 限定在 `./files/` 内。

## 5. 测试策略
- 后端执行 `go test ./internal/service ./internal/api ./router/apps`。
- 前端执行 `pnpm typecheck` 和 `pnpm lint`。
- 浏览器回归附件列表筛选、预览、下载、删除与菜单权限。

## 6. 兼容性与迁移
- 不改 `files` 表结构。
- 不改变现有上传组件响应结构。
- 新增 `backend/sql/56.sql`，并回写 `backend/sql/1.sql` 基线菜单数据。
