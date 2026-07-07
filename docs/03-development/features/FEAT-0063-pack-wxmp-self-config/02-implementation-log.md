# FEAT-0063 PACK 厂小程序配置自助入口 - 实施日志

- status: review
- owner: payhon
- last_updated: 2026-07-01
- related_feature: FEAT-0063
- version: v0.1.0

## 1. 实施记录
1. 新增 `backend/sql/61.sql`，注册 `bms_pack_wxmp_config` 菜单，并调整 PACK_FACTORY 类型权限。
2. 后端补充 PACK_FACTORY 账号访问 PACK 小程序配置的定向测试，覆盖自身机构可操作、其他 PACK 机构不可操作。
3. 新增共享组件 `pack-wxmp-config-panel.vue`，承载 PACK 小程序基础配置、素材配置、质保卡片开关和内容配置。
4. 改造 `PACK厂家管理 > 小程序配置` 弹窗，改为复用共享组件。
5. 新增 `/bms/pack-wxmp-config` 自助页面，读取登录态机构信息并限制 PACK_FACTORY 类型账号展示表单。
6. 新增路由、静态路由映射、动态导入、路由类型声明和中英文菜单文案。
7. 补齐 FEAT-0063 文档五件套和项目看板。
8. 2026-07-01 已将 `backend/sql/61.sql` 更新到测试环境和生产环境，并完成只读 SQL 校验。

## 2. 当前状态
- 代码已完成并进入 review。
- 静态检查和定向测试结果见 `03-test-report.md`。
- 测试环境和生产环境已执行 SQL `backend/sql/61.sql`，菜单与 PACK_FACTORY 权限只读校验通过。
- 待使用真实 PACK_FACTORY 账号做菜单可见性、旧入口隐藏和保存回归。

## 3. 实现备注
- 本次未新增 HTTP API，继续复用 `/api/v1/org/{id}/wxmp-config`。
- 新旧入口共用同一个表单组件，避免后续配置项漂移。
- 前端页面限制只负责用户体验，跨机构读写仍由后端服务层拒绝。
