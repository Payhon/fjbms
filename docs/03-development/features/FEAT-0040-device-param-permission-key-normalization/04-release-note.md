# FEAT-0040 设备参数权限 Key 归一化与移动端参数显隐修复 - 发布说明

- status: review
- owner: payhon
- last_updated: 2026-07-15
- related_feature: FEAT-0040
- version: v0.2.0

## 发布内容
- 统一后端设备参数权限树的设备参数叶子 key 为纯寄存器地址。
- 修复移动端设备详情参数页与后台设备参数权限 key 口径不一致的问题。
- 对历史租户已保存的旧 key 增加运行时兼容归一化，无需手工重配。
- 补充后端单测，覆盖旧 key 归一化和权限树唯一性检查。
- 后台“单体设置”新增 `40b`、`40c` 两个权限项，分别管控低温单体过放告警电压和保护电压。
- 移动端受限用户遇到未注册参数权限 key 时改为默认隐藏，避免新增参数绕过权限。

## 影响范围
- `backend/internal/service/device_param_permission_tree.go`
- `backend/internal/service/org_type_permissions.go`
- `backend/internal/service/org_type_permissions_test.go`
- `fjbms-uniapp/common/lib/bms-protocol/param-permission.ts`
- `fjbms-uniapp/common/lib/bms-protocol/param-permission.test.ts`
- `fjbms-uniapp/pages/device-battery/components/params-tab.vue`

## 发布与回滚提示
- 发布后建议立即用一个已存在历史权限配置的租户做一次“取消勾选 -> 保存 -> 打开移动端参数页”的回归验证。
- `40b`、`40c` 不会自动授予已有机构；如需终端用户使用，必须由管理员在后台显式勾选。
- 若需回滚本次增量，移除 `40b`、`40c` 权限节点并恢复移动端原参数判断；如需整体回滚 FEAT-0040，再恢复旧权限树 key 与归一化逻辑。
