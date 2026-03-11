# FEAT-0011 电池列表详情路由与元素权限补齐 - 发布说明

- status: in_progress
- owner: payhon
- last_updated: 2026-03-08
- related_feature: FEAT-0011
- version: v0.1.0

## 1. 发布内容
- 新增电池列表详情页路由权限编码：`bms_battery_list_detail`。
- 新增电池列表页面元素权限编码：
  - `bms_battery_list_export`
  - `bms_battery_list_add`
  - `bms_battery_list_import`
  - `bms_battery_list_action_params`
  - `bms_battery_list_action_offline_command`
  - `bms_battery_list_action_lifecycle_factory`
  - `bms_battery_list_action_lifecycle_activate`
  - `bms_battery_list_action_lifecycle_transfer`
- 前端新增 `v-ui-permission` 指令：默认隐藏，支持 `disable` 模式。

## 2. 升级步骤
1. 执行数据库补丁：`backend/sql/40.sql`。
2. 发布后端服务（包含 `ui_codes/me` 接口）。
3. 发布前端服务（包含权限指令与页面接入）。

## 3. 回归建议
- 机构用户菜单已分配 `bms_battery_list` 时，验证详情页跳转正常。
- 按需移除上述按钮权限编码，确认页面按钮/操作实时隐藏。
- 使用 `v-ui-permission.disable` 验证“显示但禁用”行为。

## 4. 回滚
- 回滚后端与前端版本。
- 回滚 `40.sql` 对 `sys_ui_elements` 与 `org_type_permissions` 的变更。
