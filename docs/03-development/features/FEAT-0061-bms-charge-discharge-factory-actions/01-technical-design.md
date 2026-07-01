# FEAT-0061 设备详情充放电控制工厂命令 - 技术设计

- status: review
- owner: payhon
- last_updated: 2026-06-25
- related_feature: FEAT-0061
- version: v0.1.0

## 1. 方案概览
- 将三项操作作为现有工厂命令 action 接入，统一使用 `factory:*` 设备参数权限 key。
- Web 与 UniApp 继续把 `raw` 命令字拆成高低两个 16 位寄存器，调用现有 `writeRegisters(0x57a, [hi, lo])` 或 Web APP 中继 `write_registers`。
- 后台权限管理页不改 UI；它消费后端 `device_param_options` 权限树后自动出现新增节点。

## 2. 接口与数据结构
- 不新增 API。
- `GET /api/v1/org_type_permissions/device_param_options` 新增三个叶子节点：
  - `factory:disableCharge`
  - `factory:disableDischarge`
  - `factory:allowChargeDischarge`
- `org_type_permissions.device_param_permissions` 继续保存逗号分割字符串，后端现有归一化逻辑保留 `factory:*` canonical key。

## 3. 命令映射
| 操作 | 权限 key | 命令字 | 期望完整帧 |
| --- | --- | --- | --- |
| 禁止充电 | `factory:disableCharge` | `0x80000000` | `7F 55 FE 01 10 05 7A 00 02 04 80 00 00 00 62 64 FD` |
| 禁止放电 | `factory:disableDischarge` | `0x40000000` | `7F 55 FE 01 10 05 7A 00 02 04 40 00 00 00 5E 64 FD` |
| 允许充放电 | `factory:allowChargeDischarge` | `0x00000000` | `7F 55 FE 01 10 05 7A 00 02 04 00 00 00 00 4B A4 FD` |

## 4. 关键流程
1. 用户打开设备详情高级设置/高级参数。
2. 前端读取当前账号设备参数权限；`allow_all=false` 时按 `factory:*` key 过滤工厂命令。
3. 用户点击按钮后先展示现有确认弹窗。
4. 前端将 `raw` 拆成 `[raw >>> 16, raw & 0xffff]` 写入 `0x057A~0x057B`。
5. Web 在直连不可用但 APP 中继可用时继续走现有中继命令。

## 5. 测试策略
- 后端单测确认权限树新增 key、label 和 canonical key 归一化。
- Web 执行 `pnpm typecheck`，并检查工厂命令表命令字展示。
- UniApp 执行 `pnpm exec tsc --noEmit --pretty false`。
- 手工使用受限账号确认未授权隐藏、授权后显示。

## 6. 兼容性与迁移
- 无数据库迁移。
- 已有未配置设备参数权限的账号维持现有全量可见行为。
- 已有配置过设备参数权限的组织不会自动获得三项新权限。
