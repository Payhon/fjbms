# FEAT-0062 用户质保信息与 PACK 质保卡片开关 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-07-01
- related_feature: FEAT-0062
- version: v0.1.0

## 1. 方案概览
- 后端以 `user_warranty_infos` 保存终端用户联系人信息，按 `(tenant_id, user_id)` 唯一。
- 电池质保属性落在 `device_batteries`，激活链路只在未人工覆盖时写入起始日期、质保月数和到期日。
- PACK 质保卡片开关落在 `pack_wxmp_configs.warranty_cards_enabled`，移动端接口按 `appid` 解析当前 PACK 配置，由服务端决定是否返回电池卡片。
- Web 后台复用组织 PACK 小程序配置接口和电池详情 Tab 扩展；UniApp 使用当前运行时 AppID 请求质保 profile。

## 2. 数据结构
- `user_warranty_infos`
  - `tenant_id`
  - `user_id`
  - `contact_name`
  - `contact_phone`
  - `created_at`
  - `updated_at`
  - 唯一索引：`(tenant_id, user_id)`
- `device_batteries` 新增：
  - `warranty_months`
  - `warranty_start_date`
  - `warranty_manual_override`
  - `warranty_updated_at`
  - `warranty_updated_by`
  - 保留既有 `warranty_expire_date`
- `pack_wxmp_configs` 新增：
  - `warranty_cards_enabled boolean NOT NULL DEFAULT true`
- 权限：
  - 新增页面元素权限 `bms_battery_detail_warranty`
  - 为 PACK 厂机构类型补齐 `bms_pack_factory`

## 3. 后端接口
- `GET /api/v1/app/warranty/profile?appid=...`
  - 返回个人质保信息、`warranty_cards_enabled` 和电池质保卡片列表。
- `POST /api/v1/app/warranty/profile?appid=...`
  - 保存当前终端用户联系人姓名和电话，并返回同一结构。
- `GET /api/v1/battery/{device_id}/warranty`
  - 后台查询单块电池质保信息、绑定用户和用户填写的联系人信息。
- `PUT /api/v1/battery/{device_id}/warranty`
  - 后台编辑单块电池质保月数、起始日期、到期日期，并标记人工覆盖。
- `GET/PUT /api/v1/org/{id}/wxmp-config`
  - 请求/响应增加 `warranty_cards_enabled`。
- `GET /api/v1/app/wxmp/runtime`
  - 响应增加 `warranty_cards_enabled`。

## 4. 关键规则
1. 移动端是否展示电池卡片由服务端基于 `appid -> pack_wxmp_configs` 判定。
2. `warranty_cards_enabled=false` 时，接口返回 `batteries: []`；客户端不作为最终授权源。
3. 非 PACK 小程序、未传 AppID 或未命中启用中的 PACK 配置时，卡片默认开启。
4. 电池首次激活写入 `warranty_start_date`，从 BMS 型号同步 `warranty_months`，并计算 `warranty_expire_date`。
5. `warranty_manual_override=true` 时，后续激活流程不覆盖人工设置的到期日。
6. BMS 型号没有有效 `warranty_period` 时，只保留起始日期和已有人工值，不自动生成到期日。

## 5. 前端与移动端
- Web PACK 小程序配置弹窗新增 `NSwitch`，默认开启并随配置保存。
- Web 电池详情 BMS 模式新增 `bms_battery_detail_warranty` Tab，展示电池信息、绑定用户表格和编辑弹窗。
- UniApp “我的”页终端用户显示“质保信息”入口。
- UniApp 质保页提交 `appid=getRuntimeAppId()`，关闭卡片时不渲染电池卡片区域。

## 6. 测试策略
- 后端覆盖 PACK 配置默认值、保存/读取、runtime 返回、AppID 隐藏电池卡片、激活计算和人工覆盖保护。
- Web 执行显式 `vue-tsc` 和受影响文件 ESLint。
- UniApp 执行 TypeScript 检查。
- 运行态补充 PACK_FACTORY 账号配置权限、微信小程序开关开/关展示和后台电池详情人工编辑回归。
