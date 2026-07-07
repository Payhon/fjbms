# FEAT-0063 PACK 厂小程序配置自助入口 - 发布说明

- status: review
- owner: payhon
- last_updated: 2026-07-01
- related_feature: FEAT-0063
- version: v0.1.0

## 1. 发布内容
- 在后台 `BMS 管理` 下新增 `小程序配置` 入口，供 PACK_FACTORY 账号维护自己机构关联的小程序配置。
- 原 `PACK厂家管理 > 小程序配置` 弹窗继续保留给租户/系统管理员使用。
- 新旧入口复用同一个 PACK 小程序配置组件，包含基础配置、Banner/Logo、质保卡片开关、备注和内容配置。
- 新增 SQL `backend/sql/61.sql`，注册菜单并调整 PACK_FACTORY 类型权限。

## 2. 影响范围
- Backend：新增 SQL 迁移和访问控制测试，不新增业务接口。
- Web：新增路由、自助页面、共享配置组件、旧弹窗复用和中英文文案。
- 权限：PACK_FACTORY 类型权限新增 `bms_pack_wxmp_config`，移除 `bms_pack_factory`。
- UniApp：无直接代码变更；继续读取既有 PACK 小程序运行时配置。

## 3. 发布步骤
1. 在目标环境执行 `backend/sql/61.sql`。本轮已于 2026-07-01 更新到测试环境和生产环境。
2. 部署 Web 前端，确认动态菜单能加载 `view.bms_pack_wxmp_config`。
3. 使用 PACK_FACTORY 账号登录后台，确认只看到 `BMS 管理 > 小程序配置`，不再看到 PACK 厂家管理列表。
4. 使用租户/系统管理员确认 `PACK厂家管理 > 小程序配置` 原入口仍可使用。
5. 保存并回显 FEAT-0062 的“启用质保卡片”开关，确认新旧入口一致。

### 3.1 环境执行记录
- 测试环境：`make import-sql ENV=test SQL=backend/sql/61.sql` 执行成功，输出 `DO`、`UPDATE 1`；只读校验 `menu_count=1`、`pack_total=1`、`pack_with_new=1`、`pack_with_old=0`。
- 生产环境：`make import-sql ENV=prod SQL=backend/sql/61.sql` 执行成功，输出 `DO`、`UPDATE 1`；只读校验 `menu_count=1`、`pack_total=1`、`pack_with_new=1`、`pack_with_old=0`。

## 4. 验证建议
- PACK_FACTORY 账号保存 AppID/AppSecret、Banner、Logo、质保卡片开关和协议内容。
- 用另一个 PACK 机构 ID 调用接口，确认服务端拒绝跨机构读写。
- 使用租户/系统管理员保存同一 PACK 机构配置，确认与 PACK 自助页面读取同一条配置。
- 小程序运行时接口继续返回对应 PACK 配置。

## 5. 回滚说明
- 应用层回滚：回滚 Web 新页面、路由和共享组件接入，保留原管理员弹窗能力。
- 权限层回滚：移除 PACK_FACTORY 类型权限中的 `bms_pack_wxmp_config`；如需恢复旧列表入口，将 `bms_pack_factory` 加回 PACK_FACTORY 类型权限。
- 数据层无结构变更，不需要清理业务表数据。
