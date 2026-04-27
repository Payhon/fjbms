# FEAT-0017 BMS 状态寄存器地址调整、移动端保护状态卡片与旧板兼容读取 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-04-24
- related_feature: FEAT-0017
- version: v0.1.0

## 1. 测试范围
- 后端 BMS 状态解析编译与扁平化字段输出。
- UniApp 协议类型、参数注册与仪表盘组件类型校验。
- UniApp 仪表盘温度区动态渲染与保护状态卡片默认折叠行为。
- UniApp 蓝牙设备详情状态读取的两段拼装兼容逻辑。
- 协议主文档和看板回写完整性。

## 2. 已执行验证
- [x] `cd backend && go test ./internal/bms/... ./internal/bmsbridge/...`
- [ ] `cd frontend && pnpm typecheck`
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit`
- [ ] 手工验收：
  - [ ] 电芯温度数量为 `0/1/多路` 时，温度区 `T1/T2...` 序号与行数正确。
  - [ ] `BMS保护状态` 首次进入页面默认收起，点击后可正常展开/收起。
  - [ ] Web 端 BMS 面板保护状态展开/收起与开关文本展示。
  - [ ] 真机或 HBuilderX 查看保护状态卡片展开/收起交互。
  - [ ] 有保护项激活时顶部保护提示与卡片摘要数量一致。
  - [ ] 无保护项激活时卡片仍显示且列表状态为关闭。
  - [ ] 旧款 BMS 板蓝牙设备详情轮询避开 `0x135~0x139` 时不再失败。
  - [ ] 首段读取不访问旧板未实现的 `0x135`。

## 3. 当前结论
- `cd backend && go test ./internal/bms/... ./internal/bmsbridge/...`
  - 结果：通过。
  - 备注：编译过程中出现 `gopsutil/disk` 的 macOS 过时 API 警告，不影响测试通过。
- `cd frontend && pnpm typecheck`
  - 结果：通过。
- `cd fjbms-uniapp && pnpm exec tsc --noEmit`
  - 结果：通过。
- 协议层兼容性说明：
  - 已将 UniApp `readAllStatus()` 改为 `0x100~0x134` 与 `0x141~lastAddr` 两段读取，并对 `0x135~0x140` 回填默认值。
  - 当前尚未补独立自动化单测，需通过 TypeScript 校验与真机旧板回归共同覆盖。
- UI 视觉、旧板兼容性与交互验收待真机验证完成后补充。
