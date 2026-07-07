# FEAT-0062 用户质保信息与 PACK 质保卡片开关 - 发布说明

- status: review
- owner: payhon
- last_updated: 2026-07-01
- related_feature: FEAT-0062
- version: v0.1.0

## 1. 发布内容
- 新增移动端“我的 > 质保信息”，支持终端用户维护姓名、联系电话并查看关联电池质保卡片。
- 移动端质保页个人信息默认只读，点击右上角铅笔后进入编辑态并显示保存按钮；关联电池卡片升级为拟物化质保凭证样式，并优化编号、型号和质保时长的展示层级。
- 移动端“我的”页质保信息入口使用独立质保图标，不再复用帮助与反馈图标。
- 新增 PACK 小程序配置项“启用质保卡片”，关闭后当前 PACK 小程序质保页只显示个人质保信息。
- 新增后台电池详情“质保”Tab，支持查看绑定用户、激活日期、质保时长、到期日并人工编辑。
- 电池首次激活后自动写入质保起始日期，并按 BMS 型号质保月数计算到期日。
- 新增 SQL `backend/sql/60.sql`，包含数据表、字段和页面元素权限变更。

## 2. 影响范围
- Backend：新增质保接口、PACK 配置字段、激活链路质保计算和数据库迁移。
- Web：PACK 小程序配置弹窗、电池详情 BMS 模式 Tab、BMS 多语言词包。
- UniApp：我的页菜单、质保信息页、质保 API service、页面标题和文案。
- 权限：新增 `bms_battery_detail_warranty` 页面元素权限，PACK 厂补齐 `bms_pack_factory` 配置入口。

## 3. 发布步骤
1. 发布后端前执行 `backend/sql/60.sql`。
2. 部署后端服务，确认 `/api/v1/app/wxmp/runtime` 返回 `warranty_cards_enabled`。
3. 部署 Web 前端，确认 PACK 小程序配置弹窗和电池详情质保 Tab 可见。
4. 发布 UniApp/小程序包，确认质保信息入口和卡片开关展示。

## 3.1 SQL 执行记录
- 2026-07-01：已执行 `make import-sql ENV=test SQL=backend/sql/60.sql`，测试环境导入成功。
- 2026-07-01：已执行 `make import-sql ENV=prod SQL=backend/sql/60.sql`，生产环境导入成功。
- 已对测试/生产做只读结构校验，确认新表、新列、PACK 开关字段和页面权限均存在。

## 4. 验证建议
- 使用租户管理员或系统管理员保存 PACK 小程序配置，确认开关回显。
- 使用 PACK_FACTORY 账号确认只能进入并保存自己组织配置。
- 使用终端用户在对应 PACK 小程序内验证开关开启/关闭的质保页展示差异。
- 绑定或激活测试电池后确认质保起始日期和到期日计算。
- 在后台人工修改质保到期日后再次触发激活链路，确认人工覆盖不被重算覆盖。

## 5. 回滚说明
- 应用层回滚：回滚后端接口/激活链路、Web 页面和 UniApp 页面入口。
- 数据库层回滚：默认保留新增表和列不使用；如必须清理，先备份 `user_warranty_infos` 和 `device_batteries` 质保字段数据，再执行清理 SQL。
- 若仅质保卡片展示异常，可临时将对应 PACK 配置 `warranty_cards_enabled=false` 降级为只展示个人质保信息。
