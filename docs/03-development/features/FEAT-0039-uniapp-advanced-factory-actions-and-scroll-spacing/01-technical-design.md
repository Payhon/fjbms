# FEAT-0039 UniApp 设备详情高级参数出厂命令补齐与底部遮挡修复 - 技术设计

- status: in_progress
- owner: payhon
- last_updated: 2026-04-17
- related_feature: FEAT-0039
- version: v0.1.0

## 1. 方案概览
- 出厂命令补齐：
  - 在 `params-tab.vue` 的 `FACTORY_ACTIONS` 中新增协议文档对应位掩码。
  - 继续复用现有 `runFactory()`，统一通过 `writeRegisters(0x57a, [hi, lo])` 下发命令。
- 滚动遮挡修复：
  - 在高级参数 `scroll-view` 末尾增加动态底部占位。
  - 占位高度基于屏幕宽度换算 `rpx` 并叠加 `safeAreaInsets.bottom`，覆盖设备详情底部 Tab 的遮挡高度。
- 权限补齐：
  - 后端设备参数权限树新增 `factory:*` 节点，确保组织权限配置页能配置新增工厂命令。

## 2. 新增工厂命令映射
- `eraseCurrentParams` -> `BIT16` -> `0x00010000`
- `eraseHistoryRecords` -> `BIT17` -> `0x00020000`
- `eraseCycleCount` -> `BIT18` -> `0x00040000`
- `clearProtectionStatus` -> `BIT19` -> `0x00080000`
- `resetProtectionBoard` -> `BIT21` -> `0x00200000`

### 2.1 复位保护板协议确认
- `resetProtectionBoard` 的正确示例帧为：
  - `7F 55 FE 00 10 05 7A 00 02 04 00 20 00 00 4E 92 FD`
- 该帧对应向 `0x057A~0x057B` 写入两个寄存器：
  - `0x057A = 0x0020`
  - `0x057B = 0x0000`
- 按现有 32 位位掩码语义折算后，仍对应 `BIT21 -> 0x00200000`，因此前后端现有代码实现无需调整，只需统一文档口径。

## 3. 关键流程
1. 用户在“设置 > 高级参数 > 出厂配置”点击工厂命令。
2. 前端先做连接态和 `factory:<actionKey>` 权限校验。
3. 用户确认后，前端将 32 位位掩码拆成高 16 位和低 16 位，写入 `0x57A~0x57B`。
4. 高级参数滚动区末尾始终保留一段额外空间，使最后几个菜单可滚动到底部 Tab 上方。

## 4. 接口与数据结构
- 不新增后端接口。
- 不修改 BLE/Socket 协议客户端接口。
- 权限侧仅扩展既有树节点枚举值：
  - `factory:eraseCurrentParams`
  - `factory:eraseHistoryRecords`
  - `factory:eraseCycleCount`
  - `factory:clearProtectionStatus`

## 5. 测试策略
- `cd fjbms-uniapp && pnpm exec tsc --noEmit`
- `cd backend && go test ./...`
- 手工验证：
  - 进入设备详情 > 设置 > 高级参数。
  - 滚动至出厂配置末尾，确认末尾菜单可完整露出并点击。
  - 检查新增工厂命令文案和确认弹窗流程。
  - 检查后台权限树是否出现新增工厂命令项。

## 6. 兼容性与迁移
- 不涉及数据库迁移。
- 现有未配置精细权限的账号仍沿用 `allow_all` 行为，不受影响。
- 已配置精细权限的组织在同步权限树后即可为新增命令分配授权。
