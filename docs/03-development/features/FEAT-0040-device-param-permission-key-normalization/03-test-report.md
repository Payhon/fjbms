# FEAT-0040 设备参数权限 Key 归一化与移动端参数显隐修复 - 测试报告

- status: review
- owner: payhon
- last_updated: 2026-07-15
- related_feature: FEAT-0040
- version: v0.2.0

## 1. 已执行验证
- [x] `cd backend && go test ./internal/service/...`
- [x] `cd backend && go test ./internal/service -run 'TestNormalizeDeviceParamPermissionKeys|TestBuildDeviceParamPermissionTreeUsesCanonicalKeys'`
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit --pretty false`
- [x] 临时编译并执行 `common/lib/bms-protocol/param-permission.test.ts`
- [ ] 手工验证后台权限取消勾选后的移动端显隐结果

## 2. 验证结果
- `cd backend && go test ./internal/service/...`
  - 结果：通过。
  - 备注：存在 `gopsutil/disk` 的 macOS `IOMasterPort` 弃用编译告警，不影响测试通过。
  - 备注：已覆盖寄存器地址类旧 key 归一化，以及 `factory:*` / `function:*` 规范 key 恢复场景。
- 2026-07-15 后端定向测试：通过，覆盖权限树必须存在 `40b`、`40c` 且中文标签准确。
- 2026-07-15 UniApp TypeScript 检查：通过，无输出。
- 2026-07-15 移动端参数权限回归用例：通过。
  - 无权限时 `40b`、`40c` 均隐藏。
  - 仅授权 `40b` 时不显示 `40c`。
  - 受限用户遇到未知参数 key 时默认隐藏。
  - `allow_all=true` 保持管理员放行行为。

## 3. 待补充手工验收
- [ ] APP 用户设备参数权限页可看到修正后的叶子节点 key 显隐状态
- [ ] 取消“回馈过充保护延时 / 常温低温阀值温度”权限后，移动端不显示“单体回馈过充保护延时”
- [ ] 取消 `40e / 40f / 410` 对应权限后，移动端不显示单体过放解除相关参数
- [ ] 取消 `423 / 42a / 42b` 对应权限后，移动端不显示电流延时相关参数
- [ ] 取消 `43a / 43b / 44b` 对应权限后，移动端不显示温度设置中的对应参数
- [ ] 后台“单体设置”可看到并分别勾选 `40b / 40c`
- [ ] APP 用户未勾选 `40b / 40c` 时，不显示“低温单体过放告警电压 / 低温单体过放保护电压”
- [ ] 仅勾选 `40b` 或 `40c` 时，移动端只显示对应的单项参数
