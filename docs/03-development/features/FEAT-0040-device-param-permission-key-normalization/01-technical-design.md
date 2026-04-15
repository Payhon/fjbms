# FEAT-0040 设备参数权限 Key 归一化与移动端参数显隐修复 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-04-15
- related_feature: FEAT-0040
- version: v0.1.0

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

## 2. 关键兼容映射
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

## 3. 关键流程
1. 后台权限管理页拉取 `/org_type_permissions` 列表。
2. 后端先把历史 `device_param_permissions` 归一化，再返回给前端。
3. 后台保存设备参数权限时，后端再次做归一化和去重后落库。
4. 移动端拉取 `/org_type_permissions/device_param_permissions/me` 时，后端返回的也是归一化后的地址 key。
5. 移动端继续按现有 `getParamPermissionKey()` 地址匹配逻辑判断显隐，无需额外改动。

## 4. 测试策略
- `cd backend && go test ./internal/service/...`
- 定向校验：
  - 旧 key 归一化为纯地址 key
  - 权限树叶子 key 唯一
  - 权限树不再输出带 `:` 的设备参数 key

## 5. 兼容性与迁移
- 不要求执行数据库迁移。
- 历史租户配置通过运行时归一化自动兼容。
- 若后续需要彻底清洗数据库，可再补离线数据修复脚本，但不是本次修复前置条件。
