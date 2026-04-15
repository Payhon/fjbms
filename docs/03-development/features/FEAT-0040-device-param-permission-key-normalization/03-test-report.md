# FEAT-0040 设备参数权限 Key 归一化与移动端参数显隐修复 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-04-15
- related_feature: FEAT-0040
- version: v0.1.0

## 1. 已执行验证
- [x] `cd backend && go test ./internal/service/...`
- [ ] 手工验证后台权限取消勾选后的移动端显隐结果

## 2. 验证结果
- `cd backend && go test ./internal/service/...`
  - 结果：通过。
  - 备注：存在 `gopsutil/disk` 的 macOS `IOMasterPort` 弃用编译告警，不影响测试通过。
  - 备注：已覆盖寄存器地址类旧 key 归一化，以及 `factory:*` / `function:*` 规范 key 恢复场景。

## 3. 待补充手工验收
- [ ] APP 用户设备参数权限页可看到修正后的叶子节点 key 显隐状态
- [ ] 取消“回馈过充保护延时 / 常温低温阀值温度”权限后，移动端不显示“单体回馈过充保护延时”
- [ ] 取消 `40e / 40f / 410` 对应权限后，移动端不显示单体过放解除相关参数
- [ ] 取消 `423 / 42a / 42b` 对应权限后，移动端不显示电流延时相关参数
- [ ] 取消 `43a / 43b / 44b` 对应权限后，移动端不显示温度设置中的对应参数
