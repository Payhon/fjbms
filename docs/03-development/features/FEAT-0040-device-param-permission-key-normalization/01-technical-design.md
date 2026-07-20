# FEAT-0040 设备参数权限 Key 归一化与移动端参数显隐修复 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-07-15
- related_feature: FEAT-0040
- version: v0.2.0

## 1. 方案概览
- 权限树规范化：
  - 将后端 `buildDeviceParamPermissionTree()` 中历史遗留的非标准 value 改为纯寄存器地址 key。
  - 对共享同一寄存器地址的高低字节参数，合并为同一权限节点，避免树上出现重复 key。
- 历史数据兼容：
  - 新增旧 key 到新 key 的映射表。
  - 在权限列表读取、当前用户权限获取、后台保存前统一做归一化和去重。
- 测试保障：
  - 新增单测，校验旧 key 归一化结果。
  - 新增单测，校验权限树不存在非标准设备参数 key 和重复 key。
  - 校验权限树包含 `40b`、`40c` 及其准确中文标签。
  - 抽取移动端纯函数 `canAccessDeviceParam()`，覆盖未授权隐藏、独立授权和未知 key 默认拒绝。

## 2. 2026-07-15 权限项补齐与默认拒绝
- 后端 `单体设置` 权限树在 `40a` 与 `40d` 之间补充：
  - `40b`：低温单体过放告警电压（`LOW_TEMP_CELL_UV_ALARM_V`）
  - `40c`：低温单体过放保护电压（`LOW_TEMP_CELL_UV_PROTECT_V`）
- 移动端参数显隐规则：
  1. `allow_all=true` 时保持全部可见。
  2. `allow_all=false` 时先把参数 key 解析为寄存器权限 key。
  3. 解析失败时返回 `false`，避免新参数因权限元数据遗漏而默认展示。
  4. 解析成功时只按精确权限 key 判断，不允许 `40b` 与 `40c` 互相连带授权。

## 3. 关键兼容映射
- `403:feedback_delay` -> `403`
- `40e:alarm_release_v` -> `40e`
- `40f:protect_release_v` -> `40f`
- `410:alarm_release` -> `410`
- `410:protect_release` -> `410`
- `423:small_delay` -> `423`
- `42a:alarm_delay` -> `42a`
- `42a:large_delay` -> `42a`
- `42b:small_delay` -> `42b`
- `43a:protect_delay` -> `43a`
- `43b:protect_release_delay` -> `43b`
- `44b:protect_release` -> `44b`

## 4. 关键流程
1. 后台权限管理页拉取 `/org_type_permissions` 列表。
2. 后端先把历史 `device_param_permissions` 归一化，再返回给前端。
3. 后台保存设备参数权限时，后端再次做归一化和去重后落库。
4. 移动端拉取 `/org_type_permissions/device_param_permissions/me` 时，后端返回的也是归一化后的地址 key。
5. 移动端通过 `canAccessDeviceParam()` 按地址精确匹配，受限模式下无法解析的 key 默认拒绝。

## 5. 测试策略
- `cd backend && go test ./internal/service/...`
- `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
- 临时编译并执行 `common/lib/bms-protocol/param-permission.test.ts`
- 定向校验：
  - 旧 key 归一化为纯地址 key
  - 权限树叶子 key 唯一
  - 权限树不再输出带 `:` 的设备参数 key

## 6. 兼容性与迁移
- 不要求执行数据库迁移。
- 历史租户配置通过运行时归一化自动兼容。
- 若后续需要彻底清洗数据库，可再补离线数据修复脚本，但不是本次修复前置条件。
- `40b`、`40c` 不做自动授权回填，避免已有受限终端用户因发布而获得新参数权限。
