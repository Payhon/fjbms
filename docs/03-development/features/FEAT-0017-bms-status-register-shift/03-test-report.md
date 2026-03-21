# FEAT-0017 BMS 状态寄存器地址调整与移动端保护状态卡片 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-03-20
- related_feature: FEAT-0017
- version: v0.1.0

## 1. 测试范围
- 后端 BMS 状态解析编译与扁平化字段输出。
- UniApp 协议类型、参数注册与仪表盘组件类型校验。
- 协议主文档和看板回写完整性。

## 2. 已执行验证
- [x] `cd backend && go test ./internal/bms/... ./internal/bmsbridge/...`
- [ ] `cd frontend && pnpm typecheck`
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit`
- [ ] 手工验收：
  - [ ] Web 端 BMS 面板保护状态展开/收起与开关文本展示。
  - [ ] 真机或 HBuilderX 查看保护状态卡片展开/收起交互。
  - [ ] 有保护项激活时顶部保护提示与卡片摘要数量一致。
  - [ ] 无保护项激活时卡片仍显示且列表状态为关闭。

## 3. 当前结论
- `cd backend && go test ./internal/bms/... ./internal/bmsbridge/...`
  - 结果：通过。
  - 备注：编译过程中出现 `gopsutil/disk` 的 macOS 过时 API 警告，不影响测试通过。
- `cd frontend && pnpm typecheck`
  - 结果：通过。
- `cd fjbms-uniapp && pnpm exec tsc --noEmit`
  - 结果：通过。
- UI 视觉与交互验收待真机验证完成后补充。
