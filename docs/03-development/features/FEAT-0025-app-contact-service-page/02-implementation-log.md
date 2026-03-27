# FEAT-0025 APP 联系客服单页内容接入 - 实施日志

- status: review
- owner: payhon
- last_updated: 2026-03-25
- related_feature: FEAT-0025
- version: v0.1.0

## 1. 实施记录
1. 新建 FEAT-0025 功能文档目录，并在 `docs/04-project-tracking/board.md` 登记 Backend / Frontend / UniApp 三个泳道条目。
2. 扩展后端 `backend/internal/service/app_content.go` 的单页内容白名单，新增 `contact_service`。
3. 更新后端 `backend/internal/api/app_content.go` Swagger 注释，补充 `contact_service` 的接口说明。
4. 扩展管理端 `frontend/src/service/api/app-manage.ts` 的 `ContentKey` 类型，并在 `frontend/src/views/app_manage/content/index.vue` 单页内容选项中新增“联系客服”。
5. 更新管理端中英文页面文案，补齐“联系客服 / Contact Us”标签。
6. 更新 UniApp 通用内容页标题映射，并将 `pages/my/contact/index.vue` 从占位页改为单页内容接口展示页。
7. 更新系统设计文档与 SQL 注释，使“联系客服”成为文档化支持的单页内容类型。

## 2. 当前状态
- 代码已完成。
- 已完成后端定向 Go 测试与前端类型检查。
- 当前进入联调 / 验收阶段。
