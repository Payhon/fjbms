# FEAT-0008 UniApp 蓝牙信号展示与手动断开连接优化 - 测试报告

- status: in_progress
- owner: payhon
- last_updated: 2026-03-04
- related_feature: FEAT-0008
- version: v0.1.0

## 1. 测试范围
- UniApp 蓝牙扫描页信号展示。
- 首页设备卡片断开蓝牙入口。
- 设备详情页断开蓝牙入口。

## 2. 已执行
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit`
  - 结果：通过
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit`（自动连接兼容性修复后复测）
  - 结果：通过
- [x] `cd fjbms-uniapp && pnpm exec tsc --noEmit`（MAC 归一化修复后复测）
  - 结果：通过
- [x] `cd backend && go test ./internal/service -run TestDoesNotExist`
  - 结果：通过（仅编译校验，含 macOS 工具链告警，不影响结果）
- [ ] 真机/模拟器手动验证（扫描页、首页、详情页）

## 3. 待执行
- [ ] 蓝牙连接设备：首页断开按钮点击后连接状态回落。
- [ ] 详情页蓝牙连接状态：断开按钮可见且可用。
- [ ] 非蓝牙状态：断开按钮隐藏。
- [ ] 扫描页信号强度显示为图标，无 dB 数字。

## 4. 缺陷与风险
- 目前未发现编译级缺陷。
- 仍需补充真机验证 BLE 断连体验（Android/iOS/微信小程序）。

## 5. 结论
- 代码改动已完成并通过 TypeScript 编译，当前处于真机验收阶段。
