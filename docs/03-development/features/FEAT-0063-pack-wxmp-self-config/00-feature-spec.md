# FEAT-0063 PACK 厂小程序配置自助入口 - 功能规格

- status: review
- owner: payhon
- last_updated: 2026-07-01
- related_feature: FEAT-0063
- version: v0.1.0

## 1. 背景与目标
- FEAT-0055 已支持租户/系统管理员在 `PACK厂家管理 > 小程序配置` 中维护 PACK 小程序配置。
- FEAT-0062 在同一配置中增加“启用质保卡片”开关，PACK 厂需要能自行维护自己机构关联的小程序配置。
- 目标是在后台 `BMS 管理` 下新增独立入口 `小程序配置`，供 PACK_FACTORY 类型账号直接配置自己的微信小程序，同时让 PACK 厂账号不再进入 PACK 厂家管理列表。

## 2. 范围
### In Scope
- 新增后台菜单权限 code：`bms_pack_wxmp_config`。
- 新增 Web 路由 `/bms/pack-wxmp-config`，只服务 PACK_FACTORY 业务账号。
- 新页面复用现有 PACK 小程序配置全部能力：基础配置、Banner、Logo、质保卡片开关、备注、关于我们、隐私政策、用户协议、联系客服内容配置。
- 原 `PACK厂家管理 > 小程序配置` 弹窗继续供租户/系统管理员使用，并与新页面复用同一个配置组件。
- SQL 迁移调整 PACK_FACTORY 类型权限：新增 `bms_pack_wxmp_config`，移除 `bms_pack_factory`。

### Out of Scope
- 不新增 HTTP API。
- 不变更 `pack_wxmp_configs` 表结构。
- 不改变小程序运行时配置接口和移动端读取逻辑。
- 不为经销商、门店或普通终端用户开放该入口。

## 3. 用户价值
- PACK 厂账号可独立维护自己小程序的 AppID、素材、协议内容和质保卡片开关，不依赖租户管理员进入组织列表代操作。
- 管理员入口与 PACK 自助入口共享同一配置组件，后续字段扩展只需维护一处表单。
- PACK 厂账号菜单更聚焦，避免看到不需要的 PACK 厂家管理列表。

## 4. 验收标准
1. PACK_FACTORY 账号登录后台后，在 `BMS 管理` 下可看到 `小程序配置`。
2. PACK_FACTORY 账号不再看到 `PACK厂家管理` 列表入口。
3. PACK_FACTORY 账号进入 `/bms/pack-wxmp-config` 后，只能读取和保存自己 `claims.OrgID` 对应的 PACK 小程序配置。
4. 非 PACK_FACTORY 账号访问新页面时显示无权限提示，不展示配置表单。
5. 缺少机构归属的 PACK_FACTORY 账号访问新页面时显示无机构归属提示。
6. 新页面与原 PACK 厂家管理弹窗保存、回显的是同一份 `pack_wxmp_configs` 数据。
7. 租户/系统管理员仍可在 PACK 厂家管理列表中配置下属 PACK 厂小程序。
8. FEAT-0062 的“启用质保卡片”开关在新页面和旧弹窗中保存、回显一致。

## 5. 风险与约束
- 菜单权限依赖 SQL `backend/sql/61.sql` 在目标环境执行。
- PACK_FACTORY 运行态账号回归需要真实账号和机构归属数据，本地静态检查无法完全替代。
- 现有 `/api/v1/org/{id}/wxmp-config` 权限判定仍是服务端最终保护，前端只做展示层限制。

## 6. 回滚方案
- 回滚 Web 新路由、新页面和共享组件接入，原 PACK 厂家管理弹窗可恢复到独立实现。
- 回滚 SQL 权限时，从 PACK_FACTORY 类型权限中移除 `bms_pack_wxmp_config`，如需恢复旧入口再补回 `bms_pack_factory`。
- 不涉及数据库结构新增或业务数据迁移，回滚无需清理 `pack_wxmp_configs` 数据。
